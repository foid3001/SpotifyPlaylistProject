from dotenv import load_dotenv
import spotify_functions as sf
import os

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
playlist_id = "3cEYpjA9oz9GiPac4AsH4n"

access_token = sf.get_token(CLIENT_ID, CLIENT_SECRET)
track_ids = sf.get_playlist_track_ids(playlist_id, access_token)

id_string = "".join([f"{id}," for id in track_ids])[:-1]
audio_features = sf.get_audio_features(id_string,access_token)
average_attributes = sf.average_audio_features(audio_features)

genre_seeds = sf.get_playlist_genre_seeds(access_token)["genres"]
print(genre_seeds)
recommendations = sf.get_recommendations(access_token, average_attributes, genre_seeds)
rec_ids = sf.get_recommendation_ids(recommendations)

print(rec_ids)