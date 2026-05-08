# Agent Guide

This repo contains a Windows Tkinter app for storing local Valorant/Riot account credentials, launching Riot Client, and helping paste saved credentials into the login window.

## Active Code

- `main.py` is the production entrypoint.
- `account_saver_big_borderless.py` is an older borderless UI experiment and is ignored by Git. Do not treat it as production code unless the user explicitly asks to revive it.
- `test.py` is an ignored scratch icon test. Do not use it as an app test suite.

## Runtime Behavior

- Account data is stored in SQLite at `%PROGRAMDATA%\ValorantAccountSwitcher\simple_accounts.db`.
- The selected Riot Client executable path is stored at `%PROGRAMDATA%\ValorantAccountSwitcher\riot_path.txt`.
- The last selected account id is stored at `%PROGRAMDATA%\ValorantAccountSwitcher\last_account.txt`.
- The app supports account add, update, delete, nickname search, DB import, and DB export.
- `launch_riot()` starts Riot Client with Valorant launch arguments, hides the main window, and opens a topmost mini copy/autofill panel.
- `pyautogui` drives clipboard paste, Tab, and Enter for autofill.
- `pygetwindow` is optional and is used to focus a Riot window. Without it, the app asks the user to click Riot manually before autofill.

## Commands

Run locally:

```powershell
python main.py
```

Build the Windows executable:

```powershell
pyinstaller ValorantAccountSaver.spec
```

Build the installer with Inno Setup after the executable exists:

```powershell
iscc installer\installer_script.iss
```

Release builds are handled by `.github/workflows/release.yml` on `v*` tags or manual workflow dispatch.

## Packaging

- `ValorantAccountSaver.spec` builds from `main.py` and includes `icon.ico`.
- The expected executable name is `ValorantAccountSaver.exe`.
- `installer/installer_script.iss` wraps `dist\ValorantAccountSaver.exe` and `dist\icon.ico` into `ValorantAccountSwitcherInstaller.exe`.
- The installer script supports a `MyAppVersion` define supplied by the GitHub Actions workflow.

## Guardrails

- Do not commit local SQLite databases or account data.
- Do not commit `.venv`, `build`, generated `.exe` files, or generated installer binaries.
- Do not edit ignored legacy/scratch files unless the task specifically targets them.
- Treat credential handling changes as sensitive. The app currently stores plaintext passwords and uses the clipboard for copy/autofill.
- When changing packaging, verify the PyInstaller spec, Inno Setup script, and GitHub workflow agree on executable names and output paths.
- In the Codex sandbox, Git may require:

```powershell
git -c safe.directory="C:/Users/Pc/Documents/valorant account switcher" status --short
```

## Style Notes

- Keep the app Windows-first unless the user asks for cross-platform support.
- Prefer small, direct Tkinter changes that match the existing `ttk.Style` usage in `main.py`.
- Keep runtime data under `%PROGRAMDATA%\ValorantAccountSwitcher` unless changing persistence is the main task.
- Avoid broad dependency changes unless the task is specifically dependency cleanup.
