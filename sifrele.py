from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import filedialog, messagebox
import base64
import hashlib
import os
import threading

BG        = "#0d0d0f"
PANEL     = "#16161a"
CARD      = "#1e1e24"
BORDER    = "#2a2a35"
ACCENT    = "#6c63ff"
ACCENT2   = "#ff6584"
SUCCESS   = "#43e97b"
ERROR     = "#ff4d6d"
TEXT      = "#e8e8f0"
SUBTEXT   = "#7a7a9a"
ENTRY_BG  = "#12121a"

FONT_HEAD = ("Segoe UI", 20, "bold")
FONT_SUB  = ("Segoe UI", 10)
FONT_BODY = ("Segoe UI", 10)
FONT_BTN  = ("Segoe UI", 10, "bold")
FONT_MONO = ("Consolas", 9)


def generate_key(password: str) -> bytes:
    digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt_file(file_path: str, password: str) -> tuple[bool, str]:
    try:
        key = generate_key(password)
        f = Fernet(key)
        with open(file_path, "rb") as fh:
            data = fh.read()
        encrypted = f.encrypt(data)
        new_path = file_path + ".locked"
        with open(new_path, "wb") as fh:
            fh.write(encrypted)
        os.remove(file_path)
        return True, os.path.basename(new_path)
    except Exception as e:
        return False, str(e)

def decrypt_file(file_path: str, password: str) -> tuple[bool, str]:
    try:
        key = generate_key(password)
        f = Fernet(key)
        with open(file_path, "rb") as fh:
            data = fh.read()
        decrypted = f.decrypt(data)
        new_path = file_path.replace(".locked", "")
        with open(new_path, "wb") as fh:
            fh.write(decrypted)
        os.remove(file_path)
        return True, os.path.basename(new_path)
    except Exception as e:
        return False, str(e)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AzzSec — Dosya Kilitleyici")
        self.geometry("560x680")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.selected_files: list[str] = []
        self._build()


    def _build(self):
   
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=30, pady=(26, 0))

        tk.Label(
            header, text="🔒", font=("Segoe UI Emoji", 28),
            bg=BG, fg=ACCENT
        ).pack(side="left", padx=(0, 10))

        title_box = tk.Frame(header, bg=BG)
        title_box.pack(side="left")
        tk.Label(title_box, text="Dosya Kilitleyici",
                 font=FONT_HEAD, bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(title_box, text="AzzSec Şifreleme Aracı",
                 font=FONT_SUB, bg=BG, fg=SUBTEXT).pack(anchor="w")


        self._sep()

     
        self._section("Parola")
        pw_frame = tk.Frame(self, bg=CARD, bd=0, highlightthickness=1,
                            highlightbackground=BORDER)
        pw_frame.pack(fill="x", padx=30, pady=(4, 0))

        left = tk.Frame(pw_frame, bg=CARD)
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text="Şifreleme Parolası", font=("Segoe UI", 9),
                 bg=CARD, fg=SUBTEXT).pack(anchor="w", padx=14, pady=(10, 2))
        self.pw_var = tk.StringVar()
        self.pw_entry = tk.Entry(
            left, textvariable=self.pw_var, show="●",
            font=FONT_MONO, bg=ENTRY_BG, fg=TEXT,
            insertbackground=ACCENT, relief="flat",
            bd=0, highlightthickness=0
        )
        self.pw_entry.pack(fill="x", padx=14, pady=(0, 10))

   
        self.show_pw = False
        self.eye_btn = tk.Label(pw_frame, text="👁", font=("Segoe UI Emoji", 14),
                                bg=CARD, fg=SUBTEXT, cursor="hand2")
        self.eye_btn.pack(side="right", padx=14)
        self.eye_btn.bind("<Button-1>", self._toggle_pw)

        self._section("Seçili Dosyalar")

        list_container = tk.Frame(self, bg=CARD, bd=0,
                                  highlightthickness=1,
                                  highlightbackground=BORDER)
        list_container.pack(fill="both", expand=True, padx=30, pady=(4, 0))


        scrollbar = tk.Scrollbar(list_container, bg=CARD, troughcolor=CARD,
                                 activebackground=ACCENT, relief="flat", width=8)
        scrollbar.pack(side="right", fill="y", pady=4)

        self.file_list = tk.Listbox(
            list_container,
            bg=CARD, fg=TEXT,
            selectbackground=ACCENT, selectforeground="#ffffff",
            font=FONT_MONO,
            relief="flat", bd=0, highlightthickness=0,
            activestyle="none",
            yscrollcommand=scrollbar.set
        )
        self.file_list.pack(fill="both", expand=True, padx=4, pady=4)
        scrollbar.config(command=self.file_list.yview)

        self.placeholder = tk.Label(
            list_container,
            text="Henüz dosya seçilmedi\n\nAşağıdaki butonları kullanarak dosya ekleyin",
            font=FONT_SUB, bg=CARD, fg=SUBTEXT, justify="center"
        )
        self.placeholder.place(relx=0.5, rely=0.5, anchor="center")

    
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=30, pady=(8, 0))

        self._small_btn(btn_row, "＋ Dosya Ekle", self._add_files, ACCENT).pack(side="left")
        self._small_btn(btn_row, "✕ Seçiliyi Kaldır",
                        self._remove_selected, SUBTEXT).pack(side="left", padx=(8, 0))
        self._small_btn(btn_row, "⊘ Tümünü Temizle",
                        self._clear_files, SUBTEXT).pack(side="right")

    
        self._section("İşlem Günlüğü")
        log_frame = tk.Frame(self, bg=ENTRY_BG, bd=0,
                             highlightthickness=1, highlightbackground=BORDER)
        log_frame.pack(fill="x", padx=30, pady=(4, 0))

        self.log_text = tk.Text(
            log_frame, height=5,
            bg=ENTRY_BG, fg=TEXT, font=FONT_MONO,
            relief="flat", bd=0, state="disabled",
            insertbackground=ACCENT, wrap="word"
        )
        self.log_text.pack(fill="x", padx=10, pady=8)
        self.log_text.tag_config("ok",  foreground=SUCCESS)
        self.log_text.tag_config("err", foreground=ERROR)
        self.log_text.tag_config("inf", foreground=SUBTEXT)

        self._sep(pady=14)
        action_frame = tk.Frame(self, bg=BG)
        action_frame.pack(fill="x", padx=30, pady=(0, 24))

        self._action_btn(
            action_frame, "🔐  Şifrele", self._run_encrypt,
            ACCENT, "#ffffff"
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        self._action_btn(
            action_frame, "🔓  Çöz", self._run_decrypt,
            "#2a2a35", TEXT
        ).pack(side="left", expand=True, fill="x")

    def _sep(self, pady=10):
        f = tk.Frame(self, height=1, bg=BORDER)
        f.pack(fill="x", padx=30, pady=pady)

    def _section(self, text):
        tk.Label(self, text="  ".join(text.upper()),
                 font=("Segoe UI", 8, "bold"),
                 bg=BG, fg=SUBTEXT).pack(anchor="w", padx=30, pady=(14, 0))

    def _small_btn(self, parent, text, cmd, color):
        b = tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"),
                     bg=BG, fg=color, cursor="hand2")
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>", lambda e: b.config(fg=TEXT))
        b.bind("<Leave>", lambda e: b.config(fg=color))
        return b

    def _action_btn(self, parent, text, cmd, bg_color, fg_color):
        btn = tk.Label(
            parent, text=text, font=FONT_BTN,
            bg=bg_color, fg=fg_color,
            pady=13, cursor="hand2",
            relief="flat"
        )
        btn.bind("<Button-1>", lambda e: cmd())
        btn.bind("<Enter>",    lambda e: btn.config(bg=ACCENT if bg_color==ACCENT else BORDER))
        btn.bind("<Leave>",    lambda e: btn.config(bg=bg_color))
        return btn

    def _toggle_pw(self, _=None):
        self.show_pw = not self.show_pw
        self.pw_entry.config(show="" if self.show_pw else "●")
        self.eye_btn.config(fg=ACCENT if self.show_pw else SUBTEXT)

    def _add_files(self):
        files = filedialog.askopenfilenames(title="Dosya(lar) Seçin")
        for f in files:
            if f not in self.selected_files:
                self.selected_files.append(f)
                self.file_list.insert(tk.END, f"  {os.path.basename(f)}")
        self._update_placeholder()

    def _remove_selected(self):
        sel = self.file_list.curselection()
        for idx in reversed(sel):
            self.file_list.delete(idx)
            self.selected_files.pop(idx)
        self._update_placeholder()

    def _clear_files(self):
        self.file_list.delete(0, tk.END)
        self.selected_files.clear()
        self._update_placeholder()

    def _update_placeholder(self):
        if self.selected_files:
            self.placeholder.place_forget()
        else:
            self.placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def _log(self, msg: str, tag: str = "inf"):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, msg + "\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state="disabled")

    def _validate(self) -> str | None:
        password = self.pw_var.get().strip()
        if not password:
            messagebox.showerror("Hata", "Parola alanı boş olamaz!")
            return None
        if not self.selected_files:
            messagebox.showerror("Hata", "En az bir dosya seçin!")
            return None
        return password

    def _run_encrypt(self):
        password = self._validate()
        if not password:
            return
        files = list(self.selected_files)
        self._clear_log()
        self._log(f"► {len(files)} dosya şifreleniyor…", "inf")

        def worker():
            ok = err = 0
            for path in files:
                success, result = encrypt_file(path, password)
                if success:
                    self.after(0, self._log, f"✓  {result}", "ok")
                    ok += 1
                else:
                    self.after(0, self._log, f"✗  {os.path.basename(path)} → {result}", "err")
                    err += 1
            self.after(0, self._log,
                       f"\n── Tamamlandı: {ok} başarılı, {err} hatalı ──", "inf")
            self.after(0, self._clear_files)

        threading.Thread(target=worker, daemon=True).start()

    def _run_decrypt(self):
        password = self._validate()
        if not password:
            return
        files = list(self.selected_files)
        self._clear_log()
        self._log(f"► {len(files)} dosya çözülüyor…", "inf")

        def worker():
            ok = err = 0
            for path in files:
                success, result = decrypt_file(path, password)
                if success:
                    self.after(0, self._log, f"✓  {result}", "ok")
                    ok += 1
                else:
                    self.after(0, self._log, f"✗  {os.path.basename(path)} → Parola yanlış veya dosya bozuk", "err")
                    err += 1
            self.after(0, self._log,
                       f"\n── Tamamlandı: {ok} başarılı, {err} hatalı ──", "inf")
            self.after(0, self._clear_files)

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    app = App()
    app.mainloop()