from __future__ import annotations

import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

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
from services.feature_engineering import build_item_feature_tokens, build_item_features_matrix

try:
    from lightfm import LightFM
    from lightfm.data import Dataset

    LIGHTFM_AVAILABLE = True
    LIGHTFM_IMPORT_ERROR = ""
except Exception as exc:
    LightFM = None
    Dataset = None
    LIGHTFM_AVAILABLE = False
    LIGHTFM_IMPORT_ERROR = f"{exc.__class__.__name__}: {exc}"


class RecommendationTrainer:
    def __init__(self, songs_path: Path = SONGS_PATH, interactions_path: Path = INTERACTIONS_PATH, model_path: Path = MODEL_PATH):
        self.songs_path = Path(songs_path)
        self.interactions_path = Path(interactions_path)
        self.model_path = Path(model_path)
        self.songs_df = pd.DataFrame()
        self.interactions_df = pd.DataFrame()
        self.feature_songs_df = pd.DataFrame()
        self.dataset = None
        self.interactions_matrix = None
        self.weights_matrix = None
        self.item_features_matrix = None
        self.item_feature_names: list[str] = []
        ensure_data_files()

    def load_data(self):
        self.songs_df = load_songs()
        self.interactions_df = load_interactions()
        self.feature_songs_df = self.songs_df[self.songs_df["has_audio_features"] == True].copy()
        return self.songs_df, self.interactions_df

    def build_dataset(self):
        if not LIGHTFM_AVAILABLE:
            return None
        if self.songs_df.empty:
            self.load_data()

        valid_item_ids = set(self.feature_songs_df["track_id"].astype(str))
        positive = self.interactions_df[
            (self.interactions_df["track_id"].astype(str).isin(valid_item_ids)) & (self.interactions_df["weight"] > 0)
        ].copy()
        users = sorted(positive["user_id"].astype(str).unique())
        items = sorted(self.feature_songs_df["track_id"].astype(str).unique())
        features = sorted({token for row in self.feature_songs_df.itertuples(index=False) for token in build_item_feature_tokens(row)})

        self.dataset = Dataset()
        self.dataset.fit(users=users, items=items, item_features=features)
        self.item_feature_names = features
        return self.dataset

    def build_interactions(self):
        if self.dataset is None:
            self.build_dataset()
        if self.dataset is None:
            return None, None

        valid_item_ids = set(self.feature_songs_df["track_id"].astype(str))
        positive = self.interactions_df[
            (self.interactions_df["track_id"].astype(str).isin(valid_item_ids)) & (self.interactions_df["weight"] > 0)
        ].copy()

        # LightFM WARP optimizes positive ranking examples. Dislikes are stored
        # as training data, then handled during re-ranking instead of as negative
        # matrix entries because WARP is not designed for negative weights.
        interactions = [
            (str(row.user_id), str(row.track_id), float(row.weight))
            for row in positive.itertuples(index=False)
        ]
        self.interactions_matrix, self.weights_matrix = self.dataset.build_interactions(interactions)
        return self.interactions_matrix, self.weights_matrix

    def build_item_features(self):
        if self.dataset is None:
            self.build_dataset()
        if self.dataset is None:
            return None
        self.item_features_matrix = build_item_features_matrix(self.feature_songs_df, self.dataset)
        return self.item_features_matrix

    def train_lightfm_model(self):
        self.load_data()
        status = self.get_training_status()
        if not LIGHTFM_AVAILABLE:
            status["message"] = f"LightFM is not available. Using fallback algorithm. {LIGHTFM_IMPORT_ERROR}"
            return status
        if status["num_users"] < 1 or status["num_interactions"] < 5 or status["num_items"] < 10:
            status["message"] = "Not enough data to train LightFM model. Using content-based baseline."
            return status

        self.build_dataset()
        self.build_interactions()
        self.build_item_features()
        model = LightFM(loss="warp", random_state=42)
        model.fit(
            self.interactions_matrix,
            item_features=self.item_features_matrix,
            sample_weight=self.weights_matrix,
            epochs=30,
            num_threads=1,
        )
        self.save_model(model)
        return self.get_training_status()

    def save_model(self, model: Any) -> None:
        user_id_map, _, item_id_map, _ = self.dataset.mapping()
        payload = {
            "model": model,
            "dataset": self.dataset,
            "user_id_map": user_id_map,
            "item_id_map": item_id_map,
            "item_feature_names": self.item_feature_names,
            "trained_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        }
        self.model_path.parent.mkdir(exist_ok=True)
        with self.model_path.open("wb") as handle:
            pickle.dump(payload, handle)

    def load_model(self) -> dict[str, Any] | None:
        if not self.model_path.exists():
            return None
        try:
            with self.model_path.open("rb") as handle:
                return pickle.load(handle)
        except Exception:
            return None

    def get_training_status(self) -> dict[str, Any]:
        if self.songs_df.empty:
            self.load_data()

        valid_items = set(self.feature_songs_df["track_id"].astype(str))
        usable_interactions = self.interactions_df[
            (self.interactions_df["track_id"].astype(str).isin(valid_items)) & (self.interactions_df["weight"] > 0)
        ]
        users = sorted(usable_interactions["user_id"].astype(str).unique())
        payload = self.load_model()
        is_trained = bool(payload and payload.get("model") is not None)
        feature_count = len(payload.get("item_feature_names", [])) if payload else 0
        message = "LightFM hybrid recommendation model is trained." if is_trained else "Model has not been trained yet."
        if not LIGHTFM_AVAILABLE:
            message = f"LightFM is not installed. Fallback recommender will be used. {LIGHTFM_IMPORT_ERROR}"

        return {
            "model_type": "LightFM WARP",
            "main_model": "LightFM Hybrid Recommendation Model",
            "lightfm_available": LIGHTFM_AVAILABLE,
            "is_trained": is_trained,
            "num_users": len(users),
            "num_items": int(self.feature_songs_df.shape[0]),
            "num_interactions": int(usable_interactions.shape[0]),
            "num_item_features": int(feature_count),
            "last_trained_at": payload.get("trained_at") if payload else "",
            "message": message,
        }
