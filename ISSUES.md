# Known Issues

This file records issues found during repo review. These are documented only; no code fixes are included here.

## Security

- Passwords are stored in plaintext SQLite at `%PROGRAMDATA%\ValorantAccountSwitcher\simple_accounts.db`.
- Passwords are copied through the system clipboard for manual copy and autofill.
- Autofill uses simulated keystrokes, so it can paste into the wrong window if focus changes at the wrong time.

Suggested future direction: consider Windows Credential Manager, DPAPI, or another local encryption approach before distributing to users who expect stronger credential protection.

## Dependencies

- `requirements.txt` is much larger than the app appears to need.
- The active app imports a small Tkinter/SQLite/automation stack, but the requirements file includes heavy and unrelated packages such as OCR, data science, notebooks, Selenium, Torch, and media libraries.
- This can slow CI, increase installer/build instability, and make dependency conflicts more likely.

Suggested future direction: derive a minimal runtime requirements file from `main.py` and keep development-only tools separate.

## README Encoding

- `README.md` contains mojibake around smart quotes and arrows, for example the copy/paste helper description and import/export notes.
- This makes the README look corrupted in plain text and can confuse future agents or users.

Suggested future direction: replace the corrupted characters with plain ASCII quotes and arrows.

## Icon Path Fragility

- `main.py` loads `icon.ico` using a relative path.
- Depending on the current working directory or PyInstaller runtime behavior, icon loading may fail even when the icon is bundled.

Suggested future direction: resolve bundled assets through a helper that handles normal source runs and PyInstaller `_MEIPASS`.

## Git Safe Directory In Sandbox

- In Codex, `git status` may fail because the repo is owned by `YASH-PC/Pc` while the sandbox user is `YASH-PC/CodexSandboxOffline`.
- Use a one-off safe-directory override for inspection commands:

```powershell
git -c safe.directory="C:/Users/Pc/Documents/valorant account switcher" status --short --branch
```

Suggested future direction: no repo code change is needed. This is an environment note for AI-agent sessions.
