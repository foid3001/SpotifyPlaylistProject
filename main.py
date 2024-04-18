from flask import Flask, redirect, request, jsonify, session
from dotenv import load_dotenv
import spotify_functions as sf
import datetime
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

@app.route('/')
def index():
    return("<a href='/login'>Log in with Spotify</a>")

@app.route('/login')
def login():
    scope = 'playlist-modify-public playlist-modify-private user-read-private user-read-email'

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
        
        req_header = {
            "Authorization": f"Basic {token_bytes.decode()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(TOKEN_URL, data=req_body, headers=req_header)
        token_info = response.json()

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
        if datetime.now().timestamp() > session['expires_at']:
            pass
        user_id = sf.get_user_info(session['access_token'])

if __name__ == "__main__":
    app.run(host='0.0.0.0')