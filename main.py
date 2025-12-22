#!/usr/bin/env python3
"""
simple_account_saver_with_mini_autofill.py
Minimal local account saver (Nickname, Username, Password)
+ Launch Riot Client
+ Mini copy panel with one-click auto-fill (username -> Tab -> password)
"""

import os
import sys
import sqlite3
import subprocess
import time
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont, filedialog

# --- pyautogui for keystrokes ---
try:
    import pyautogui as pag
    pag.FAILSAFE = True
    _HAS_PYAUTOGUI = True
except Exception:
    _HAS_PYAUTOGUI = False

# --- pygetwindow for focusing Riot window (optional) ---
try:
    import pygetwindow as gw
    _HAS_PYGETWINDOW = True
except Exception:
    _HAS_PYGETWINDOW = False

DB = "simple_accounts.db"
RIOT_PATH = r"C:\Riot Games\Riot Client\RiotClientServices.exe"  # <-- set your path

# Choose paste key per OS
IS_MAC = sys.platform == "darwin"
PASTE_MOD = "command" if IS_MAC else "ctrl"
APP_NAME = "ValorantAccountSwitcher"


def get_default_db_path():
    # Prefer ProgramData to avoid permission issues in Program Files
    program_data = os.environ.get("PROGRAMDATA") or os.environ.get("ProgramData")
    if not program_data:
        program_data = os.path.expanduser("~")
    data_dir = os.path.join(program_data, APP_NAME)
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "simple_accounts.db")


DB_PATH = get_default_db_path()

# ---------------- Data layer ----------------
class SimpleDB:
    def __init__(self, path=DB_PATH):
        self.conn = sqlite3.connect(path)
        self._ensure_table()

    def _ensure_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add(self, nickname, username, password):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO accounts (nickname, username, password) VALUES (?, ?, ?)",
                    (nickname, username, password))
        self.conn.commit()

    def update(self, rowid, nickname, username, password):
        self.conn.execute("UPDATE accounts SET nickname=?, username=?, password=? WHERE id=?",
                          (nickname, username, password, rowid))
        self.conn.commit()

    def delete(self, rowid):
        self.conn.execute("DELETE FROM accounts WHERE id=?", (rowid,))
        self.conn.commit()

    def all(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, nickname, username, password FROM accounts ORDER BY nickname COLLATE NOCASE")
        return cur.fetchall()

# ---------------- UI ----------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # Keep the standard Windows title bar instead of a custom header
        self.overrideredirect(False)
        self.title("Simple Account Saver + Riot Launcher")
        self.geometry("780x500")
        self.icon_image = None
        self._set_icon(self)
        self._setup_style()
        self.db = SimpleDB()
        self.current_id = None
        self.rows = []

        self._build_ui()
        self._refresh_list()

    def _set_icon(self, window):
        try:
            window.iconbitmap("icon.ico")
        except Exception:
            pass
        try:
            self.icon_image = tk.PhotoImage(file="icon.ico")
            window.iconphoto(True, self.icon_image)
        except Exception:
            self.icon_image = None

    def _setup_style(self):
        # Red-accent dark palette
        self.colors = {
            "bg": "#1a0d0f",
            "panel": "#210f13",
            "accent": "#ff2d44",
            "text": "#f5e9ea",
            "muted": "#c48c94"
        }
        self.configure(bg=self.colors["bg"])
        base_font = tkfont.Font(family="JetBrainsMono Nerd Font", size=10, weight="normal")
        header_font = tkfont.Font(family="JetBrainsMono Nerd Font", size=12, weight="bold")
        self.option_add("*Font", base_font)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=self.colors["panel"])
        style.configure("Main.TFrame", background=self.colors["panel"])
        style.configure("Side.TFrame", background=self.colors["panel"])
        style.configure("TLabel", background=self.colors["panel"], foreground=self.colors["text"], font=base_font)
        style.configure("Header.TLabel", background=self.colors["panel"], foreground=self.colors["text"],
                        font=header_font)
        style.configure("Muted.TLabel", background=self.colors["panel"], foreground=self.colors["muted"], font=base_font)
        style.configure("TButton", background=self.colors["panel"], foreground=self.colors["text"], padding=6)
        style.map("TButton",
                  background=[("active", self.colors["accent"])],
                  foreground=[("active", "white")])
        style.configure("Accent.TButton", background=self.colors["accent"], foreground="white", padding=8)
        style.map("Accent.TButton",
                  background=[("active", "#ff6977")],
                  foreground=[("active", "white")])
        style.configure("TCheckbutton", background=self.colors["panel"], foreground=self.colors["text"])
        style.configure("TEntry", fieldbackground=self.colors["bg"], foreground=self.colors["text"],
                        bordercolor=self.colors["bg"])
        style.configure("ReadOnly.TEntry", fieldbackground=self.colors["bg"], foreground=self.colors["text"],
                        bordercolor=self.colors["bg"])
        style.map("ReadOnly.TEntry",
                  fieldbackground=[("readonly", self.colors["bg"])],
                  foreground=[("readonly", self.colors["text"])],
                  bordercolor=[("readonly", self.colors["bg"])])

    def _build_ui(self):
        main = ttk.Frame(self, style="Main.TFrame")
        main.pack(fill="both", expand=True, padx=16, pady=16)
        main.columnconfigure(0, weight=1, minsize=260)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        # Left pane: list with scrollbar
        left = ttk.Frame(main, style="Side.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14), pady=6)
        ttk.Label(left, text="Accounts", style="Header.TLabel").pack(anchor="w", pady=(0, 10))
        list_wrap = ttk.Frame(left, style="Side.TFrame")
        list_wrap.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_wrap, orient="vertical")
        self.listbox = tk.Listbox(
            list_wrap, width=28, bg=self.colors["bg"], fg=self.colors["text"],
            selectbackground=self.colors["accent"], selectforeground="white",
            relief="flat", highlightthickness=0, borderwidth=0,
            font=("JetBrainsMono Nerd Font", 10), yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        # Right pane: form + actions
        right = ttk.Frame(main, style="Side.TFrame")
        right.grid(row=0, column=1, sticky="nsew", pady=6)
        right.columnconfigure(1, weight=1)
        right.columnconfigure(2, weight=1)

        ttk.Label(right, text="Account Details", style="Header.TLabel")\
            .grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        ttk.Label(right, text="Nickname:").grid(row=1, column=0, sticky="w", padx=4, pady=6)
        self.nickname_var = tk.StringVar()
        ttk.Entry(right, textvariable=self.nickname_var, width=40).grid(row=1, column=1, columnspan=2, sticky="ew")

        ttk.Label(right, text="Username:").grid(row=2, column=0, sticky="w", padx=4, pady=6)
        self.username_var = tk.StringVar()
        ttk.Entry(right, textvariable=self.username_var, width=40).grid(row=2, column=1, columnspan=2, sticky="ew")

        ttk.Label(right, text="Password:").grid(row=3, column=0, sticky="w", padx=4, pady=6)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(right, textvariable=self.password_var, width=40, show="*")
        self.password_entry.grid(row=3, column=1, columnspan=2, sticky="ew")

        self.show_pw = tk.BooleanVar(value=False)
        ttk.Checkbutton(right, text="Show password", variable=self.show_pw,
                        command=self._toggle_pw).grid(row=4, column=1, sticky="w", pady=(0, 8))

        btns = ttk.Frame(right)
        btns.grid(row=5, column=0, columnspan=3, pady=16, sticky="w")
        buttons = [
            ("Add", self.add_account, "Accent.TButton"),
            ("Update", self.update_account, "TButton"),
            ("Delete", self.delete_account, "TButton"),
            ("Import DB", self.import_db, "TButton"),
            ("Export DB", self.export_db, "TButton"),
            ("Launch Riot Client", self.launch_riot, "Accent.TButton"),
        ]
        self.launch_btn = None
        for idx, (label, cmd, style) in enumerate(buttons):
            row_idx = idx // 3
            col_idx = idx % 3
            btn = ttk.Button(btns, text=label, command=cmd, style=style)
            btn.grid(row=row_idx, column=col_idx, padx=6, pady=4, sticky="ew")
            if label == "Launch Riot Client":
                self.launch_btn = btn
        for c in range(3):
            btns.columnconfigure(c, weight=1)
        if self.launch_btn:
            self.launch_btn.state(["disabled"])

        self.status = ttk.Label(right, text="Select an account to enable launcher.", style="Muted.TLabel")
        self.status.grid(row=6, column=0, columnspan=3, pady=10, sticky="w")

    def _toggle_pw(self):
        self.password_entry.config(show="" if self.show_pw.get() else "*")

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        self.rows = self.db.all()
        for row in self.rows:
            self.listbox.insert(tk.END, row[1])  # nickname

    def on_select(self, _evt=None):
        sel = self.listbox.curselection()
        if not sel:
            self.launch_btn.state(["disabled"])
            self.current_id = None
            return
        idx = sel[0]
        rid, nick, user, pw = self.rows[idx]
        self.current_id = rid
        self.nickname_var.set(nick)
        self.username_var.set(user)
        self.password_var.set(pw)
        self.launch_btn.state(["!disabled"])

    # ---------- CRUD ----------
    def add_account(self):
        nick = self.nickname_var.get().strip()
        user = self.username_var.get().strip()
        pw = self.password_var.get().strip()
        if (not nick) or (not user) or (not pw):
            messagebox.showwarning("Missing fields", "All fields are required.")
            return
        try:
            self.db.add(nick, user, pw)
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate", "Nickname already exists.")
            return
        self.clear_form()
        self._refresh_list()



    def update_account(self):
        if not self.current_id:
            messagebox.showinfo("Select", "Select an account first.")
            return
        nick = self.nickname_var.get().strip()
        user = self.username_var.get().strip()
        pw = self.password_var.get().strip()
        if not nick or not user or not pw:
            messagebox.showwarning("Missing fields", "All fields are required.")
            return
        try:
            self.db.update(self.current_id, nick, user, pw)
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate", "Nickname already exists.")
            return
        self._refresh_list()

    def delete_account(self):
        if not self.current_id:
            messagebox.showinfo("Select", "Select an account to delete.")
            return
        if messagebox.askyesno("Confirm", "Delete this account?"):
            self.db.delete(self.current_id)
            self.clear_form()
            self._refresh_list()
            self.launch_btn.state(["disabled"])

    def clear_form(self):
        self.nickname_var.set("")
        self.username_var.set("")
        self.password_var.set("")
        self.show_pw.set(False)
        self._toggle_pw()
        self.listbox.selection_clear(0, tk.END)
        self.current_id = None

    def import_db(self):
        file_path = filedialog.askopenfilename(
            title="Select database file",
            filetypes=[("SQLite DB", "*.db"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            choice = messagebox.askyesnocancel(
                "Import database",
                "Append data from selected DB?\nYes = append (skip duplicate nicknames)\nNo = override current DB\nCancel = abort"
            )
            if choice is None:
                return

            if choice:  # append
                # open source db
                src_db = sqlite3.connect(file_path)
                rows = src_db.execute("SELECT nickname, username, password FROM accounts").fetchall()
                src_db.close()
                added = 0
                skipped = 0
                for nick, user, pw in rows:
                    try:
                        self.db.add(nick, user, pw)
                        added += 1
                    except sqlite3.IntegrityError:
                        skipped += 1
                self._refresh_list()
                messagebox.showinfo("Import complete",
                                    f"Appended {added} entr{'y' if added==1 else 'ies'}; "
                                    f"skipped {skipped} duplicate nickname(s).")
            else:  # override
                try:
                    self.db.conn.close()
                except Exception:
                    pass
                shutil.copy(file_path, DB_PATH)
                self.db = SimpleDB()
                self.clear_form()
                self._refresh_list()
                messagebox.showinfo("Import complete", f"Database overridden from:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Import failed", f"Could not import DB:\n{e}")

    def export_db(self):
        dest_path = filedialog.asksaveasfilename(
            title="Export database",
            defaultextension=".db",
            filetypes=[("SQLite DB", "*.db"), ("All files", "*.*")],
            initialfile="simple_accounts.db"
        )
        if not dest_path:
            return
        try:
            shutil.copy(DB_PATH, dest_path)
            messagebox.showinfo("Export complete", f"Database saved to:\n{dest_path}")
        except Exception as e:
            messagebox.showerror("Export failed", f"Could not export DB:\n{e}")

    # ---------- Launch & Mini Panel ----------
    def launch_riot(self):
        if not self.current_id:
            messagebox.showinfo("Select", "Select an account first.")
            return

        # Launch Riot (optional)
        if not os.path.exists(RIOT_PATH):
            messagebox.showerror("Error", f"Riot Client not found at:\n{RIOT_PATH}")
            return
        try:
            subprocess.Popen([RIOT_PATH])
        except Exception as e:
            messagebox.showerror("Launch failed", f"Could not launch Riot Client:\n{e}")
            return

        # Hide main window and show mini panel
        self.withdraw()
        self._show_copy_panel(
            self.nickname_var.get(),
            self.username_var.get(),
            self.password_var.get()
        )

    # ---- Mini panel with Autofill button ----
    def _show_copy_panel(self, nick, user, pw):
        top = tk.Toplevel(self)
        # Keep default window decorations (title bar, close button)
        top.overrideredirect(False)
        top.title("Copy & Paste Helper")
        self._set_icon(top)
        top.attributes("-topmost", True)
        top.resizable(False, False)
        top.geometry("360x220+200+200")
        top.configure(bg=self.colors["panel"])

        container = ttk.Frame(top, style="Main.TFrame")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        def on_close():
            self.destroy()
        top.protocol("WM_DELETE_WINDOW", on_close)

        # toast label
        toast_lbl = ttk.Label(container, text="", foreground="green", background=self.colors["panel"])
        toast_lbl.pack_forget()
        def toast(msg):
            toast_lbl.config(text=msg)
            toast_lbl.pack(pady=(0, 4))
            top.after(1400, lambda: toast_lbl.config(text=""))

        # reusable row builder (copy on click)
        
        def make_row(parent, label_text, value, mask=False):
            row = ttk.Frame(parent, style="Side.TFrame")
            row.pack(fill="x", padx=8, pady=4)

            ttk.Label(row, text=label_text, width=10).pack(side="left")

            # Store REAL value (for copy/autofill)
            real_var = tk.StringVar(value=value)

            # Show masked password instead of the real text in the mini panel
            display_text = ("*" * max(4, len(value))) if mask else value
            display_var = tk.StringVar(value=display_text)

            ent = tk.Entry(
                row, textvariable=display_var, width=32, state="readonly",
                readonlybackground=self.colors["panel"],
                fg=self.colors["text"], disabledforeground=self.colors["text"],
                relief="flat", highlightthickness=0, borderwidth=0, cursor="arrow",
                insertontime=0, insertofftime=0
            )
            ent.pack(side="left", fill="x", expand=True)

            def copy_value(_evt=None):
                try:
                    self.clipboard_clear()
                    self.clipboard_append(real_var.get())  # copy REAL value
                    self.update()
                    toast("Copied!")
                except Exception:
                    pass

            ent.bind("<Button-1>", copy_value)
            ttk.Button(row, text="Copy", command=copy_value).pack(side="left", padx=4)

            return real_var
        user_var = make_row(container, "Username", user)
        pw_var   = make_row(container, "Password", pw, mask=True)

        # Autofill button: focus Riot -> paste username -> Tab -> paste password
        def autofocus_and_autofill():
            if not _HAS_PYAUTOGUI:
                messagebox.showerror("pyautogui missing", "Install pyautogui:\n\npip install pyautogui")
                return

            # Try bringing Riot window to front
            focused = False
            if _HAS_PYGETWINDOW:
                try:
                    candidates = gw.getWindowsWithTitle("Riot")
                    if not candidates:
                        candidates = gw.getWindowsWithTitle("Riot Client")
                    if candidates:
                        w = candidates[0]
                        w.activate()
                        focused = True
                except Exception:
                    focused = False

            if not focused:
                # Fallback: briefly drop topmost and ask user to click Riot
                toast("Click the Riot window")
                try:
                    top.attributes("-topmost", False)
                except Exception:
                    pass
                # give 2 seconds to the user to click Riot field
                top.after(2000, do_autofill)
            else:
                # short delay to ensure focus
                top.after(400, do_autofill)

        def do_autofill():
            try:
                # Restore topmost afterwards
                def restore_top():
                    try:
                        top.attributes("-topmost", True)
                    except Exception:
                        pass

                # Paste USERNAME
                self.clipboard_clear()
                self.clipboard_append(self.children_clip_sanitize(user_var.get()))
                self.update()
                pag.hotkey(PASTE_MOD, 'v')
                time.sleep(0.1)

                # TAB to password field
                pag.press('tab')
                time.sleep(0.05)

                # Paste PASSWORD
                self.clipboard_clear()
                self.clipboard_append(self.children_clip_sanitize(pw_var.get()))
                self.update()
                pag.hotkey(PASTE_MOD, 'v')

                # Enter to submit login
                time.sleep(0.3)
                pag.press('enter')

                toast("Filled!")
                time.sleep(0.5)
                self.destroy()

                # top.after(10, restore_top)
            except Exception as e:
                messagebox.showerror("Autofill failed", f"{e}")

        # helper to avoid weird clipboard characters
        def sanitize_text(s: str) -> str:
            # You can customize if needed; keeping minimal
            return s.replace("\r\n", "\n").replace("\r", "\n")

        # store on self so inner function can call
        self.children_clip_sanitize = sanitize_text

        btn_row = ttk.Frame(container, style="Side.TFrame")
        btn_row.pack(fill="x", padx=8, pady=(10, 6))
        ttk.Button(btn_row, text="Auto-fill Username + Password", command=autofocus_and_autofill)\
            .pack(side="left")

        ttk.Label(container, text="Tip: If it can't focus Riot automatically, it will give you 2s to click it.",
                  style="Muted.TLabel").pack(pady=(6, 0))

if __name__ == "__main__":
    app = App()
    app.mainloop()
