# New Chat Checklist

Use this checklist when starting a fresh AI-agent session on this repository.

## First Pass

Run or inspect:

```powershell
rg --files
Get-Content README.md
Get-Content main.py -TotalCount 220
Get-Content ValorantAccountSaver.spec
Get-Content installer\installer_script.iss
Get-Content .github\workflows\release.yml
git -c safe.directory="C:/Users/Pc/Documents/valorant account switcher" status --short --branch
```

Confirm:

- The active app is `main.py`.
- `account_saver_big_borderless.py` and `test.py` are ignored legacy/scratch files.
- Runtime data is written under `%PROGRAMDATA%\ValorantAccountSwitcher`.
- Packaging still expects `dist\ValorantAccountSaver.exe`.

## Request Classification

Before editing, identify the request type:

- Docs-only: update markdown and do not change code.
- App behavior: edit `main.py` and manually verify the affected Tkinter flow.
- Packaging/release: check `ValorantAccountSaver.spec`, `installer/installer_script.iss`, and `.github/workflows/release.yml` together.
- Dependency cleanup: inspect imports in `main.py` before changing `requirements.txt`.

## Manual App Test Flow

For behavior changes, test the relevant flow on Windows:

- Start the app with `python main.py`.
- Add an account with nickname, username, and password.
- Select an account and confirm fields populate.
- Update an account and confirm duplicate nickname handling still works.
- Delete an account and confirm the list and button states update.
- Search by nickname.
- Export the DB.
- Import a DB with append and confirm duplicate nicknames are skipped.
- Import a DB with override and confirm the current DB is replaced.
- Set or locate `RiotClientServices.exe`.
- Launch Riot Client and confirm the mini copy/autofill panel appears.
- Click username/password rows and Copy buttons to confirm clipboard behavior.
- Test autofill when Riot can be focused automatically.
- Test autofill fallback when the user must click Riot manually.

## Packaging Check Flow

For build or release changes:

```powershell
pyinstaller ValorantAccountSaver.spec
```

Confirm:

- `dist\ValorantAccountSaver.exe` exists.
- `dist\icon.ico` exists or the installer still receives the icon file it expects.
- Launching the built executable opens the Tkinter app.

Then, with Inno Setup available:

```powershell
iscc installer\installer_script.iss
```

Confirm:

- `installer\ValorantAccountSwitcherInstaller.exe` is produced, or update the workflow if Inno outputs elsewhere.
- `.github/workflows/release.yml` still collects and uploads the expected installer name.

## Documentation Check

When docs change:

- Confirm Markdown paths and commands are accurate for this repo.
- Keep `ISSUES.md` limited to documented risks unless the task asks for fixes.
- Keep `AGENTS.md` focused on instructions future agents need before touching files.
