from __future__ import annotations

import pickle
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from services.data_store import (
    AUDIO_FEATURE_COLUMNS,
    INTERACTIONS_PATH,
    MODEL_PATH,
    SONGS_PATH,
    ensure_data_files,
    load_interactions,
    load_songs,
)

try:
    from sklearn.linear_model import LogisticRegression

    SKLEARN_AVAILABLE = True
except Exception:
    LogisticRegression = None
    SKLEARN_AVAILABLE = False


class HybridMusicRecommender:
    def __init__(self, songs_path: Path = SONGS_PATH, interactions_path: Path = INTERACTIONS_PATH, model_path: Path = MODEL_PATH):
        self.songs_path = Path(songs_path)
        self.interactions_path = Path(interactions_path)
        self.model_path = Path(model_path)
        ensure_data_files()

    def recommend_for_user(self, user_id: str = "demo_user", top_n: int = 10) -> list[dict[str, Any]]:
        model_payload = self._load_model()
        if model_payload:
            lightfm_scores = self.recommend_lightfm(user_id, top_n=max(top_n * 4, 30))
            content_scores = self._content_score_map(user_id)
            ranked = self.rerank_recommendations(lightfm_scores, content_scores)
            return ranked[:top_n]
        return self.recommend_content_based(user_id, top_n=top_n)

    def daily_recommendations(self, user_id: str = "demo_user", top_n: int = 50) -> list[dict[str, Any]]:
        model_payload = self._load_model()
        if model_payload:
            lightfm_scores = self.recommend_lightfm(user_id, top_n=max(top_n * 5, 160))
            content_scores = self._content_score_map(user_id)
            ranked = self.rerank_recommendations(lightfm_scores, content_scores)
        else:
            ranked = self.recommend_content_based(user_id, top_n=max(top_n * 4, 120))
        return self._diversify(ranked, top_n=top_n)

    def recommend_content_based(self, user_id: str, top_n: int = 10) -> list[dict[str, Any]]:
        songs = self._candidate_songs()
        excluded = self._excluded_track_ids(user_id)
        content_scores = self._content_score_map(user_id)
        logistic_scores = self._logistic_feedback_scores(user_id)
        user_profile = self.get_user_taste_profile(user_id)

        rows = []
        for row in songs.itertuples(index=False):
            track_id = str(row.track_id)
            if track_id in excluded:
                continue
            content_score = float(content_scores.get(track_id, 0.0))
            logistic_score = float(logistic_scores.get(track_id, 0.0))
            # Fallback ranking still uses a trained LogisticRegression feedback
            # model when possible, while content similarity handles cold start.
            final_score = 0.6 * content_score + 0.4 * logistic_score
            rows.append(self._result_row(row._asdict(), final_score, content_score, logistic_score, "Logistic Regression Fallback" if logistic_scores else "Content-Based Baseline", user_profile))

        if not rows:
            rows = self._popular_fallback_rows(songs, excluded, user_profile)
        return sorted(rows, key=lambda item: item["score"], reverse=True)[:top_n]

    def recommend_lightfm(self, user_id: str, top_n: int = 10) -> list[dict[str, Any]]:
        payload = self._load_model()
        if not payload:
            return []
        songs = self._candidate_songs()
        excluded = self._excluded_track_ids(user_id)
        user_id_map = payload.get("user_id_map", {})
        item_id_map = payload.get("item_id_map", {})
        if user_id not in user_id_map:
            return []

        candidates = [track_id for track_id in songs["track_id"].astype(str) if track_id in item_id_map and track_id not in excluded]
        if not candidates:
            return []
        internal_user_id = user_id_map[user_id]
        internal_item_ids = np.array([item_id_map[track_id] for track_id in candidates], dtype=np.int32)
        try:
            raw_scores = payload["model"].predict(internal_user_id, internal_item_ids)
        except Exception:
            return []
        normalized_scores = self._normalize_scores(raw_scores)
        score_by_track = dict(zip(candidates, normalized_scores))
        user_profile = self.get_user_taste_profile(user_id)
        rows = []
        by_id = songs.set_index("track_id").to_dict("index")
        for track_id, model_score in score_by_track.items():
            row = by_id[track_id]
            row["track_id"] = track_id
            rows.append(self._result_row(row, float(model_score), 0.0, float(model_score), "LightFM Hybrid Model", user_profile))
        return sorted(rows, key=lambda item: item["score"], reverse=True)[:top_n]

    def rerank_recommendations(self, lightfm_scores: list[dict[str, Any]], content_scores: dict[str, float]) -> list[dict[str, Any]]:
        user_profile = self.get_user_taste_profile("demo_user")
        reranked = []
        disliked = self._disliked_track_ids("demo_user")
        for item in lightfm_scores:
            track_id = str(item["track_id"])
            model_score = float(item.get("model_score", item.get("score", 0.0)))
            content_score = float(content_scores.get(track_id, 0.0))
            # model_score is the learned user preference score from LightFM.
            # content_score is the audio-feature similarity to the user's songs.
            # final_score blends trained ranking with content similarity.
            final_score = 0.7 * model_score + 0.3 * content_score
            if track_id in disliked:
                final_score -= 0.35
            item["score"] = round(float(final_score), 4)
            item["content_score"] = round(content_score, 4)
            item["model_score"] = round(model_score, 4)
            item["algorithm_used"] = "LightFM Hybrid Model"
            item["reason"] = self.generate_reason(item, user_profile)
            item["features_matched"] = self._matched_features(item, user_profile)
            reranked.append(item)
        return sorted(reranked, key=lambda row: row["score"], reverse=True)

    def _diversify(self, ranked: list[dict[str, Any]], top_n: int = 50) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        artist_counts: Counter[str] = Counter()
        genre_counts: Counter[str] = Counter()
        seen_titles: set[tuple[str, str]] = set()

        def key_for(item: dict[str, Any]) -> tuple[str, str]:
            return (str(item.get("track_name", "")).strip().lower(), str(item.get("artist_name", "")).strip().lower())

        for pass_index in range(3):
            for item in ranked:
                key = key_for(item)
                if key in seen_titles:
                    continue
                artist = str(item.get("artist_name", ""))
                genre = str(item.get("genre", ""))
                if pass_index == 0 and (artist_counts[artist] >= 2 or genre_counts[genre] >= 14):
                    continue
                if pass_index == 1 and (artist_counts[artist] >= 3 or genre_counts[genre] >= 20):
                    continue
                selected.append({**item, "rank": len(selected) + 1})
                seen_titles.add(key)
                artist_counts[artist] += 1
                genre_counts[genre] += 1
                if len(selected) >= top_n:
                    return selected
        return selected

    def generate_reason(self, song_row: dict[str, Any], user_profile: dict[str, Any]) -> str:
        matched = self._matched_features(song_row, user_profile)
        if matched:
            return f"This song is recommended because it shares {', '.join(matched[:3])} with your playlist."
        return "This song is recommended because its audio feature profile is close to your imported playlist."

    def get_user_taste_profile(self, user_id: str) -> dict[str, Any]:
        songs = load_songs()
        interactions = load_interactions()
        user_interactions = interactions[(interactions["user_id"].astype(str) == user_id) & (interactions["weight"] > 0)]
        liked_ids = set(user_interactions["track_id"].astype(str))
        liked = songs[songs["track_id"].astype(str).isin(liked_ids)]
        if liked.empty:
            return {
                "summary": "No playlist data yet. Add songs or import a playlist to build a taste profile.",
                "favorite_genres": [],
                "main_artists": [],
                "energy_level": "Unknown",
                "danceability": "Unknown",
                "mood": "Unknown",
                "tempo": "Unknown",
            }
        genres = Counter(liked["genre"].astype(str)).most_common(4)
        artists = Counter(liked["artist_name"].astype(str)).most_common(4)
        avg = liked[AUDIO_FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce").mean()
        profile = {
            "favorite_genres": [item[0] for item in genres],
            "main_artists": [item[0] for item in artists],
            "energy_level": "High Energy" if avg["energy"] >= 0.65 else "Low Energy" if avg["energy"] <= 0.4 else "Medium Energy",
            "danceability": "Danceable" if avg["danceability"] >= 0.65 else "Less Danceable",
            "mood": "Positive Mood" if avg["valence"] >= 0.65 else "Sad Mood" if avg["valence"] <= 0.4 else "Neutral Mood",
            "tempo": "Fast Tempo" if avg["tempo"] >= 125 else "Slow Tempo" if avg["tempo"] <= 90 else "Medium Tempo",
        }
        profile["summary"] = f"Your profile leans toward {profile['energy_level']}, {profile['tempo']}, and {', '.join(profile['favorite_genres'][:2]) or 'mixed genres'}."
        return profile

    def _candidate_songs(self) -> pd.DataFrame:
        songs = load_songs()
        title_text = songs["track_name"].astype(str)
        artist_text = songs["artist_name"].astype(str)
        real_songs = songs[
            ~title_text.str.match(r"^Demo .+ Track \d+$", case=False, na=False)
            & ~artist_text.str.match(r"^AI Fair Artist \d+$", case=False, na=False)
        ].copy()
        real_songs = real_songs.drop_duplicates(subset=["track_id"], keep="first")
        return real_songs[real_songs["has_audio_features"] == True].copy()

    def _load_model(self) -> dict[str, Any] | None:
        if not self.model_path.exists():
            return None
        try:
            with self.model_path.open("rb") as handle:
                payload = pickle.load(handle)
            return payload if payload.get("model") is not None else None
        except Exception:
            return None

    def _excluded_track_ids(self, user_id: str) -> set[str]:
        interactions = load_interactions()
        user_rows = interactions[interactions["user_id"].astype(str) == user_id]
        return set(user_rows["track_id"].astype(str))

    def _disliked_track_ids(self, user_id: str) -> set[str]:
        interactions = load_interactions()
        rows = interactions[(interactions["user_id"].astype(str) == user_id) & (interactions["interaction_type"].astype(str) == "dislike")]
        return set(rows["track_id"].astype(str))

    def _content_score_map(self, user_id: str) -> dict[str, float]:
        songs = self._candidate_songs()
        if songs.empty:
            return {}
        interactions = load_interactions()
        positive_ids = set(
            interactions[(interactions["user_id"].astype(str) == user_id) & (interactions["weight"] > 0)]["track_id"].astype(str)
        )
        feature_matrix = songs[AUDIO_FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float)
        normalized = self._standardize(feature_matrix)
        if positive_ids:
            mask = songs["track_id"].astype(str).isin(positive_ids).to_numpy()
            if mask.any():
                profile = normalized[mask].mean(axis=0)
            else:
                profile = normalized.mean(axis=0)
        else:
            popularity_index = AUDIO_FEATURE_COLUMNS.index("popularity")
            top = np.argsort(feature_matrix[:, popularity_index])[-8:]
            profile = normalized[top].mean(axis=0)
        profile_norm = np.linalg.norm(profile)
        item_norms = np.linalg.norm(normalized, axis=1)
        denom = np.where(item_norms * profile_norm == 0, 1.0, item_norms * profile_norm)
        cosine = np.dot(normalized, profile) / denom
        cosine = (cosine + 1.0) / 2.0
        return dict(zip(songs["track_id"].astype(str), cosine.astype(float)))

    def _logistic_feedback_scores(self, user_id: str) -> dict[str, float]:
        if not SKLEARN_AVAILABLE:
            return {}
        songs = self._candidate_songs()
        interactions = load_interactions()
        labeled = interactions[
            (interactions["user_id"].astype(str) == user_id)
            & (interactions["interaction_type"].astype(str).isin(["like", "dislike"]))
        ].copy()
        if labeled.empty or labeled["interaction_type"].nunique() < 2:
            return {}
        train = songs.merge(labeled[["track_id", "interaction_type"]], on="track_id", how="inner")
        if train.shape[0] < 4 or train["interaction_type"].nunique() < 2:
            return {}
        x_train = train[AUDIO_FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float)
        y_train = (train["interaction_type"] == "like").astype(int).to_numpy()
        x_all = songs[AUDIO_FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(dtype=float)
        try:
            model = LogisticRegression(max_iter=1000)
            model.fit(self._standardize(x_train), y_train)
            probs = model.predict_proba(self._standardize(x_all))[:, 1]
        except Exception:
            return {}
        return dict(zip(songs["track_id"].astype(str), probs.astype(float)))

    def _popular_fallback_rows(self, songs: pd.DataFrame, excluded: set[str], user_profile: dict[str, Any]) -> list[dict[str, Any]]:
        rows = []
        for row in songs.sort_values("popularity", ascending=False).head(20).itertuples(index=False):
            if str(row.track_id) in excluded:
                continue
            rows.append(self._result_row(row._asdict(), float(row.popularity) / 100, 0.0, 0.0, "Content-Based Baseline", user_profile))
        return rows

    def _result_row(self, row: dict[str, Any], score: float, content_score: float, model_score: float, algorithm: str, user_profile: dict[str, Any]) -> dict[str, Any]:
        item = {
            "track_id": str(row.get("track_id", "")),
            "track_name": row.get("track_name", ""),
            "artist_name": row.get("artist_name", ""),
            "album_name": row.get("album_name", ""),
            "genre": row.get("genre", ""),
            "score": round(float(score), 4),
            "content_score": round(float(content_score), 4),
            "model_score": round(float(model_score), 4),
            "algorithm_used": algorithm,
        }
        item["features_matched"] = self._matched_features({**row, **item}, user_profile)
        item["reason"] = self.generate_reason({**row, **item}, user_profile)
        return item

    def _matched_features(self, song_row: dict[str, Any], user_profile: dict[str, Any]) -> list[str]:
        matched = []
        genre = str(song_row.get("genre", ""))
        if genre and genre in user_profile.get("favorite_genres", []):
            matched.append(f"{genre} genre")
        try:
            if float(song_row.get("energy", 0)) >= 0.7 and "High" in user_profile.get("energy_level", ""):
                matched.append("high energy")
            if float(song_row.get("tempo", 0)) >= 125 and "Fast" in user_profile.get("tempo", ""):
                matched.append("fast tempo")
            if float(song_row.get("danceability", 0)) >= 0.7 and "Danceable" in user_profile.get("danceability", ""):
                matched.append("danceable rhythm")
            if float(song_row.get("valence", 0)) <= 0.4 and "Sad" in user_profile.get("mood", ""):
                matched.append("sad mood")
            if float(song_row.get("valence", 0)) >= 0.65 and "Positive" in user_profile.get("mood", ""):
                matched.append("positive mood")
        except Exception:
            pass
        return matched

    def _standardize(self, matrix: np.ndarray) -> np.ndarray:
        mean = matrix.mean(axis=0)
        std = matrix.std(axis=0)
        std = np.where(std == 0, 1.0, std)
        return (matrix - mean) / std

    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        if scores.size == 0:
            return scores
        low = float(np.min(scores))
        high = float(np.max(scores))
        if high == low:
            return np.ones_like(scores) * 0.5
        return (scores - low) / (high - low)
