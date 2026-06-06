from __future__ import annotations

import os
import time
from urllib.parse import quote_plus

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

from services.data_store import SONG_COLUMNS, load_songs, match_local_song, stable_track_id


MUSICBRAINZ_LAST_REQUEST = 0.0
USER_AGENT = "AI-Fair-Music-Recommendation-System/1.0 (educational demo)"


def search_music(query: str, limit: int = 10) -> list[dict[str, object]]:
    query = (query or "").strip()
    if not query:
        return []

    results = search_local_csv(query, limit=limit)
    if len(results) >= limit:
        return results[:limit]

    needed = limit - len(results)
    seen = {(str(item["track_name"]).lower(), str(item["artist_name"]).lower()) for item in results}
    # Deezer usually returns the cleanest public track metadata for mainstream
    # music, so use it before broader metadata indexes.
    for provider in (search_deezer, search_musicbrainz, search_lastfm):
        if needed <= 0:
            break
        for item in provider(query, limit=needed):
            key = (str(item["track_name"]).lower(), str(item["artist_name"]).lower())
            if key in seen:
                continue
            seen.add(key)
            results.append(item)
            needed -= 1
            if needed <= 0:
                break
    return results[:limit]


def search_local_csv(query: str, limit: int = 10) -> list[dict[str, object]]:
    songs = load_songs()
    q = query.lower()
    if songs.empty:
        return []
    mask = (
        songs["track_name"].astype(str).str.lower().str.contains(q, na=False)
        | songs["artist_name"].astype(str).str.lower().str.contains(q, na=False)
        | songs["genre"].astype(str).str.lower().str.contains(q, na=False)
        | songs["tags"].astype(str).str.lower().str.contains(q, na=False)
    )
    return [_format_result(row, "local") for row in songs[mask].head(limit).to_dict("records")]


def search_musicbrainz(query: str, limit: int = 5) -> list[dict[str, object]]:
    global MUSICBRAINZ_LAST_REQUEST
    elapsed = time.time() - MUSICBRAINZ_LAST_REQUEST
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    MUSICBRAINZ_LAST_REQUEST = time.time()

    try:
        response = requests.get(
            "https://musicbrainz.org/ws/2/recording/",
            params={"query": query, "fmt": "json", "limit": limit},
            headers={"User-Agent": USER_AGENT},
            timeout=8,
        )
        response.raise_for_status()
        recordings = response.json().get("recordings", [])
    except Exception:
        return []

    results = []
    for item in recordings:
        artists = item.get("artist-credit") or []
        artist_name = "Unknown Artist"
        if artists and isinstance(artists[0], dict):
            artist_name = artists[0].get("name") or artists[0].get("artist", {}).get("name") or artist_name
        album_name = ""
        releases = item.get("releases") or []
        if releases:
            album_name = releases[0].get("title") or ""
        results.append(
            build_estimated_song_row(
                {
                "track_id": stable_track_id(item.get("title", ""), artist_name, "musicbrainz"),
                "track_name": item.get("title", ""),
                "artist_name": artist_name,
                "album_name": album_name,
                "source": "musicbrainz",
                "external_url": f"https://musicbrainz.org/recording/{item.get('id')}" if item.get("id") else "",
                },
                source="musicbrainz",
            )
        )
    return [_format_result(row, "musicbrainz") for row in results]


def search_lastfm(query: str, limit: int = 5) -> list[dict[str, object]]:
    api_key = os.getenv("LASTFM_API_KEY", "").strip()
    if not api_key:
        return []
    try:
        response = requests.get(
            "https://ws.audioscrobbler.com/2.0/",
            params={"method": "track.search", "track": query, "api_key": api_key, "format": "json", "limit": limit},
            timeout=8,
        )
        response.raise_for_status()
        tracks = response.json().get("results", {}).get("trackmatches", {}).get("track", [])
    except Exception:
        return []

    results = []
    for item in tracks:
        results.append(
            build_estimated_song_row(
                {
                "track_id": stable_track_id(item.get("name", ""), item.get("artist", ""), "lastfm"),
                "track_name": item.get("name", ""),
                "artist_name": item.get("artist", "Unknown Artist"),
                "album_name": "",
                "source": "lastfm",
                "external_url": item.get("url", ""),
                },
                source="lastfm",
            )
        )
    return [_format_result(row, "lastfm") for row in results]


def search_deezer(query: str, limit: int = 5) -> list[dict[str, object]]:
    try:
        response = requests.get(
            "https://api.deezer.com/search",
            params={"q": query, "limit": limit},
            timeout=8,
        )
        response.raise_for_status()
        tracks = response.json().get("data", [])
    except Exception:
        return []

    results = []
    for item in tracks:
        artist = item.get("artist") or {}
        album = item.get("album") or {}
        artist_name = artist.get("name", "Unknown Artist")
        rank = item.get("rank") or 0
        results.append(
            build_estimated_song_row(
                {
                "track_id": stable_track_id(item.get("title", ""), artist_name, "deezer"),
                "track_name": item.get("title", ""),
                "artist_name": artist_name,
                "album_name": album.get("title", ""),
                "source": "deezer",
                "external_url": item.get("link", ""),
                "popularity": min(95, max(45, int(float(rank) / 10000))) if rank else 68,
                },
                source="deezer",
            )
        )
    return [_format_result(row, "deezer") for row in results]


def _format_result(row: dict[str, object], default_source: str) -> dict[str, object]:
    formatted = {column: row.get(column, "") for column in SONG_COLUMNS}
    formatted.update(
        {
            "track_id": row.get("track_id") or stable_track_id(str(row.get("track_name", "")), str(row.get("artist_name", "")), default_source),
            "track_name": row.get("track_name", ""),
            "artist_name": row.get("artist_name", "Unknown Artist"),
            "album_name": row.get("album_name", ""),
            "source": row.get("source", default_source),
            "external_url": row.get("external_url", ""),
            "has_audio_features": bool(row.get("has_audio_features", False)),
        }
    )
    formatted["training_note"] = (
        "Audio features are estimated from public metadata for model training."
        if formatted["has_audio_features"] and formatted.get("source") in {"deezer", "musicbrainz", "lastfm"}
        else "" if formatted["has_audio_features"] else "This online result was found, but it does not have enough audio features for model training."
    )
    return formatted


def search_url(track_name: str, artist_name: str) -> str:
    return f"https://www.deezer.com/search/{quote_plus(f'{track_name} {artist_name}')}"


GENRE_FEATURES = {
    "Pop": (0.72, 0.70, 0.72, 112, 0.12, 0.01, 0.07, 0.12, "dance,pop,radio"),
    "Rock": (0.50, 0.84, 0.48, 130, 0.05, 0.02, 0.06, 0.17, "guitar,rock,anthem"),
    "Electronic": (0.70, 0.86, 0.46, 126, 0.03, 0.30, 0.06, 0.15, "dance,electronic,edm"),
    "Hip-hop": (0.80, 0.68, 0.48, 98, 0.05, 0.00, 0.22, 0.14, "rap,beats,flow"),
    "Ballad": (0.43, 0.32, 0.28, 84, 0.78, 0.01, 0.04, 0.10, "piano,emotional,slow"),
    "Indie": (0.58, 0.56, 0.55, 108, 0.34, 0.04, 0.05, 0.13, "indie,melodic,alternative"),
    "R&B": (0.66, 0.52, 0.53, 94, 0.26, 0.00, 0.09, 0.12, "soul,smooth,rnb"),
    "Acoustic": (0.52, 0.36, 0.50, 88, 0.82, 0.03, 0.04, 0.11, "folk,acoustic,singer-songwriter"),
}

ARTIST_GENRE_HINTS = {
    "taylor swift": "Pop", "ed sheeran": "Pop", "dua lipa": "Pop", "olivia rodrigo": "Pop", "miley cyrus": "Pop",
    "the weeknd": "R&B", "sza": "R&B", "frank ocean": "R&B", "alicia keys": "R&B", "john legend": "R&B",
    "adele": "Ballad", "sam smith": "Ballad", "celine dion": "Ballad", "whitney houston": "Ballad",
    "coldplay": "Rock", "linkin park": "Rock", "nirvana": "Rock", "radiohead": "Rock", "foo fighters": "Rock",
    "avicii": "Electronic", "zedd": "Electronic", "calvin harris": "Electronic", "daft punk": "Electronic", "skrillex": "Electronic",
    "drake": "Hip-hop", "kendrick lamar": "Hip-hop", "eminem": "Hip-hop", "travis scott": "Hip-hop", "kanye west": "Hip-hop",
    "vance joy": "Indie", "the lumineers": "Indie", "hozier": "Indie", "mgmt": "Indie", "phoenix": "Indie",
    "jack johnson": "Acoustic", "bon iver": "Acoustic", "jason mraz": "Acoustic", "jose gonzalez": "Acoustic",
}

TITLE_GENRE_HINTS = {
    "remix": "Electronic", "club": "Electronic", "dance": "Electronic", "edm": "Electronic",
    "rap": "Hip-hop", "freestyle": "Hip-hop", "cypher": "Hip-hop",
    "acoustic": "Acoustic", "unplugged": "Acoustic", "piano": "Ballad", "sad": "Ballad",
    "love": "R&B", "soul": "R&B", "rock": "Rock",
}


def build_estimated_song_row(row: dict[str, object], source: str = "online") -> dict[str, object]:
    track_name = str(row.get("track_name") or "")
    artist_name = str(row.get("artist_name") or "Unknown Artist")
    local_match = match_local_song(track_name, artist_name)
    if local_match:
        local_match["source"] = source
        local_match["external_url"] = row.get("external_url", local_match.get("external_url", ""))
        return local_match

    genre = infer_genre(track_name, artist_name)
    danceability, energy, valence, tempo, acousticness, instrumentalness, speechiness, liveness, tags = GENRE_FEATURES[genre]
    popularity = float(row.get("popularity") or 68)
    return {
        **row,
        "genre": genre,
        "tags": f"{tags},estimated-features,online-metadata",
        "danceability": danceability,
        "energy": energy,
        "valence": valence,
        "tempo": tempo,
        "acousticness": acousticness,
        "instrumentalness": instrumentalness,
        "speechiness": speechiness,
        "liveness": liveness,
        "popularity": popularity,
        "source": source,
        "has_audio_features": True,
    }


def infer_genre(track_name: str, artist_name: str) -> str:
    artist = artist_name.lower()
    title = track_name.lower()
    for key, genre in ARTIST_GENRE_HINTS.items():
        if key in artist:
            return genre
    for key, genre in TITLE_GENRE_HINTS.items():
        if key in title:
            return genre
    return "Pop"
