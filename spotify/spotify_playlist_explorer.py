import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials

# Set up your app credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="CLIENT_ID",
    client_secret="CLIENT_SECRET",
    redirect_uri="REDIRECT_URI",
    scope='playlist-read-private'  # Scope required to access private playlists
))

# look up playlist by name or id
playlist_name_to_search = "PLAYLIST_NAME"

playlist_id = "PLAYLIST_ID"

# assign results variable
results = sp.playlist_tracks(playlist_id)

# Loop through the items and extract track info
for item in results['items']:
    track = item['track']
    print(f"Track Name: {track['name']} - Artist: {track['artists'][0]['name']}")