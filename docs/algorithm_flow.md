# Algorithm Flow

User imports QQ Music playlist or manually adds songs

↓

System saves songs and playlist interactions

↓

System builds item features from genre, artist, tags and audio feature buckets

↓

System creates user-item interaction matrix

↓

LightFM trains a hybrid recommendation model

↓

Model predicts scores for candidate songs

↓

System ranks songs and shows recommendations

↓

User clicks Like or Dislike

↓

Feedback is saved as new training data

↓

Model retrains and improves recommendations
