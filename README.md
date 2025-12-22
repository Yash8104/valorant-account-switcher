# Valorant Account Switcher

Lightweight Tkinter app to save multiple Valorant/Riot logins locally, copy or auto-fill them into Riot Client, and launch the client. Data lives in a local SQLite DB under ProgramData so it persists across updates.

## Features
- Save, update, delete accounts (nickname/username/password) stored in SQLite at `%PROGRAMDATA%\ValorantAccountSwitcher\simple_accounts.db`.
- Mini “Copy & Paste Helper” panel with masked password, copy buttons, and one-click auto-fill (username → Tab → password → Enter) via `pyautogui`.
- Optional Riot Client launch path (`RIOT_PATH` in `main.py`).
- Import DB with Append (skips duplicate nicknames) or Override; Export DB to any location.
- Custom dark red theme, JetBrainsMono Nerd Font support, and app icon (`icon.ico`).

## Requirements
- Python 3.10+ on Windows.
- `pip install -r requirements.txt` (includes `pyautogui`, `pygetwindow`, `pillow`, etc.).
- For full auto-focus of Riot Client, keep `pygetwindow` installed; without it the app will prompt you to manually click Riot before autofill.

## Running
```bash
python main.py
```
Data is saved to `%PROGRAMDATA%\ValorantAccountSwitcher\simple_accounts.db` automatically (directory is created if missing).

## Building an EXE (PyInstaller)
From the project root (where `main.py` and `icon.ico` live):
```bash
pyinstaller --noconfirm --onefile --windowed --icon icon.ico --add-data "icon.ico;." main.py
```
- Output: `dist\main.exe`
- Keep `icon.ico` next to the exe (the command above embeds it and also copies it alongside).
- If you prefer a bundled folder (faster startup), drop `--onefile`.

## Installer idea
For easy sharing, wrap `dist\main.exe` with Inno Setup or NSIS to:
- Install into `%ProgramFiles%\ValorantAccountSwitcher\`
- Place shortcuts in Start Menu/Desktop
- Optionally launch after install
Signing the exe/installer reduces SmartScreen prompts.

## Import/Export notes
- Import → choose file → dialog asks Append vs Override. Append skips duplicate nicknames; Override replaces the current DB.
- Export saves the current DB anywhere you pick (suggest keeping backups).

## Customization
- Change Riot path via `RIOT_PATH` in `main.py`.
- Fonts/theme colors live in `_setup_style` in `main.py`.
- Mini panel window uses the same icon and theme; defaults to topmost during autofill.

## Known limitations
- Title bar color stays system-default (Tk can’t recolor native chrome without a custom title bar).
- Auto-focus depends on Riot window title and `pygetwindow`; otherwise manual click is required.
