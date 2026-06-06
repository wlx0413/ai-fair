# Codex Cloud Handoff

This repository is prepared for Codex Cloud through GitHub.

## What to upload to GitHub

Commit the source project files:

- Flask app: `app.py`
- Recommendation services: `services/`
- Frontend: `templates/`, `static/`
- Data and trained model seed files: `data/`, `models/`
- macOS app launcher and PyInstaller config: `mac_app_launcher.py`, `AI_Music_Recommender.spec`
- Logo/build helper assets: `mac_app_assets/`, `tools/`
- Documentation: `README.md`, `docs/`, `TEMPLATE_LICENSE.md`, `mac_installer_dmg/README_CREATE_DMG.txt`

## What not to upload

The `.gitignore` intentionally excludes generated or local-only files:

- `mac_app_content*/`
- `mac_build*/`
- `pyinstaller_config/`
- `*.dmg`
- `*.app/`
- `mac_installer_dmg/staging*/`
- local backups and retired files
- `.env`, `users.json`, caches, and editor files

These files are either too large, machine-specific, or easy to rebuild.

## Local Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open the printed local URL.

## macOS App Build

```bash
python3 tools/generate_logo_assets.py
PYINSTALLER_CONFIG_DIR="$(pwd)/pyinstaller_config" python3 -m PyInstaller AI_Music_Recommender.spec --noconfirm --distpath mac_app_content_final --workpath mac_build_work_native_logo
```

The app is generated at:

```text
mac_app_content_final/AI Music Recommender.app
```

## DMG Build

The DMG staging folder is intentionally ignored by Git. Recreate it locally, then run:

```bash
hdiutil create -volname "AI Music Recommender" -srcfolder "mac_installer_dmg/staging_ai_music_recommender_v1" -format UDZO "mac_installer_dmg/AI-Music-Recommender-macOS-1.0.0.dmg"
```

## Codex Cloud Use

1. Push this repository to GitHub.
2. Open Codex Cloud.
3. Choose the GitHub repository.
4. Ask Codex Cloud to continue from `CODEX_CLOUD_HANDOFF.md`.

The installed macOS app is self-contained for normal use. Online music search still requires internet access on the user's Mac.
