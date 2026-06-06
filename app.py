from __future__ import annotations

import socket
import math
import sys
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

from services.data_store import (
    MODEL_PATH,
    add_feedback,
    add_interaction,
    add_playlist,
    ensure_data_files,
    match_local_song,
    normalize_song_row,
    upsert_songs,
)
from services.music_search import build_estimated_song_row, search_music
from services.qq_music_importer import FRIENDLY_ERROR, import_qq_playlist
from services.recommender import HybridMusicRecommender
from services.training_service import RecommendationTrainer


BASE_DIR = Path(__file__).resolve().parent


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return BASE_DIR / relative_path


app = Flask(
    __name__,
    template_folder=str(resource_path("templates")),
    static_folder=str(resource_path("static")),
)


def trainer() -> RecommendationTrainer:
    return RecommendationTrainer(model_path=MODEL_PATH)


def recommender() -> HybridMusicRecommender:
    return HybridMusicRecommender(model_path=MODEL_PATH)


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, float):
        return None if math.isnan(value) or math.isinf(value) else value
    try:
        import numpy as np

        if isinstance(value, np.integer):
            return int(value)
        if isinstance(value, np.floating):
            number = float(value)
            return None if math.isnan(number) or math.isinf(number) else number
    except Exception:
        pass
    if str(value) == "nan":
        return ""
    return value


def safe_jsonify(payload: Any):
    return jsonify(json_safe(payload))


@app.route("/")
def index():
    ensure_data_files()
    return render_template("index.html")


@app.get("/api/health")
def health():
    ensure_data_files()
    return safe_jsonify({"status": "ok", "message": "AI Music Recommendation System is running."})


@app.get("/api/search")
def api_search():
    query = request.args.get("q", "")
    results = search_music(query, limit=12)
    return safe_jsonify({"query": query, "results": results})


@app.post("/api/import/qq")
def api_import_qq():
    payload = request.get_json(silent=True) or {}
    playlist_url = payload.get("playlist_url", "")
    result = import_qq_playlist(playlist_url)
    if not result.get("success"):
        return safe_jsonify(
            {
                "success": False,
                "message": FRIENDLY_ERROR,
                "songs": [],
                "playlist_id": result.get("playlist_id", ""),
                "tried_endpoints": result.get("tried_endpoints", []),
                "failure_reason": result.get("failure_reason", ""),
            }
        ), 200
    return safe_jsonify(result)


@app.post("/api/playlist/manual")
def api_manual_playlist():
    payload = request.get_json(silent=True) or {}
    raw_songs = payload.get("songs", [])
    user_id = payload.get("user_id", "demo_user")
    normalized = []
    for item in raw_songs:
        if isinstance(item, str):
            track_name, artist_name = parse_song_line(item)
        else:
            track_name = item.get("track_name", "")
            artist_name = item.get("artist_name", "")
        if not track_name:
            continue
        matched = match_local_song(track_name, artist_name)
        if matched:
            matched["source"] = "manual"
            normalized.append(matched)
        else:
            normalized.append(
                build_estimated_song_row(
                    {
                        "track_name": track_name,
                        "artist_name": artist_name or "Unknown Artist",
                        "source": "manual",
                    },
                    source="manual",
                )
            )
    saved = upsert_songs(normalized)
    add_playlist("Manual Playlist", "manual", len(saved))
    interactions = []
    for song in saved:
        if song.get("has_audio_features"):
            interactions.append(add_interaction(user_id, str(song["track_id"]), "manual_add"))
    return safe_jsonify({"success": True, "saved_songs": saved, "interactions_created": len(interactions)})


@app.post("/api/training/add")
def api_add_training_song():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id", "demo_user")
    song = normalize_song_row(payload.get("song", payload))
    saved = upsert_songs([song])[0]
    if saved.get("has_audio_features"):
        add_interaction(user_id, str(saved["track_id"]), "manual_add")
        message = "Song added to training data."
    else:
        message = "Song saved as metadata, but it does not have enough audio features for model training."
    return safe_jsonify({"success": True, "message": message, "song": saved})


@app.post("/api/train")
def api_train():
    status = trainer().train_lightfm_model()
    return safe_jsonify(status)


@app.get("/api/model-status")
def api_model_status():
    return safe_jsonify(trainer().get_training_status())


@app.get("/api/recommendations")
def api_recommendations():
    user_id = request.args.get("user_id", "demo_user")
    top_n = int(request.args.get("top_n", 10))
    results = recommender().recommend_for_user(user_id=user_id, top_n=top_n)
    return safe_jsonify({"user_id": user_id, "recommendations": results, "taste_profile": recommender().get_user_taste_profile(user_id)})


@app.get("/api/daily-recommendations")
def api_daily_recommendations():
    user_id = request.args.get("user_id", "demo_user")
    top_n = int(request.args.get("top_n", 50))
    top_n = max(1, min(top_n, 50))
    results = recommender().daily_recommendations(user_id=user_id, top_n=top_n)
    return safe_jsonify(
        {
            "user_id": user_id,
            "recommendations": results,
            "count": len(results),
            "requested_count": top_n,
            "message": f"Generated {len(results)} final daily recommendations.",
            "taste_profile": recommender().get_user_taste_profile(user_id),
        }
    )


@app.post("/api/feedback")
def api_feedback():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id", "demo_user")
    track_id = payload.get("track_id", "")
    label = int(payload.get("label", 1))
    if not track_id:
        return safe_jsonify({"success": False, "message": "track_id is required"}), 400
    feedback = add_feedback(user_id, track_id, label)
    status = trainer().train_lightfm_model()
    return safe_jsonify({"success": True, "feedback": feedback, "model_status": status})


@app.get("/api/taste-profile")
def api_taste_profile():
    user_id = request.args.get("user_id", "demo_user")
    return safe_jsonify(recommender().get_user_taste_profile(user_id))


def parse_song_line(line: str) -> tuple[str, str]:
    parts = [part.strip() for part in str(line).split("-", 1)]
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], ""


def port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def choose_port() -> int:
    for port in [5000, 5001, 5002, 5003, 8000, 8080]:
        if port_available(port):
            return port
    return 5000


if __name__ == "__main__":
    ensure_data_files()
    selected_port = choose_port()
    print(f"Local URL: http://127.0.0.1:{selected_port}")
    app.run(host="127.0.0.1", port=selected_port, debug=False)
