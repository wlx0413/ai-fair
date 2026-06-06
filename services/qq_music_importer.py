from __future__ import annotations

import re
import json
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests

from services.data_store import add_interaction, add_playlist, match_local_song, stable_track_id, upsert_songs
from services.music_search import build_estimated_song_row


FRIENDLY_ERROR = "QQ Music import failed. Please try manual playlist input or song search."


def extract_qq_playlist_id(input_text: str) -> str | None:
    text = (input_text or "").strip()
    if not text:
        return None
    parsed = urlparse(text)
    query = parse_qs(parsed.query)
    for key in ("id", "disstid", "tid"):
        if query.get(key) and str(query[key][0]).isdigit():
            return str(query[key][0])
    patterns = [
        r"/playlist/(\d+)",
        r"playlist/(\d+)",
        r"/taoge\.html.*?[?&]id=(\d+)",
        r"[?&](?:id|disstid|tid)=(\d+)",
        r"(?:id|disstid|tid)=(\d+)",
        r"[?&]id=(\d+)",
        r"^[0-9]{4,}$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1) if match.groups() else match.group(0)
    return None


def import_qq_playlist(playlist_url_or_id: str) -> dict[str, Any]:
    playlist_id = extract_qq_playlist_id(playlist_url_or_id)
    if not playlist_id:
        return {
            "success": False,
            "message": FRIENDLY_ERROR,
            "songs": [],
            "playlist_id": "",
            "tried_endpoints": [],
            "failure_reason": "Could not recognize a QQ Music playlist ID from the input.",
        }

    payload = None
    tried_endpoints = []
    failure_reason = ""
    for fetcher in (_fetch_with_qzone_endpoint, _fetch_with_v8_endpoint, _fetch_with_musicu_endpoint):
        try:
            tried_endpoints.append(fetcher.__name__.removeprefix("_fetch_with_").removesuffix("_endpoint"))
            payload = fetcher(playlist_id)
            if payload and payload.get("songs"):
                break
        except Exception as exc:
            failure_reason = f"{fetcher.__name__}: {exc.__class__.__name__}"
            payload = None

    if not payload or not payload.get("songs"):
        return {
            "success": False,
            "message": FRIENDLY_ERROR,
            "songs": [],
            "playlist_id": playlist_id,
            "tried_endpoints": tried_endpoints,
            "failure_reason": failure_reason or "No public playlist metadata was returned. The playlist may be private or blocked by QQ Music.",
        }

    playlist_name = payload.get("playlist_name") or f"QQ Music Playlist {playlist_id}"
    songs = [normalize_qq_song(song) for song in payload.get("songs", [])]
    songs = [song for song in songs if song.get("track_name")]
    if not songs:
        return {
            "success": False,
            "message": FRIENDLY_ERROR,
            "songs": [],
            "playlist_id": playlist_id,
            "tried_endpoints": tried_endpoints,
            "failure_reason": "Playlist metadata was returned, but no valid songs were found.",
        }

    saved = save_imported_playlist(playlist_name, songs)
    return {
        "success": True,
        "message": f"Imported {len(saved)} songs from QQ Music metadata.",
        "playlist_id": playlist_id,
        "playlist_name": playlist_name,
        "tried_endpoints": tried_endpoints,
        "imported_count": len(saved),
        "songs": saved,
    }


def _fetch_with_qzone_endpoint(playlist_id: str) -> dict[str, Any] | None:
    url = "https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg"
    try:
        response = requests.get(
            url,
            params={
                "type": "1",
                "json": "1",
                "utf8": "1",
                "onlysong": "0",
                "disstid": playlist_id,
                "format": "json",
            },
            headers={
                "User-Agent": "Mozilla/5.0 AI Fair metadata importer",
                "Referer": "https://y.qq.com/",
            },
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    cdlist = data.get("cdlist") or []
    if not cdlist:
        return None
    playlist = cdlist[0]
    raw_songs = playlist.get("songlist") or []
    return {"playlist_name": playlist.get("dissname") or "", "songs": raw_songs}


def _fetch_with_v8_endpoint(playlist_id: str) -> dict[str, Any] | None:
    url = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_playlist_cp.fcg"
    try:
        response = requests.get(
            url,
            params={
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
            },
            headers={
                "User-Agent": "Mozilla/5.0 AI Fair metadata importer",
                "Referer": "https://y.qq.com/",
            },
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    cdlist = data.get("data", {}).get("cdlist") or data.get("cdlist") or []
    if not cdlist:
        return None
    playlist = cdlist[0]
    return {"playlist_name": playlist.get("dissname") or playlist.get("title") or "", "songs": playlist.get("songlist") or []}


def _fetch_with_musicu_endpoint(playlist_id: str) -> dict[str, Any] | None:
    url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
    request_payload = {
        "comm": {"ct": 24, "cv": 0},
        "req_1": {
            "module": "music.srfDissInfo.aiDissInfo",
            "method": "uniform_get_Dissinfo",
            "param": {
                "disstid": int(playlist_id),
                "userinfo": 1,
                "tag": 1,
                "orderlist": 1,
                "song_begin": 0,
                "song_num": 800,
                "onlysonglist": 0,
                "enc_host_uin": "",
            },
        },
    }
    try:
        response = requests.get(
            url,
            params={"format": "json", "data": json.dumps(request_payload, ensure_ascii=False)},
            headers={
                "User-Agent": "Mozilla/5.0 AI Fair metadata importer",
                "Referer": "https://y.qq.com/",
            },
            timeout=8,
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    diss = data.get("req_1", {}).get("data", {}).get("dirinfo") or {}
    songlist = data.get("req_1", {}).get("data", {}).get("songlist") or []
    return {"playlist_name": diss.get("title") or "", "songs": songlist}


def normalize_qq_song(raw_song: dict[str, Any]) -> dict[str, Any]:
    song_info = raw_song.get("songInfo") if isinstance(raw_song.get("songInfo"), dict) else raw_song
    title = song_info.get("songname") or song_info.get("title") or song_info.get("name") or raw_song.get("name") or ""
    singers = song_info.get("singer") or song_info.get("singers") or raw_song.get("singer") or []
    if isinstance(singers, list):
        artist = ", ".join([item.get("name", "") if isinstance(item, dict) else str(item) for item in singers]).strip(", ")
    else:
        artist = str(singers)
    album_obj = song_info.get("album") or raw_song.get("album") or {}
    album = song_info.get("albumname") or (album_obj.get("name", "") if isinstance(album_obj, dict) else "")
    matched = match_local_song(title, artist)
    if matched:
        matched["source"] = "qq"
        return matched
    return build_estimated_song_row(
        {
            "track_id": stable_track_id(title, artist or "Unknown Artist", "qq"),
            "track_name": title,
            "artist_name": artist or "Unknown Artist",
            "album_name": album or "",
            "source": "qq",
            "external_url": "",
        },
        source="qq",
    )


def save_imported_playlist(playlist_name: str, songs: list[dict[str, Any]], user_id: str = "demo_user") -> list[dict[str, Any]]:
    add_playlist(playlist_name, "qq", len(songs))
    saved = upsert_songs(songs)
    for song in saved:
        if song.get("has_audio_features"):
            add_interaction(user_id, str(song["track_id"]), "playlist_import")
    return saved
