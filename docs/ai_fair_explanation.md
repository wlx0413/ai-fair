# AI Music Recommendation System

## 1. Problem

Many music apps recommend songs, but the process can feel like a black box. This project shows a simple version of how a recommendation system can learn from playlist data and feedback.

## 2. Dataset

The dataset contains songs, artists, genres, tags, and audio-style features such as danceability, energy, valence, tempo, acousticness, speechiness, liveness, and popularity.

## 3. Playlist Import

Playlist import creates implicit feedback. If a user imports a playlist, the system treats those songs as examples of music the user may like.

## 4. Feature Engineering

Each song is converted into item features. These include genre, artist, tags, source, and buckets such as high energy, fast tempo, sad mood, or danceable rhythm.

## 5. User-Item Interaction Matrix

The system creates a matrix where rows are users and columns are songs. Playlist imports, manual adds, Likes, and Dislikes become training signals.

## 6. Item Features

Item features describe each song. LightFM can use these features to recommend songs even when the user has not interacted with every song.

## 7. Model Training

The project trains a LightFM hybrid recommendation model with WARP ranking loss. The model learns which songs are more likely to match the user's taste.

## 8. Recommendation Ranking

The system predicts scores for candidate songs. It combines the LightFM learned score with content similarity from audio features, then returns the Top 10 songs.

## 9. Feedback Learning

Like and Dislike create explicit feedback. Feedback is saved as new training data and can be used to retrain the model, improving future recommendations.

## 10. Limitations

Free music APIs usually provide metadata, not full audio features. The demo dataset uses realistic simplified feature values for AI Fair presentation.

## 11. Future Improvements

Future versions could use a larger licensed dataset, add evaluation metrics, support multiple users, and improve matching between online metadata and local audio features.
