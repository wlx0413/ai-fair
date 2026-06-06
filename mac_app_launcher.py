from __future__ import annotations

import os
import shutil
import sys
import threading
import time
import traceback
from pathlib import Path


APP_NAME = "AI Music Recommendation System"


def bundle_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def runtime_root() -> Path:
    return Path.home() / "Library" / "Application Support" / APP_NAME


def launcher_log_path() -> Path:
    return runtime_root() / "launcher.log"


def write_log(message: str) -> None:
    try:
        runtime_root().mkdir(parents=True, exist_ok=True)
        with launcher_log_path().open("a", encoding="utf-8") as log_file:
            log_file.write(message.rstrip() + "\n")
    except Exception:
        pass


def copy_seed_folder(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        return
    for item in source.iterdir():
        target = destination / item.name
        if target.exists():
            continue
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def prepare_runtime_data() -> None:
    root = runtime_root()
    root.mkdir(parents=True, exist_ok=True)
    copy_seed_folder(bundle_root() / "data", root / "data")
    copy_seed_folder(bundle_root() / "models", root / "models")
    os.environ["AI_MUSIC_DATA_DIR"] = str(root / "data")
    os.environ["AI_MUSIC_MODELS_DIR"] = str(root / "models")


def run_flask_server(app, port: int) -> None:
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def open_native_window(url: str) -> None:
    import webview

    webview.create_window(
        "AI Music Recommendation System",
        url,
        width=1280,
        height=850,
        min_size=(980, 680),
        text_select=True,
    )
    webview.start(gui="cocoa", debug=False)


def main() -> None:
    try:
        prepare_runtime_data()

        from app import app, choose_port
        from services.data_store import ensure_data_files

        ensure_data_files()
        port = choose_port()
        url = f"http://127.0.0.1:{port}"
        write_log(f"Starting AI Music Recommender at {url}")
        threading.Thread(target=run_flask_server, args=(app, port), daemon=True).start()
        time.sleep(1.0)
        open_native_window(url)
    except Exception:
        write_log(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
