from flask import Flask, redirect, request, jsonify, session
from dotenv import load_dotenv
from datetime import datetime
import spotify_functions as sf
import requests
import base64
import os


app = Flask(__name__)
load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

REDIRECT_URI = 'http://localhost:5000/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_URL = 'https://api.spotify.com/v1/'

def token_invalid(expires_at: int) -> bool:
    return datetime.now().timestamp() > expires_at

def validate_token(expires_at: int, refresh_token: str, auth_token: str) -> None:
    """
    Given token expiry timestamp, refresh token and auth token (base64 encoded client id:secret)
    Updates session dict with new token info
    Returns nothing
    """
    if token_invalid(expires_at):
        response = sf.refresh_access_token(refresh_token, auth_token)
        session['access_token'] = response.json()['access_token']
        session['expires_at'] = datetime.now().timestamp() + response.json()['expires_in']
        session['refresh_token'] = response.json()['refresh_token']

@app.route('/')
def index():
    return("<a href='/login'>Log in with Spotify</a>")

@app.route('/login')
def login():
    scope = 'playlist-modify-public playlist-modify-private playlist-read-private'

    login_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={scope}&show_dialog=true"

    return redirect(login_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error":request.args["error"]})
    if 'code' in request.args:
        req_body = {
            "grant_type": "authorization_code",
            "code": request.args["code"],
            "redirect_uri": REDIRECT_URI
        }

        token_bytes = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode())
        session['auth_token'] = token_bytes.decode()
        
        req_header = {
            "Authorization": f"Basic {session['auth_token']}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(TOKEN_URL, data=req_body, headers=req_header)
        token_info = response.json()
        print(token_info)
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']
        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']

        return redirect("/playlists")

    return redirect("/")

@app.route('/playlists')
def playlists():
    if 'access_token' not in session:
        return redirect('/')
    if 'access_token' in session:
        validate_token(session['expires_at'], session['refresh_token'], session['auth_token'])
        access_token = session['access_token']
        header = {'Authorization': f'Bearer {access_token}'}
        import pdb; pdb.set_trace()
        response = requests.get(url='https://api.spotify.com/v1/me/playlists', headers=header)
        print(response)
        user_playlists = response.json()['items']
        return user_playlists

if __name__ == "__main__":
    app.run(host='0.0.0.0')