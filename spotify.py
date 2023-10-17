import base64
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, jsonify

app = Flask(__name__)

# Set up your Spotify API credentials
client_id = 'a56ebd7094f445089d78603709c02422'
client_secret = '315e9b113f3a468d93ab42f9f4bde493'
redirect_uri = 'http://localhost:8888/callback/'
# Base64 encode the client ID and client secret for authentication
credentials = base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8')
headers = {'Authorization': f'Basic {credentials}'}

# Get an access token
def get_access_token():
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_data = {'grant_type': 'client_credentials'}
    response = requests.post(auth_url, headers=headers, data=auth_data)
    response_data = response.json()
    access_token = response_data['access_token']
    return access_token

# Example function to search for tracks
def search_tracks(query, access_token):
    search_url = 'https://api.spotify.com/v1/search'
    params = {'q': query, 'type': 'track'}
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(search_url, headers=headers, params=params)
    response_data = response.json()
    tracks = response_data.get('tracks', {}).get('items', [])
    return tracks

# Example function to retrieve liked songs
def get_liked_songs(access_token):
    liked_songs_url = 'https://api.spotify.com/v1/me/tracks'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(liked_songs_url, headers=headers)
    response_data = response.json()
    liked_songs = response_data.get('items', [])
    return liked_songs

# HTTP endpoint to view data
@app.route('/tracks/<query>')
def view_tracks(query):
    access_token = get_access_token()
    search_results = search_tracks(query, access_token)
    tracks = []
    for track in search_results:
        track_name = track.get("name", "N/A")
        artist_name = track.get("artists", [{}])[0].get("name", "N/A")
        tracks.append({'track': track_name, 'artist': artist_name})
    return jsonify(tracks)

# HTTP endpoint to retrieve liked songs
# Create a Spotify client with OAuth authorization flow
scope = 'user-library-read'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

# API endpoint to retrieve liked songs
#http://localhost:5000/liked_songs
@app.route('/liked_songs', methods=['GET'])
def get_liked_songs():
    liked_songs = sp.current_user_saved_tracks(limit=50)  # Fetch the first 50 liked songs
    while liked_songs['next']:
        next_songs = sp.next(liked_songs)
        liked_songs['items'].extend(next_songs['items'])
        liked_songs['next'] = next_songs['next']

    songs = []
    for song in liked_songs['items']:
        track = song['track']
        songs.append({
            'track_name': track['name'],
            'artist_name': track['artists'][0]['name'],
            'album_name': track['album']['name'],
            'release_date': track['album']['release_date']
        })

    return jsonify(songs)

# Run the Flask app
if __name__ == '__main__':
    app.run()
