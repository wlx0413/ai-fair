from __future__ import annotations

import csv
import hashlib
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd


BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
DATA_DIR = Path(os.getenv("AI_MUSIC_DATA_DIR", BASE_DIR / "data"))
MODELS_DIR = Path(os.getenv("AI_MUSIC_MODELS_DIR", BASE_DIR / "models"))

SONGS_PATH = DATA_DIR / "songs.csv"
PLAYLISTS_PATH = DATA_DIR / "playlists.csv"
INTERACTIONS_PATH = DATA_DIR / "interactions.csv"
FEEDBACK_PATH = DATA_DIR / "feedback.csv"
MODEL_PATH = MODELS_DIR / "lightfm_model.pkl"

SONG_COLUMNS = [
    "track_id",
    "track_name",
    "artist_name",
    "album_name",
    "genre",
    "tags",
    "danceability",
    "energy",
    "valence",
    "tempo",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
    "popularity",
    "source",
    "external_url",
    "has_audio_features",
]

PLAYLIST_COLUMNS = ["playlist_id", "playlist_name", "source", "song_count", "created_at"]
INTERACTION_COLUMNS = ["interaction_id", "user_id", "track_id", "interaction_type", "weight", "timestamp"]
FEEDBACK_COLUMNS = ["feedback_id", "user_id", "track_id", "label", "timestamp"]

AUDIO_FEATURE_COLUMNS = [
    "danceability",
    "energy",
    "valence",
    "tempo",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
    "popularity",
]

INTERACTION_WEIGHTS = {
    "playlist_import": 1.0,
    "manual_add": 1.0,
    "like": 2.0,
    "dislike": -1.0,
    "skip": -0.5,
}


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or uuid.uuid4().hex[:10]


def stable_track_id(track_name: str, artist_name: str, source: str = "demo") -> str:
    raw = f"{track_name}|{artist_name}|{source}".lower().encode("utf-8")
    digest = hashlib.sha1(raw).hexdigest()[:10]
    return f"{source}_{slugify(track_name)[:28]}_{digest}"


def safe_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def ensure_data_files() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)
    _ensure_csv(SONGS_PATH, SONG_COLUMNS)
    _ensure_csv(PLAYLISTS_PATH, PLAYLIST_COLUMNS)
    _ensure_csv(INTERACTIONS_PATH, INTERACTION_COLUMNS)
    _ensure_csv(FEEDBACK_PATH, FEEDBACK_COLUMNS)
    ensure_demo_songs()


def _ensure_csv(path: Path, columns: list[str]) -> None:
    if path.exists():
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        csv.DictWriter(handle, fieldnames=columns).writeheader()


def read_csv(path: Path, columns: list[str]) -> pd.DataFrame:
    ensure_data_files()
    try:
        df = pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=columns)
    for column in columns:
        if column not in df.columns:
            df[column] = ""
    return df[columns]


def write_csv(path: Path, df: pd.DataFrame, columns: list[str]) -> None:
    path.parent.mkdir(exist_ok=True)
    df = df.copy()
    for column in columns:
        if column not in df.columns:
            df[column] = ""
    df[columns].to_csv(path, index=False)


def load_songs() -> pd.DataFrame:
    df = read_csv(SONGS_PATH, SONG_COLUMNS)
    df = df.drop_duplicates(subset=["track_id"], keep="first")
    for column in AUDIO_FEATURE_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["has_audio_features"] = df["has_audio_features"].apply(safe_bool)
    return df


def load_interactions() -> pd.DataFrame:
    df = read_csv(INTERACTIONS_PATH, INTERACTION_COLUMNS)
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce").fillna(0.0)
    return df


def load_feedback() -> pd.DataFrame:
    df = read_csv(FEEDBACK_PATH, FEEDBACK_COLUMNS)
    df["label"] = pd.to_numeric(df["label"], errors="coerce").fillna(0).astype(int)
    return df


def upsert_songs(rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    ensure_data_files()
    existing = load_songs()
    existing_ids = set(existing["track_id"].astype(str))
    normalized_rows: list[dict[str, object]] = []

    for row in rows:
        normalized = normalize_song_row(row)
        if not normalized["track_id"]:
            normalized["track_id"] = stable_track_id(
                normalized["track_name"], normalized["artist_name"], str(normalized["source"] or "manual")
            )
        normalized_rows.append(normalized)

    new_rows = [row for row in normalized_rows if row["track_id"] not in existing_ids]
    if new_rows:
        combined = pd.concat([existing, pd.DataFrame(new_rows)], ignore_index=True)
        combined = combined.drop_duplicates(subset=["track_id"], keep="first")
        write_csv(SONGS_PATH, combined, SONG_COLUMNS)
    return normalized_rows


def normalize_song_row(row: dict[str, object]) -> dict[str, object]:
    source = str(row.get("source") or "manual").strip() or "manual"
    track_name = str(row.get("track_name") or row.get("song") or "").strip()
    artist_name = str(row.get("artist_name") or row.get("artist") or "Unknown Artist").strip()
    has_features = safe_bool(row.get("has_audio_features"))
    if not has_features:
        has_features = all(row.get(column) not in [None, ""] for column in AUDIO_FEATURE_COLUMNS)
    normalized = {column: row.get(column, "") for column in SONG_COLUMNS}
    normalized.update(
        {
            "track_id": str(row.get("track_id") or stable_track_id(track_name, artist_name, source)),
            "track_name": track_name,
            "artist_name": artist_name,
            "album_name": str(row.get("album_name") or "").strip(),
            "genre": str(row.get("genre") or "Unknown").strip(),
            "tags": str(row.get("tags") or "").strip(),
            "source": source,
            "external_url": str(row.get("external_url") or "").strip(),
            "has_audio_features": bool(has_features),
        }
    )
    for column in AUDIO_FEATURE_COLUMNS:
        value = row.get(column)
        normalized[column] = "" if value in [None, ""] else float(value)
    return normalized


def add_playlist(playlist_name: str, source: str, song_count: int) -> dict[str, str]:
    ensure_data_files()
    row = {
        "playlist_id": f"{source}_{uuid.uuid4().hex[:12]}",
        "playlist_name": playlist_name or f"{source.title()} Playlist",
        "source": source,
        "song_count": int(song_count),
        "created_at": now_iso(),
    }
    df = read_csv(PLAYLISTS_PATH, PLAYLIST_COLUMNS)
    write_csv(PLAYLISTS_PATH, pd.concat([df, pd.DataFrame([row])], ignore_index=True), PLAYLIST_COLUMNS)
    return row


def add_interaction(user_id: str, track_id: str, interaction_type: str) -> dict[str, object]:
    ensure_data_files()
    row = {
        "interaction_id": uuid.uuid4().hex,
        "user_id": user_id or "demo_user",
        "track_id": track_id,
        "interaction_type": interaction_type,
        "weight": INTERACTION_WEIGHTS.get(interaction_type, 1.0),
        "timestamp": now_iso(),
    }
    df = read_csv(INTERACTIONS_PATH, INTERACTION_COLUMNS)
    write_csv(INTERACTIONS_PATH, pd.concat([df, pd.DataFrame([row])], ignore_index=True), INTERACTION_COLUMNS)
    return row


def add_feedback(user_id: str, track_id: str, label: int) -> dict[str, object]:
    ensure_data_files()
    label = 1 if int(label) == 1 else 0
    row = {
        "feedback_id": uuid.uuid4().hex,
        "user_id": user_id or "demo_user",
        "track_id": track_id,
        "label": label,
        "timestamp": now_iso(),
    }
    feedback_df = read_csv(FEEDBACK_PATH, FEEDBACK_COLUMNS)
    write_csv(FEEDBACK_PATH, pd.concat([feedback_df, pd.DataFrame([row])], ignore_index=True), FEEDBACK_COLUMNS)
    add_interaction(user_id, track_id, "like" if label == 1 else "dislike")
    return row


def match_local_song(track_name: str, artist_name: str) -> dict[str, object] | None:
    songs = load_songs()
    wanted_title = slugify(track_name)
    wanted_artist = slugify(artist_name)
    if songs.empty:
        return None
    songs = songs.copy()
    songs["_title"] = songs["track_name"].apply(slugify)
    songs["_artist"] = songs["artist_name"].apply(slugify)
    exact = songs[(songs["_title"] == wanted_title) & (songs["_artist"] == wanted_artist)]
    if not exact.empty:
        return exact.iloc[0][SONG_COLUMNS].to_dict()
    title_match = songs[songs["_title"] == wanted_title]
    if not title_match.empty:
        return title_match.iloc[0][SONG_COLUMNS].to_dict()
    return None


def ensure_demo_songs() -> None:
    existing = pd.read_csv(SONGS_PATH) if SONGS_PATH.exists() else pd.DataFrame(columns=SONG_COLUMNS)
    demo_rows = [normalize_song_row(row) for row in build_demo_songs()]
    changed_existing = False
    if not existing.empty:
        original_len = len(existing)
        original_source = existing.get("source", pd.Series(dtype=str)).astype(str).tolist()
        title_text = existing["track_name"].astype(str)
        artist_text = existing["artist_name"].astype(str)
        existing = existing[
            ~title_text.str.match(r"^Demo .+ Track \d+$", case=False, na=False)
            & ~artist_text.str.match(r"^AI Fair Artist \d+$", case=False, na=False)
        ].copy()
        existing.loc[existing["source"].astype(str).str.lower() == "demo", "source"] = "curated"
        existing.loc[
            existing["album_name"].astype(str).str.lower() == "ai fair demo dataset",
            "album_name",
        ] = "Curated Real Song Library"
        changed_existing = original_len != len(existing) or original_source != existing.get("source", pd.Series(dtype=str)).astype(str).tolist()
    if existing.empty:
        write_csv(SONGS_PATH, pd.DataFrame(demo_rows), SONG_COLUMNS)
        return
    existing_ids = set(existing["track_id"].astype(str))
    existing_pairs = {
        (str(row.track_name).strip().lower(), str(row.artist_name).strip().lower())
        for row in existing.itertuples(index=False)
    }
    rows_to_add = [
        row
        for row in demo_rows
        if row["track_id"] not in existing_ids
        and (row["track_name"].lower(), row["artist_name"].lower()) not in existing_pairs
    ]
    if rows_to_add:
        combined = pd.concat([existing, pd.DataFrame(rows_to_add)], ignore_index=True)
        write_csv(SONGS_PATH, combined, SONG_COLUMNS)
    elif changed_existing:
        write_csv(SONGS_PATH, existing, SONG_COLUMNS)


def build_demo_songs() -> list[dict[str, object]]:
    required = [
        ("Shape of You", "Ed Sheeran", "Pop", "dance,romantic", 0.83, 0.65, 0.93, 96, 0.58, 0.00, 0.08, 0.09, 88),
        ("Blinding Lights", "The Weeknd", "Pop", "synth,dance", 0.51, 0.73, 0.33, 171, 0.00, 0.00, 0.06, 0.09, 92),
        ("Levitating", "Dua Lipa", "Pop", "dance,happy", 0.70, 0.82, 0.91, 103, 0.01, 0.00, 0.06, 0.07, 87),
        ("Uptown Funk", "Mark Ronson ft. Bruno Mars", "Pop", "funk,dance", 0.86, 0.61, 0.93, 115, 0.01, 0.00, 0.08, 0.03, 86),
        ("Can't Stop the Feeling", "Justin Timberlake", "Pop", "happy,dance", 0.67, 0.83, 0.70, 113, 0.01, 0.00, 0.07, 0.19, 84),
        ("Someone Like You", "Adele", "Ballad", "sad,piano", 0.56, 0.33, 0.28, 135, 0.89, 0.00, 0.03, 0.10, 86),
        ("All of Me", "John Legend", "Ballad", "romantic,piano", 0.42, 0.26, 0.33, 120, 0.92, 0.00, 0.03, 0.13, 85),
        ("Fix You", "Coldplay", "Ballad", "emotional,anthem", 0.21, 0.42, 0.12, 138, 0.16, 0.00, 0.03, 0.11, 82),
        ("Let Her Go", "Passenger", "Acoustic", "sad,folk", 0.51, 0.54, 0.24, 75, 0.66, 0.00, 0.04, 0.10, 81),
        ("Say Something", "A Great Big World", "Ballad", "sad,piano", 0.45, 0.15, 0.09, 138, 0.87, 0.00, 0.03, 0.09, 78),
        ("Believer", "Imagine Dragons", "Rock", "anthem,energy", 0.78, 0.78, 0.67, 125, 0.06, 0.00, 0.13, 0.08, 85),
        ("Numb", "Linkin Park", "Rock", "intense,anthem", 0.50, 0.86, 0.24, 110, 0.00, 0.00, 0.04, 0.64, 84),
        ("Mr. Brightside", "The Killers", "Rock", "indie,energy", 0.36, 0.91, 0.23, 148, 0.00, 0.00, 0.07, 0.10, 83),
        ("Seven Nation Army", "The White Stripes", "Rock", "garage,anthem", 0.74, 0.46, 0.32, 124, 0.01, 0.11, 0.08, 0.27, 82),
        ("Smells Like Teen Spirit", "Nirvana", "Rock", "grunge,intense", 0.50, 0.91, 0.53, 117, 0.00, 0.00, 0.06, 0.11, 86),
        ("Titanium", "David Guetta ft. Sia", "Electronic", "dance,anthem", 0.60, 0.79, 0.30, 126, 0.07, 0.00, 0.10, 0.13, 82),
        ("Wake Me Up", "Avicii", "Electronic", "dance,country", 0.53, 0.78, 0.64, 124, 0.00, 0.00, 0.05, 0.16, 84),
        ("Animals", "Martin Garrix", "Electronic", "festival,edm", 0.59, 0.90, 0.04, 128, 0.00, 0.74, 0.04, 0.07, 78),
        ("One More Time", "Daft Punk", "Electronic", "dance,classic", 0.61, 0.70, 0.48, 123, 0.02, 0.16, 0.13, 0.33, 80),
        ("Strobe", "Deadmau5", "Electronic", "progressive,instrumental", 0.49, 0.77, 0.08, 128, 0.00, 0.82, 0.04, 0.08, 74),
        ("God's Plan", "Drake", "Hip-hop", "rap,confident", 0.75, 0.45, 0.36, 77, 0.03, 0.00, 0.10, 0.55, 86),
        ("SICKO MODE", "Travis Scott", "Hip-hop", "rap,dark", 0.83, 0.73, 0.45, 155, 0.01, 0.00, 0.22, 0.12, 85),
        ("Lose Yourself", "Eminem", "Hip-hop", "rap,intense", 0.69, 0.74, 0.06, 171, 0.01, 0.00, 0.26, 0.36, 89),
        ("HUMBLE.", "Kendrick Lamar", "Hip-hop", "rap,confident", 0.91, 0.62, 0.42, 150, 0.00, 0.00, 0.10, 0.10, 86),
        ("Stronger", "Kanye West", "Hip-hop", "rap,electronic", 0.62, 0.72, 0.49, 104, 0.01, 0.00, 0.15, 0.41, 84),
    ]
    extra_titles = [
        ("Anti-Hero", "Taylor Swift", "Pop"), ("Bad Guy", "Billie Eilish", "Pop"), ("Watermelon Sugar", "Harry Styles", "Pop"),
        ("As It Was", "Harry Styles", "Pop"), ("Roar", "Katy Perry", "Pop"), ("Firework", "Katy Perry", "Pop"),
        ("Viva La Vida", "Coldplay", "Rock"), ("Thunder", "Imagine Dragons", "Rock"), ("Radioactive", "Imagine Dragons", "Rock"),
        ("Yellow", "Coldplay", "Rock"), ("The Pretender", "Foo Fighters", "Rock"), ("Boulevard of Broken Dreams", "Green Day", "Rock"),
        ("Clarity", "Zedd", "Electronic"), ("Levels", "Avicii", "Electronic"), ("Scary Monsters and Nice Sprites", "Skrillex", "Electronic"),
        ("Shelter", "Porter Robinson", "Electronic"), ("Midnight City", "M83", "Electronic"), ("Faded", "Alan Walker", "Electronic"),
        ("Sunflower", "Post Malone", "Hip-hop"), ("The Real Slim Shady", "Eminem", "Hip-hop"), ("DNA.", "Kendrick Lamar", "Hip-hop"),
        ("Hotline Bling", "Drake", "Hip-hop"), ("Mask Off", "Future", "Hip-hop"), ("Old Town Road", "Lil Nas X", "Hip-hop"),
        ("Hello", "Adele", "Ballad"), ("Perfect", "Ed Sheeran", "Ballad"), ("The Scientist", "Coldplay", "Ballad"),
        ("Stay With Me", "Sam Smith", "Ballad"), ("When I Was Your Man", "Bruno Mars", "Ballad"), ("Jar of Hearts", "Christina Perri", "Ballad"),
        ("Riptide", "Vance Joy", "Indie"), ("Ho Hey", "The Lumineers", "Indie"), ("Take Me to Church", "Hozier", "Indie"),
        ("Dog Days Are Over", "Florence + The Machine", "Indie"), ("Pumped Up Kicks", "Foster the People", "Indie"), ("Sweater Weather", "The Neighbourhood", "Indie"),
        ("No One", "Alicia Keys", "R&B"), ("Adorn", "Miguel", "R&B"), ("Thinking Bout You", "Frank Ocean", "R&B"),
        ("Earned It", "The Weeknd", "R&B"), ("Love on the Brain", "Rihanna", "R&B"), ("If I Ain't Got You", "Alicia Keys", "R&B"),
        ("Banana Pancakes", "Jack Johnson", "Acoustic"), ("Fast Car", "Tracy Chapman", "Acoustic"), ("Blackbird", "The Beatles", "Acoustic"),
        ("Skinny Love", "Bon Iver", "Acoustic"), ("Budapest", "George Ezra", "Acoustic"), ("Better Together", "Jack Johnson", "Acoustic"),
        ("Cruel Summer", "Taylor Swift", "Pop"), ("Bad Habits", "Ed Sheeran", "Pop"), ("Drivers License", "Olivia Rodrigo", "Pop"),
        ("Good 4 U", "Olivia Rodrigo", "Pop"), ("Flowers", "Miley Cyrus", "Pop"), ("Stay", "The Kid LAROI and Justin Bieber", "Pop"),
        ("About Damn Time", "Lizzo", "Pop"), ("Shivers", "Ed Sheeran", "Pop"), ("Save Your Tears", "The Weeknd", "Pop"),
        ("Heat Waves", "Glass Animals", "Pop"), ("Counting Stars", "OneRepublic", "Pop"), ("Havana", "Camila Cabello", "Pop"),
        ("Rolling in the Deep", "Adele", "Pop"), ("Chandelier", "Sia", "Pop"), ("Royals", "Lorde", "Pop"),
        ("Zombie", "The Cranberries", "Rock"), ("Wonderwall", "Oasis", "Rock"), ("Creep", "Radiohead", "Rock"),
        ("Use Somebody", "Kings of Leon", "Rock"), ("Everlong", "Foo Fighters", "Rock"), ("Sex on Fire", "Kings of Leon", "Rock"),
        ("Sweet Child O' Mine", "Guns N' Roses", "Rock"), ("Back in Black", "AC/DC", "Rock"), ("Dreams", "Fleetwood Mac", "Rock"),
        ("Enter Sandman", "Metallica", "Rock"), ("In the End", "Linkin Park", "Rock"), ("Do I Wanna Know?", "Arctic Monkeys", "Rock"),
        ("Get Lucky", "Daft Punk ft. Pharrell Williams", "Electronic"), ("The Nights", "Avicii", "Electronic"), ("Lean On", "Major Lazer and DJ Snake", "Electronic"),
        ("Rather Be", "Clean Bandit", "Electronic"), ("Don't You Worry Child", "Swedish House Mafia", "Electronic"), ("Turn Me On", "Riton and Oliver Heldens", "Electronic"),
        ("Sweet Nothing", "Calvin Harris ft. Florence Welch", "Electronic"), ("Summer", "Calvin Harris", "Electronic"), ("This Is What You Came For", "Calvin Harris ft. Rihanna", "Electronic"),
        ("Where Are U Now", "Skrillex and Diplo ft. Justin Bieber", "Electronic"), ("Ghosts 'n' Stuff", "Deadmau5", "Electronic"), ("Opus", "Eric Prydz", "Electronic"),
        ("Empire State of Mind", "Jay-Z ft. Alicia Keys", "Hip-hop"), ("All of the Lights", "Kanye West", "Hip-hop"), ("Alright", "Kendrick Lamar", "Hip-hop"),
        ("In Da Club", "50 Cent", "Hip-hop"), ("Ms. Jackson", "Outkast", "Hip-hop"), ("Juicy", "The Notorious B.I.G.", "Hip-hop"),
        ("N.Y. State of Mind", "Nas", "Hip-hop"), ("The Motto", "Drake", "Hip-hop"), ("Congratulations", "Post Malone", "Hip-hop"),
        ("XO Tour Llif3", "Lil Uzi Vert", "Hip-hop"), ("Money Trees", "Kendrick Lamar", "Hip-hop"), ("Lucid Dreams", "Juice WRLD", "Hip-hop"),
        ("Easy On Me", "Adele", "Ballad"), ("A Thousand Years", "Christina Perri", "Ballad"), ("Apologize", "OneRepublic", "Ballad"),
        ("I Will Always Love You", "Whitney Houston", "Ballad"), ("My Heart Will Go On", "Celine Dion", "Ballad"), ("Let It Be", "The Beatles", "Ballad"),
        ("Make You Feel My Love", "Adele", "Ballad"), ("Gravity", "John Mayer", "Ballad"), ("Iris", "Goo Goo Dolls", "Ballad"),
        ("Photograph", "Ed Sheeran", "Ballad"), ("Fix You", "Coldplay", "Ballad"), ("Say You Won't Let Go", "James Arthur", "Ballad"),
        ("Electric Feel", "MGMT", "Indie"), ("Little Talks", "Of Monsters and Men", "Indie"), ("1901", "Phoenix", "Indie"),
        ("Somebody Else", "The 1975", "Indie"), ("Dope on a Rope", "The Growlers", "Indie"), ("First Day of My Life", "Bright Eyes", "Indie"),
        ("New Slang", "The Shins", "Indie"), ("Sweet Disposition", "The Temper Trap", "Indie"), ("Young Folks", "Peter Bjorn and John", "Indie"),
        ("Home", "Edward Sharpe and the Magnetic Zeros", "Indie"), ("My Number", "Foals", "Indie"), ("Santeria", "Sublime", "Indie"),
        ("Blinding Lights", "The Weeknd", "R&B"), ("Good Days", "SZA", "R&B"), ("Supermodel", "SZA", "R&B"),
        ("Redbone", "Childish Gambino", "R&B"), ("Location", "Khalid", "R&B"), ("Boo'd Up", "Ella Mai", "R&B"),
        ("Crew", "GoldLink ft. Brent Faiyaz", "R&B"), ("Pyramids", "Frank Ocean", "R&B"), ("Pink + White", "Frank Ocean", "R&B"),
        ("Ordinary People", "John Legend", "R&B"), ("Fallin'", "Alicia Keys", "R&B"), ("Leave The Door Open", "Silk Sonic", "R&B"),
        ("Wonderwall", "Oasis", "Acoustic"), ("Landslide", "Fleetwood Mac", "Acoustic"), ("Tenerife Sea", "Ed Sheeran", "Acoustic"),
        ("The A Team", "Ed Sheeran", "Acoustic"), ("Heartbeats", "Jose Gonzalez", "Acoustic"), ("Holocene", "Bon Iver", "Acoustic"),
        ("To Build a Home", "The Cinematic Orchestra", "Acoustic"), ("Wagon Wheel", "Old Crow Medicine Show", "Acoustic"), ("I'm Yours", "Jason Mraz", "Acoustic"),
        ("Hey There Delilah", "Plain White T's", "Acoustic"), ("Free Fallin'", "Tom Petty", "Acoustic"), ("Tears in Heaven", "Eric Clapton", "Acoustic"),
    ]

    templates = {
        "Pop": (0.72, 0.70, 0.72, 112, 0.12, 0.01, 0.07, 0.12, "dance,happy"),
        "Rock": (0.48, 0.84, 0.46, 132, 0.04, 0.02, 0.06, 0.18, "guitar,anthem"),
        "Electronic": (0.68, 0.86, 0.45, 128, 0.03, 0.35, 0.06, 0.16, "dance,edm"),
        "Hip-hop": (0.79, 0.68, 0.48, 96, 0.05, 0.00, 0.22, 0.15, "rap,beat"),
        "Ballad": (0.42, 0.31, 0.28, 82, 0.78, 0.01, 0.04, 0.10, "piano,emotional"),
        "Indie": (0.58, 0.56, 0.55, 108, 0.34, 0.04, 0.05, 0.13, "indie,melodic"),
        "R&B": (0.65, 0.50, 0.52, 94, 0.28, 0.00, 0.09, 0.12, "soul,smooth"),
        "Acoustic": (0.52, 0.36, 0.50, 88, 0.82, 0.03, 0.04, 0.11, "folk,acoustic"),
    }

    rows: list[dict[str, object]] = []
    for item in required:
        rows.append(_demo_row(*item))
    for index, (title, artist, genre) in enumerate(extra_titles):
        base = templates[genre]
        offset = ((index % 5) - 2) * 0.025
        rows.append(
            _demo_row(
                title,
                artist,
                genre,
                base[8],
                max(0.05, min(0.95, base[0] + offset)),
                max(0.05, min(0.95, base[1] - offset)),
                max(0.05, min(0.95, base[2] + offset)),
                base[3] + (index % 7 - 3) * 3,
                max(0.0, min(0.98, base[4] - offset)),
                base[5],
                base[6],
                base[7],
                72 + (index % 20),
            )
        )

    return rows


def _demo_row(
    track_name: str,
    artist_name: str,
    genre: str,
    tags: str,
    danceability: float,
    energy: float,
    valence: float,
    tempo: float,
    acousticness: float,
    instrumentalness: float,
    speechiness: float,
    liveness: float,
    popularity: int,
) -> dict[str, object]:
    return {
        "track_id": stable_track_id(track_name, artist_name, "curated"),
        "track_name": track_name,
        "artist_name": artist_name,
        "album_name": "Curated Real Song Library",
        "genre": genre,
        "tags": tags,
        "danceability": round(danceability, 3),
        "energy": round(energy, 3),
        "valence": round(valence, 3),
        "tempo": round(float(tempo), 1),
        "acousticness": round(acousticness, 3),
        "instrumentalness": round(instrumentalness, 3),
        "speechiness": round(speechiness, 3),
        "liveness": round(liveness, 3),
        "popularity": int(popularity),
        "source": "curated",
        "external_url": "",
        "has_audio_features": True,
    }
