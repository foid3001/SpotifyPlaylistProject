import requests

def get_token(client_id: str, client_secret: str) -> str:
    token_url = "https://accounts.spotify.com/api/token"

    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }

    auth_response = requests.post(token_url,data=data).json()

    return auth_response["access_token"]

def get_playlist_track_ids(playlist_id: str, access_token: str) -> list:
    field_string = "tracks.items.track.id"
    playlist_endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}?fields={field_string}"

    header = {"Authorization": f"Bearer {access_token}"}

    playlist_request = requests.get(playlist_endpoint, headers=header)

    track_ids = playlist_request.json()["tracks"]["items"]

    track_id_list = []
    for track in track_ids:
        track_id = track["track"]["id"]
        track_id_list.append(track_id)

    return track_id_list

def get_audio_features(track_ids: str, access_token: str) -> dict:
    audio_features_endpoint = f"https://api.spotify.com/v1/audio-features?ids={track_ids}"
    header = {"Authorization": f"Bearer {access_token}"}

    audio_features = requests.get(audio_features_endpoint,headers=header).json()["audio_features"]

    return audio_features

def average_audio_features(audio_features: dict) -> dict:
    averages = {}
    
    for track in audio_features:
        for attribute, value in track.items():
            if isinstance(value, (int, float)):
                if attribute not in averages:
                    averages[attribute] = value/len(audio_features)
                elif attribute in averages:
                    averages[attribute] += value/len(audio_features)

    return averages

def get_playlist_genre_seeds(access_token: str) -> dict:
    genre_seed_endpoint = "https://api.spotify.com/v1/recommendations/available-genre-seeds"
    header = {"Authorization": f"Bearer {access_token}"}
    genre_seeds = requests.get(genre_seed_endpoint, headers=header).json()
    return genre_seeds

def get_attribute_min_maxes(averages: dict) -> dict:
    attributes = [
        "acousticness", "danceability", "energy", "instrumentalness",
        "key", "liveness", "loudness", "mode",
        "speechiness", "tempo", "time_signature", "valence"
    ]

    min_maxes = {}
    min_multiplier = 0.5
    max_multiplier = 1.5
    for i, attribute in enumerate(attributes):
        problems = ["key", "mode", "time_signature"]
        val = averages[attribute]
        max = round(max_multiplier*val, 3)
        min = round(min_multiplier*val, 3)
        if attribute == "loudness":
            min_maxes[f"min_{attribute}"] = int(max)
            min_maxes[f"max_{attribute}"] = int(min)
            min_maxes[f"target_{attribute}"] = int(val)
        else:
            min_maxes[f"min_{attribute}"] = int(min) if attribute in problems else min
            min_maxes[f"max_{attribute}"] = int(max) if attribute in problems else max
            min_maxes[f"target_{attribute}"] = int(val) if attribute in problems else val

    return min_maxes

def batch(genres: list[str], batch_size: int) -> list[list]:
    batches = []
    current_batch = []
    for genre in genres:
        current_batch.append(genre)
        if len(current_batch) == batch_size:
            batches.append(current_batch)
            current_batch = []
        if genre == genres[-1]:
            batches.append(current_batch)
    return batches
    
def get_recommendations(access_token: str, averages: dict, genres: list) -> list:
    get_recs_endpoint = "https://api.spotify.com/v1/recommendations"
    header = {"Authorization": f"Bearer {access_token}"}
    rec_query = get_attribute_min_maxes(averages)

    recommendation_list = []
    
    genre_batches = batch(genres, 5)
    for genre_batch in genre_batches:
        rec_query.update({"seed_genres":genre_batch})
        recommendations = requests.get(get_recs_endpoint, params=rec_query, headers=header).json()
        if recommendations["seeds"][0]["afterFilteringSize"] > 0:
            recommendation_list.append(recommendations)

    return recommendation_list

def get_recommendation_ids(recs_list: list[dict]):
    id_list = []
    for response in recs_list:
        for track in response["tracks"]:
            id_list.append(track["id"])

    return id_list

def get_user_info(access_token: str) -> dict:
    header = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url='https://api.spotify.com/v1/me', headers=header)
    return response

def refresh_access_token(refresh_token: str, auth_token: str) -> dict:
    refresh_token_endpoint = 'https://accounts.spotify.com/api/token'
    body = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f"Basic {auth_token}"
    }
    response = requests.post(url=refresh_token_endpoint, params=body, headers=header)
    return response