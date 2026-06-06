"""Content-based music recommendation system.

This module turns song features into simple vectors, builds a user profile from
liked songs, and recommends songs with the highest cosine similarity.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus


DATA_PATH = Path(__file__).with_name("songs.csv")
EXTRA_DATA_PATH = Path(__file__).with_name("catalog_extra.csv")
ONLINE_SEED_PATH = Path(__file__).with_name("online_seed_catalog.csv")

FEATURE_WEIGHTS = {
    "artist": 0.75,
    "genre": 2.4,
    "mood": 2.1,
    "tempo": 0.9,
    "energy": 1.05,
}

TEMPO_SCORE = {
    "Slow": 0.0,
    "Medium": 0.5,
    "Fast": 1.0,
}

ENERGY_SCORE = {
    "Low": 0.0,
    "Medium": 0.5,
    "High": 1.0,
}


@dataclass(frozen=True)
class Song:
    song: str
    artist: str
    genre: str
    mood: str
    tempo: str
    energy: str

    @property
    def display_name(self) -> str:
        return f"{self.song} - {self.artist}"


def load_songs(path: Path = DATA_PATH) -> list[Song]:
    """Load songs from the base CSV and optional expanded catalogue."""
    songs: list[Song] = []
    seen: set[tuple[str, str]] = set()

    for source in [path, EXTRA_DATA_PATH, ONLINE_SEED_PATH]:
        if not source.exists():
            continue

        with source.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                key = (row["song"].strip().lower(), row["artist"].strip().lower())
                if key in seen:
                    continue
                seen.add(key)
                songs.append(
                    Song(
                        song=row["song"].strip(),
                        artist=row["artist"].strip(),
                        genre=row["genre"].strip(),
                        mood=row["mood"].strip(),
                        tempo=row["tempo"].strip(),
                        energy=row["energy"].strip(),
                    )
                )

    return songs


def canonical_title(title: str) -> str:
    """Normalize a song title so covers/remixes/live versions collapse together."""
    title = title.lower()
    title = re.sub(r"\([^)]*\)|（[^）]*）|\[[^\]]*\]|【[^】]*】", "", title)
    title = re.sub(
        r"(remix|live|cover|version|伴奏|翻唱|现场|柔情版|新版|旧版|抖音版|dj版|合唱版|"
        r"纯享版|完整版|片段|剪辑|加速版|降调版|升调版|伴奏版|demo|ost|主题曲|插曲)",
        "",
        title,
    )
    title = re.sub(r"[\s\-–—_|·,，.。:：/\\!！?？'\"“”‘’]+", "", title)
    return title.strip()


def build_feature_space(songs: list[Song]) -> list[str]:
    """Create stable feature names for one-hot categorical encoding."""
    artists = sorted({song.artist for song in songs})
    genres = sorted({song.genre for song in songs})
    moods = sorted({song.mood for song in songs})
    return [f"artist:{artist}" for artist in artists] + [f"genre:{genre}" for genre in genres] + [f"mood:{mood}" for mood in moods] + [
        "tempo",
        "energy",
    ]


def vectorize(song: Song, feature_space: list[str]) -> list[float]:
    """Convert one song into a numeric feature vector."""
    values = []
    for feature in feature_space:
        if feature.startswith("artist:"):
            values.append(FEATURE_WEIGHTS["artist"] if song.artist == feature.removeprefix("artist:") else 0.0)
        elif feature.startswith("genre:"):
            values.append(FEATURE_WEIGHTS["genre"] if song.genre == feature.removeprefix("genre:") else 0.0)
        elif feature.startswith("mood:"):
            values.append(FEATURE_WEIGHTS["mood"] if song.mood == feature.removeprefix("mood:") else 0.0)
        elif feature == "tempo":
            values.append(TEMPO_SCORE[song.tempo] * FEATURE_WEIGHTS["tempo"])
        elif feature == "energy":
            values.append(ENERGY_SCORE[song.energy] * FEATURE_WEIGHTS["energy"])
        else:
            raise ValueError(f"Unknown feature: {feature}")
    return values


def average_vectors(vectors: list[list[float]]) -> list[float]:
    """Average multiple song vectors to create a user profile."""
    if not vectors:
        raise ValueError("At least one liked song is required.")

    return [sum(values) / len(values) for values in zip(*vectors)]


def weighted_average_vectors(vectors: list[list[float]]) -> list[float]:
    """Average vectors while giving newer quiz answers slightly more influence."""
    if not vectors:
        raise ValueError("At least one liked song is required.")

    weights = [1 + index * 0.13 for index in range(len(vectors))]
    total_weight = sum(weights)
    averaged = []
    for column in zip(*vectors):
        averaged.append(sum(value * weight for value, weight in zip(column, weights)) / total_weight)
    return averaged


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Measure how similar two vectors are."""
    dot_product = sum(a * b for a, b in zip(left, right))
    left_length = math.sqrt(sum(a * a for a in left))
    right_length = math.sqrt(sum(b * b for b in right))

    if left_length == 0 or right_length == 0:
        return 0.0
    return dot_product / (left_length * right_length)


def explain_recommendation(song: Song, liked_songs: list[Song]) -> str:
    """Explain the recommendation using matching human-readable features."""
    shared_features = []
    if any(liked.genre == song.genre for liked in liked_songs):
        shared_features.append(f"genre: {song.genre}")
    if any(liked.mood == song.mood for liked in liked_songs):
        shared_features.append(f"mood: {song.mood}")
    if any(liked.tempo == song.tempo for liked in liked_songs):
        shared_features.append(f"tempo: {song.tempo}")
    if any(liked.energy == song.energy for liked in liked_songs):
        shared_features.append(f"energy: {song.energy}")

    if not shared_features:
        return "It has a balanced feature profile close to your selected songs."
    return "Similar " + ", ".join(shared_features) + "."


def build_user_profile(liked_songs: list[Song]) -> dict[str, object]:
    """Summarize the user's listening taste from selected songs."""
    if not liked_songs:
        raise ValueError("At least one liked song is required.")

    genre_counts = Counter(song.genre for song in liked_songs)
    mood_counts = Counter(song.mood for song in liked_songs)
    tempo_counts = Counter(song.tempo for song in liked_songs)
    energy_counts = Counter(song.energy for song in liked_songs)
    artist_counts = Counter(song.artist for song in liked_songs)

    return {
        "genres": genre_counts.most_common(3),
        "moods": mood_counts.most_common(3),
        "artists": artist_counts.most_common(3),
        "tempo": tempo_counts.most_common(1)[0][0],
        "energy": energy_counts.most_common(1)[0][0],
        "song_count": len(liked_songs),
    }


def music_links(song: str, artist: str) -> dict[str, str]:
    """Create search links for platforms that may not expose public track URLs."""
    query = quote_plus(f"{song} {artist}")
    return {
        "qq_music": f"https://y.qq.com/n/ryqq/search?w={query}",
        "netease": f"https://music.163.com/#/search/m/?s={query}&type=1",
        "kugou": f"https://www.kugou.com/yy/html/search.html#searchType=song&searchKeyWord={query}",
        "kuwo": f"https://www.kuwo.cn/search/list?key={query}",
        "migu": f"https://music.migu.cn/v3/search?keyword={query}",
        "bilibili": f"https://search.bilibili.com/all?keyword={query}",
        "youtube": f"https://www.youtube.com/results?search_query={query}",
    }


def feature_overlap_score(song: Song, liked_songs: list[Song]) -> float:
    """Add a small preference boost based on repeated user choices."""
    liked_count = len(liked_songs)
    genre_ratio = sum(liked.genre == song.genre for liked in liked_songs) / liked_count
    mood_ratio = sum(liked.mood == song.mood for liked in liked_songs) / liked_count
    artist_ratio = sum(liked.artist == song.artist for liked in liked_songs) / liked_count
    tempo_ratio = sum(liked.tempo == song.tempo for liked in liked_songs) / liked_count
    energy_ratio = sum(liked.energy == song.energy for liked in liked_songs) / liked_count
    return (
        genre_ratio * 0.08
        + mood_ratio * 0.07
        + artist_ratio * 0.05
        + tempo_ratio * 0.025
        + energy_ratio * 0.025
    )


def novelty_penalty(song: Song, liked_songs: list[Song]) -> float:
    """Penalize same-work variants and over-repeated artists."""
    title = canonical_title(song.song)
    liked_titles = {canonical_title(liked.song) for liked in liked_songs}
    artist_counts = Counter(liked.artist for liked in liked_songs)

    penalty = 0.0
    if title in liked_titles:
        penalty += 0.55
    if any(title and (title in canonical_title(liked.song) or canonical_title(liked.song) in title) for liked in liked_songs):
        penalty += 0.25
    if artist_counts[song.artist] >= 3:
        penalty += 0.10
    elif artist_counts[song.artist] >= 1:
        penalty += 0.04
    return penalty


def diversify_ranked_items(items: list[dict[str, object]], top_n: int) -> list[dict[str, object]]:
    """Keep recommendations relevant while reducing repeated artists."""
    selected: list[dict[str, object]] = []
    remaining = items[:]
    used_titles: set[str] = set()

    while remaining and len(selected) < top_n:
        best_item = None
        best_score = -1.0

        for item in remaining:
            if str(item["canonical_title"]) in used_titles:
                continue
            same_artist = sum(existing["artist"] == item["artist"] for existing in selected)
            same_genre = sum(existing["genre"] == item["genre"] for existing in selected)
            same_title = sum(existing["canonical_title"] == item["canonical_title"] for existing in selected)
            adjusted = (
                float(item["raw_score"])
                - same_artist * 0.075
                - same_genre * 0.006
                - same_title * 0.65
            )
            if adjusted > best_score:
                best_score = adjusted
                best_item = item

        if best_item is None:
            break
        selected.append(best_item)
        used_titles.add(str(best_item["canonical_title"]))
        remaining.remove(best_item)

    return selected


def rank_recommendations(
    liked_songs: list[Song],
    songs: list[Song] | None = None,
    top_n: int = 10,
) -> list[dict[str, object]]:
    """Rank recommendations from already-loaded liked Song objects."""
    songs = songs or load_songs()
    feature_space = build_feature_space(songs)
    liked_vectors = [vectorize(song, feature_space) for song in liked_songs]
    user_profile = weighted_average_vectors(liked_vectors)
    liked_names = {song.song for song in liked_songs}
    liked_titles = {canonical_title(song.song) for song in liked_songs}

    recommendations = []
    for song in songs:
        canonical = canonical_title(song.song)
        if song.song in liked_names or canonical in liked_titles:
            continue

        score = cosine_similarity(user_profile, vectorize(song, feature_space))
        raw_score = max(min(score + feature_overlap_score(song, liked_songs) - novelty_penalty(song, liked_songs), 1.0), 0.0)
        links = music_links(song.song, song.artist)
        recommendations.append(
            {
                "song": song.song,
                "artist": song.artist,
                "genre": song.genre,
                "mood": song.mood,
                "tempo": song.tempo,
                "energy": song.energy,
                "similarity": round(raw_score * 100, 1),
                "raw_score": raw_score,
                "canonical_title": canonical,
                "reason": explain_recommendation(song, liked_songs),
                "qq_music": links["qq_music"],
                "netease": links["netease"],
                "kugou": links["kugou"],
                "kuwo": links["kuwo"],
                "migu": links["migu"],
                "bilibili": links["bilibili"],
                "youtube": links["youtube"],
            }
        )

    sorted_items = sorted(recommendations, key=lambda item: item["raw_score"], reverse=True)
    return diversify_ranked_items(sorted_items, top_n)


def recommend_songs(
    liked_song_names: list[str],
    songs: list[Song] | None = None,
    top_n: int = 5,
) -> list[dict[str, object]]:
    """Recommend songs based on the user's selected favorite songs."""
    songs = songs or load_songs()
    songs_by_name = {song.song.lower(): song for song in songs}
    liked_songs = []

    for name in liked_song_names:
        song = songs_by_name.get(name.lower())
        if song is None:
            available = ", ".join(sorted(song.song for song in songs))
            raise ValueError(f"Song not found: {name}. Available songs: {available}")
        liked_songs.append(song)

    return rank_recommendations(liked_songs, songs=songs, top_n=top_n)


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend songs from songs.csv.")
    parser.add_argument("liked_songs", nargs="+", help="Songs the user likes")
    parser.add_argument("--top", type=int, default=5, help="Number of recommendations")
    args = parser.parse_args()

    recommendations = recommend_songs(args.liked_songs, top_n=args.top)
    print("Recommended songs:")
    for index, item in enumerate(recommendations, start=1):
        print(
            f"{index}. {item['song']} by {item['artist']} "
            f"({item['similarity']}% match) - {item['reason']}"
        )


if __name__ == "__main__":
    main()
