"""Playlist parsing helpers for uploaded QQ Music exports or copied text."""

from __future__ import annotations

import csv
import io
import json
import re
from html.parser import HTMLParser

from online_catalog import make_song
from recommender import Song


class TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        cleaned = data.strip()
        if cleaned:
            self.parts.append(cleaned)

    def text(self) -> str:
        return "\n".join(self.parts)


def clean_cell(value: object) -> str:
    return str(value or "").strip().strip('"').strip("'")


def song_from_pair(song_name: str, artist: str, base_songs: list[Song]) -> Song | None:
    song_name = clean_cell(song_name)
    artist = clean_cell(artist)
    if not song_name or not artist:
        return None
    return make_song(song_name, artist, base_songs)


def parse_csv_playlist(text: str, base_songs: list[Song]) -> list[Song]:
    songs = []
    reader = csv.DictReader(io.StringIO(text))
    fieldnames = {name.lower(): name for name in reader.fieldnames or []}

    song_key = next((fieldnames[key] for key in ["song", "歌曲", "歌曲名", "歌名", "title", "name"] if key in fieldnames), None)
    artist_key = next((fieldnames[key] for key in ["artist", "歌手", "singer", "singers"] if key in fieldnames), None)

    if not song_key or not artist_key:
        return []

    for row in reader:
        song = song_from_pair(row.get(song_key, ""), row.get(artist_key, ""), base_songs)
        if song:
            songs.append(song)
    return songs


def walk_json(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def parse_json_playlist(text: str, base_songs: list[Song]) -> list[Song]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return []

    songs = []
    for item in walk_json(payload):
        song_name = (
            item.get("song")
            or item.get("songname")
            or item.get("songName")
            or item.get("title")
            or item.get("name")
        )
        artist = item.get("artist") or item.get("singer") or item.get("singername")
        if isinstance(artist, list):
            artist = " / ".join(str(part.get("name", part)) if isinstance(part, dict) else str(part) for part in artist)
        song = song_from_pair(song_name, artist, base_songs)
        if song:
            songs.append(song)
    return songs


def html_to_text(text: str) -> str:
    parser = TextHTMLParser()
    parser.feed(text)
    return parser.text()


def parse_text_playlist(text: str, base_songs: list[Song]) -> list[Song]:
    songs = []
    text = html_to_text(text) if "<html" in text.lower() or "</" in text else text

    patterns = [
        re.compile(r"^\s*(?P<song>.+?)\s*[-–—|]\s*(?P<artist>.+?)\s*$"),
        re.compile(r"^\s*(?P<artist>.+?)\s*[-–—|]\s*(?P<song>.+?)\s*$"),
        re.compile(r"^\s*\d+[\).\s]+(?P<song>.+?)\s+[-–—|]\s+(?P<artist>.+?)\s*$"),
    ]

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if len(line) > 160:
            continue
        for pattern in patterns:
            match = pattern.match(line)
            if not match:
                continue
            song = song_from_pair(match.group("song"), match.group("artist"), base_songs)
            if song:
                songs.append(song)
            break

    return songs


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


def parse_playlist_upload(filename: str, content: bytes, base_songs: list[Song]) -> list[Song]:
    text = content.decode("utf-8", errors="ignore")
    lower_name = filename.lower()

    parsed = []
    if lower_name.endswith(".csv"):
        parsed = parse_csv_playlist(text, base_songs)
    elif lower_name.endswith(".json"):
        parsed = parse_json_playlist(text, base_songs)
    elif lower_name.endswith((".html", ".htm")):
        parsed = parse_text_playlist(html_to_text(text), base_songs)

    if not parsed:
        parsed = parse_json_playlist(text, base_songs)
    if not parsed:
        parsed = parse_csv_playlist(text, base_songs)
    if not parsed:
        parsed = parse_text_playlist(text, base_songs)

    return dedupe_songs(parsed)


def parse_playlist_text(text: str, base_songs: list[Song]) -> list[Song]:
    return dedupe_songs(
        parse_json_playlist(text, base_songs)
        or parse_csv_playlist(text, base_songs)
        or parse_text_playlist(text, base_songs)
    )
