import os
import base64
import requests
from flask import Flask, redirect, request, render_template, session
# from dotenv import load_dotenv

# load_dotenv()

app = Flask(__name__)

# Spotify API credentials
CLIENT_ID = "61e3e5a60d1047189e872c8a7a9f0113"
CLIENT_SECRET = "1e4f633fb0894564b824f11100fd9d18"
REDIRECT_URI =  "http://localhost:5000/callback" # Example: 'http://localhost:5000/callback'
AUTHORIZATION_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_URL = 'https://api.spotify.com/v1/me/playlists'

credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
base64_credentials = base64.b64encode(credentials.encode()).decode("utf-8")

app.secret_key = "This is my sevret key"  # Set your secret key

@app.route('/')
def index():
    if 'access_token' not in session:
        return redirect('/login')
    return redirect('/home')


# Step 1: Redirect the user to Spotify's login page
@app.route('/login')
def login():
    auth_url = f"{AUTHORIZATION_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=playlist-read-private"
    return redirect(auth_url)


# Step 2: Spotify will redirect here with a code that we exchange for a token
@app.route('/callback')
def callback():
    code = request.args.get('code')

    # Exchange the code for an access token
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }

    headers = {
        'Authorization': f'Basic {base64_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    response_data = response.json()
    print(response_data)  # Debugging output

    access_token = response_data.get('access_token')
    if access_token:
        session['access_token'] = access_token
        return redirect('/home')
    else:
        return f"Error retrieving access token: {response_data.get('error_description')}", 400

# Step 4: Fetch playlists and render them on the home page
@app.route('/home')
def home():
    access_token = session.get('access_token')
    if not access_token:
        return redirect('/login')

    # Get the user's playlists using the Spotify API
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(API_URL, headers=headers)
    playlists = response.json().get('items', [])

    return render_template('index.html', playlists=playlists)


if __name__ == '__main__':
    app.run(debug=True,host="localhost",port=5000)
