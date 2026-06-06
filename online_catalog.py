"""Online catalogue expansion for mainland-accessible music search sources."""

from __future__ import annotations

import base64
from collections import Counter, defaultdict
from dataclasses import asdict
import os
import re
from urllib.parse import parse_qs, urlparse

import requests

from recommender import Song


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://y.qq.com/",
}
NETEASE_HEADERS = {
    "User-Agent": HEADERS["User-Agent"],
    "Referer": "https://music.163.com/",
}
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"

DEFAULT_FEATURES = {
    "genre": "Pop",
    "mood": "Chill",
    "tempo": "Medium",
    "energy": "Medium",
}

SAD_WORDS = {"sad", "cry", "tears", "lonely", "goodbye", "失恋", "再见", "眼泪", "孤独", "遗憾"}
ROMANTIC_WORDS = {"love", "lover", "heart", "kiss", "喜欢", "爱", "告白", "恋", "心动"}
ENERGETIC_WORDS = {"party", "dance", "fire", "run", "high", "派对", "舞", "燃", "热", "少年"}
DARK_WORDS = {"dark", "bad", "monster", "devil", "night", "黑", "夜", "怪", "魔鬼"}

ARTIST_FEATURE_HINTS = {
    "周杰伦": {"genre": "Mandopop", "mood": "Nostalgic", "tempo": "Medium", "energy": "Medium"},
    "林俊杰": {"genre": "Mandopop", "mood": "Romantic", "tempo": "Medium", "energy": "Medium"},
    "陈奕迅": {"genre": "Cantopop", "mood": "Emotional", "tempo": "Medium", "energy": "Medium"},
    "薛之谦": {"genre": "Mandopop", "mood": "Sad", "tempo": "Slow", "energy": "Medium"},
    "邓紫棋": {"genre": "Mandopop", "mood": "Energetic", "tempo": "Medium", "energy": "High"},
    "五月天": {"genre": "Rock", "mood": "Energetic", "tempo": "Fast", "energy": "High"},
    "告五人": {"genre": "Indie", "mood": "Romantic", "tempo": "Medium", "energy": "Medium"},
    "毛不易": {"genre": "Folk", "mood": "Sad", "tempo": "Slow", "energy": "Low"},
    "许嵩": {"genre": "Mandopop", "mood": "Emotional", "tempo": "Medium", "energy": "Medium"},
    "汪苏泷": {"genre": "Mandopop", "mood": "Romantic", "tempo": "Medium", "energy": "Medium"},
    "张杰": {"genre": "Mandopop", "mood": "Energetic", "tempo": "Medium", "energy": "High"},
    "王力宏": {"genre": "R&B", "mood": "Romantic", "tempo": "Medium", "energy": "Medium"},
    "陶喆": {"genre": "R&B", "mood": "Chill", "tempo": "Medium", "energy": "Medium"},
    "李荣浩": {"genre": "Mandopop", "mood": "Chill", "tempo": "Medium", "energy": "Medium"},
    "田馥甄": {"genre": "Mandopop", "mood": "Emotional", "tempo": "Medium", "energy": "Medium"},
    "孙燕姿": {"genre": "Pop", "mood": "Energetic", "tempo": "Medium", "energy": "High"},
    "梁静茹": {"genre": "Mandopop", "mood": "Romantic", "tempo": "Medium", "energy": "Medium"},
    "张惠妹": {"genre": "Pop", "mood": "Emotional", "tempo": "Medium", "energy": "High"},
    "a-lin": {"genre": "Pop", "mood": "Emotional", "tempo": "Medium", "energy": "High"},
}


def normalize_text(value: object) -> str:
    return str(value or "").replace("<em>", "").replace("</em>", "").strip()


def has_chinese(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text)


def build_artist_feature_index(base_songs: list[Song]) -> dict[str, dict[str, str]]:
    grouped = defaultdict(list)
    for song in base_songs:
        grouped[song.artist.lower()].append(song)

    index = {}
    for artist, songs in grouped.items():
        index[artist] = {
            "genre": Counter(song.genre for song in songs).most_common(1)[0][0],
            "mood": Counter(song.mood for song in songs).most_common(1)[0][0],
            "tempo": Counter(song.tempo for song in songs).most_common(1)[0][0],
            "energy": Counter(song.energy for song in songs).most_common(1)[0][0],
        }
    return index


def infer_features(song_name: str, artist: str, base_songs: list[Song]) -> dict[str, str]:
    artist_index = build_artist_feature_index(base_songs)
    features = dict(artist_index.get(artist.lower(), DEFAULT_FEATURES))

    if artist.lower() not in artist_index:
        for hint_artist, hint_features in ARTIST_FEATURE_HINTS.items():
            if hint_artist.lower() in artist.lower():
                features = dict(hint_features)
                break
        else:
            if has_chinese(song_name + artist):
                features["genre"] = "Mandopop"

    lowered = (song_name + " " + artist).lower()
    if any(word in lowered for word in SAD_WORDS):
        features.update({"mood": "Sad", "tempo": "Slow", "energy": "Low"})
    elif any(word in lowered for word in ROMANTIC_WORDS):
        features.update({"mood": "Romantic", "tempo": "Medium", "energy": "Medium"})
    elif any(word in lowered for word in ENERGETIC_WORDS):
        features.update({"mood": "Energetic", "tempo": "Fast", "energy": "High"})
    elif any(word in lowered for word in DARK_WORDS):
        features.update({"mood": "Dark", "tempo": "Medium", "energy": "High"})

    return features


def make_song(song_name: str, artist: str, base_songs: list[Song]) -> Song | None:
    song_name = normalize_text(song_name)
    artist = normalize_text(artist)
    if not song_name or not artist:
        return None

    features = infer_features(song_name, artist, base_songs)
    return Song(
        song=song_name,
        artist=artist,
        genre=features["genre"],
        mood=features["mood"],
        tempo=features["tempo"],
        energy=features["energy"],
    )


def search_qq_music(query: str, base_songs: list[Song], limit: int = 20) -> list[Song]:
    url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"
    params = {"p": 1, "n": limit, "w": query, "format": "json"}
    response = requests.get(url, params=params, headers=HEADERS, timeout=3)
    response.raise_for_status()
    data = response.json()

    songs = []
    for item in data.get("data", {}).get("song", {}).get("list", []):
        singers = item.get("singer") or []
        artist = " / ".join(normalize_text(singer.get("name")) for singer in singers if singer.get("name"))
        song = make_song(item.get("songname"), artist, base_songs)
        if song:
            songs.append(song)
    return songs


def search_kugou(query: str, base_songs: list[Song], limit: int = 20) -> list[Song]:
    url = "http://mobilecdn.kugou.com/api/v3/search/song"
    params = {"format": "json", "keyword": query, "page": 1, "pagesize": limit}
    response = requests.get(url, params=params, headers=HEADERS, timeout=3)
    response.raise_for_status()
    data = response.json()

    songs = []
    for item in data.get("data", {}).get("info", []):
        song = make_song(item.get("songname_original") or item.get("songname"), item.get("singername"), base_songs)
        if song:
            songs.append(song)
    return songs


def extract_qq_playlist_id(value: str) -> str:
    """Extract a public QQ Music playlist id from common shared URL formats."""
    value = normalize_text(value)
    if not value:
        return ""

    if value.isdigit():
        return value

    patterns = [
        r"/playlist/(\d+)",
        r"/taoge\.html.*?[?&]id=(\d+)",
        r"[?&](?:id|disstid)=(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1)

    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    for key in ("id", "disstid"):
        if query.get(key) and query[key][0].isdigit():
            return query[key][0]
    return ""


def fetch_qq_playlist(value: str, base_songs: list[Song], limit: int = 800) -> list[Song]:
    """Fetch a public QQ Music playlist and normalize tracks into Song objects."""
    playlist_id = extract_qq_playlist_id(value)
    if not playlist_id:
        return []

    url = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_playlist_cp.fcg"
    params = {
        "id": playlist_id,
        "format": "json",
        "g_tk": "5381",
        "loginUin": "0",
        "hostUin": "0",
        "inCharset": "utf8",
        "outCharset": "utf-8",
        "notice": "0",
        "platform": "yqq",
        "needNewCode": "0",
    }
    response = requests.get(url, params=params, headers=HEADERS, timeout=8)
    response.raise_for_status()
    data = response.json()

    cdlist = data.get("data", {}).get("cdlist") or data.get("cdlist") or []
    if not cdlist:
        return []

    songs = []
    for item in cdlist[0].get("songlist", [])[:limit]:
        singers = item.get("singer") or []
        artist = " / ".join(normalize_text(singer.get("name")) for singer in singers if singer.get("name"))
        if not artist:
            artist = normalize_text(item.get("singername"))
        song = make_song(item.get("songname") or item.get("name"), artist, base_songs)
        if song:
            songs.append(song)
    return dedupe_songs(songs)


def extract_netease_playlist_id(value: str) -> str:
    """Extract a NetEase Cloud Music playlist id from public shared links."""
    value = normalize_text(value)
    if "163.com" not in value and "music.163" not in value:
        return ""

    patterns = [
        r"[?&]id=(\d+)",
        r"/playlist/(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return match.group(1)

    parsed = urlparse(value)
    query = parse_qs(parsed.query)
    if query.get("id") and query["id"][0].isdigit():
        return query["id"][0]
    return ""


def fetch_netease_playlist(value: str, base_songs: list[Song], limit: int = 800) -> list[Song]:
    """Fetch a public NetEase Cloud Music playlist and normalize tracks."""
    playlist_id = extract_netease_playlist_id(value)
    if not playlist_id:
        return []

    url = "https://music.163.com/api/playlist/detail"
    response = requests.get(url, params={"id": playlist_id}, headers=NETEASE_HEADERS, timeout=8)
    response.raise_for_status()
    data = response.json()
    tracks = (
        data.get("result", {}).get("tracks")
        or data.get("playlist", {}).get("tracks")
        or []
    )

    songs = []
    for item in tracks[:limit]:
        artists = item.get("artists") or item.get("ar") or []
        artist = " / ".join(normalize_text(artist.get("name")) for artist in artists if artist.get("name"))
        song = make_song(item.get("name"), artist, base_songs)
        if song:
            songs.append(song)
    return dedupe_songs(songs)


def extract_spotify_playlist_id(value: str) -> str:
    """Extract a Spotify playlist id from web or URI formats."""
    value = normalize_text(value)
    if "spotify:playlist:" in value:
        return value.rsplit(":", 1)[-1].split("?")[0]

    match = re.search(r"open\.spotify\.com/playlist/([A-Za-z0-9]+)", value)
    if match:
        return match.group(1)
    return ""


def spotify_access_token(client_id: str = "", client_secret: str = "") -> str:
    """Get a Spotify app token using Client Credentials."""
    client_id = client_id or os.environ.get("SPOTIFY_CLIENT_ID", "")
    client_secret = client_secret or os.environ.get("SPOTIFY_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return ""

    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        headers={"Authorization": f"Basic {credentials}"},
        data={"grant_type": "client_credentials"},
        timeout=8,
    )
    response.raise_for_status()
    return response.json().get("access_token", "")


def fetch_spotify_playlist(
    value: str,
    base_songs: list[Song],
    limit: int = 800,
    client_id: str = "",
    client_secret: str = "",
) -> list[Song]:
    """Fetch a public Spotify playlist when API credentials are available."""
    playlist_id = extract_spotify_playlist_id(value)
    if not playlist_id:
        return []

    token = spotify_access_token(client_id, client_secret)
    if not token:
        return []

    songs = []
    offset = 0
    headers = {"Authorization": f"Bearer {token}"}
    while len(songs) < limit:
        response = requests.get(
            f"{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks",
            params={
                "limit": min(100, limit - len(songs)),
                "offset": offset,
                "fields": "items(track(name,artists(name))),next",
            },
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        for item in items:
            track = item.get("track") or {}
            artists = track.get("artists") or []
            artist = " / ".join(normalize_text(part.get("name")) for part in artists if part.get("name"))
            song = make_song(track.get("name"), artist, base_songs)
            if song:
                songs.append(song)

        if not data.get("next"):
            break
        offset += len(items)

    return dedupe_songs(songs)


def fetch_playlist_link(
    value: str,
    base_songs: list[Song],
    limit: int = 800,
    spotify_client_id: str = "",
    spotify_client_secret: str = "",
) -> list[Song]:
    """Auto-detect QQ Music, NetEase Cloud Music, or Spotify playlist links."""
    lowered = value.lower()
    if "spotify" in lowered:
        return fetch_spotify_playlist(
            value,
            base_songs,
            limit=limit,
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
        )
    if "163.com" in lowered or "music.163" in lowered:
        return fetch_netease_playlist(value, base_songs, limit=limit)
    return fetch_qq_playlist(value, base_songs, limit=limit)


def dedupe_songs(songs: list[Song]) -> list[Song]:
    seen = set()
    unique = []
    for song in songs:
        key = (song.song.lower(), song.artist.lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(song)
    return unique


def search_online_catalog(query: str, base_songs: list[Song], limit: int = 40) -> list[Song]:
    """Search multiple online sources and normalize results into Song objects."""
    if not query.strip():
        return []

    results: list[Song] = []
    for searcher in (search_qq_music, search_kugou):
        try:
            results.extend(searcher(query, base_songs, limit=limit // 2))
        except requests.RequestException:
            continue
        except ValueError:
            continue

    return dedupe_songs(results)[:limit]


def songs_to_dicts(songs: list[Song]) -> list[dict[str, str]]:
    return [asdict(song) for song in songs]


def songs_from_dicts(rows: list[dict[str, str]]) -> list[Song]:
    return [Song(**row) for row in rows]
