from __future__ import annotations

import re
from typing import Iterable


def _get(row: object, key: str, default: object = "") -> object:
    if isinstance(row, dict):
        return row.get(key, default)
    if hasattr(row, "_asdict"):
        return row._asdict().get(key, default)
    if hasattr(row, key):
        return getattr(row, key)
    try:
        return row[key]
    except Exception:
        return default


def _float(row: object, key: str, default: float = 0.0) -> float:
    try:
        value = _get(row, key, default)
        if value == "" or value is None:
            return default
        return float(value)
    except Exception:
        return default


def _token_value(value: object) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"


def bucket_audio_features(song_row: object) -> list[str]:
    energy = _float(song_row, "energy")
    valence = _float(song_row, "valence")
    tempo = _float(song_row, "tempo")
    danceability = _float(song_row, "danceability")
    acousticness = _float(song_row, "acousticness")
    speechiness = _float(song_row, "speechiness")
    popularity = _float(song_row, "popularity")

    tokens = []
    tokens.append("energy:high" if energy >= 0.7 else "energy:low" if energy <= 0.4 else "energy:medium")
    tokens.append("valence:positive" if valence >= 0.65 else "valence:sad" if valence <= 0.4 else "valence:neutral")
    tokens.append("tempo:fast" if tempo >= 125 else "tempo:slow" if tempo <= 90 else "tempo:medium")
    tokens.append(
        "danceability:high"
        if danceability >= 0.7
        else "danceability:low"
        if danceability <= 0.4
        else "danceability:medium"
    )
    if acousticness >= 0.6:
        tokens.append("acousticness:high")
    if speechiness >= 0.25:
        tokens.append("speechiness:high")
    if popularity >= 75:
        tokens.append("popularity:high")
    return tokens


def extract_tag_features(song_row: object) -> list[str]:
    tags = _get(song_row, "tags", "")
    return [f"tag:{_token_value(tag)}" for tag in re.split(r"[,;/|]+", str(tags)) if tag.strip()]


def build_item_feature_tokens(song_row: object) -> list[str]:
    genre = _get(song_row, "genre", "Unknown")
    artist = _get(song_row, "artist_name", "Unknown Artist")
    source = _get(song_row, "source", "manual")

    tokens = [
        f"genre:{_token_value(genre)}",
        f"artist:{_token_value(artist)}",
        f"source:{_token_value(source)}",
    ]
    tokens.extend(extract_tag_features(song_row))
    tokens.extend(bucket_audio_features(song_row))
    return sorted(set(tokens))


def build_item_features_matrix(songs_df, dataset):
    item_features: list[tuple[str, Iterable[str]]] = []
    for row in songs_df.itertuples(index=False):
        item_features.append((str(row.track_id), build_item_feature_tokens(row)))
    return dataset.build_item_features(item_features, normalize=True)
