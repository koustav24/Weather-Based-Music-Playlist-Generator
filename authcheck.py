import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")


def test_auth():
    scope = "playlist-modify-public playlist-modify-private user-read-private"
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=scope
        ))

        # Test authentication
        user = sp.current_user()
        print(f"Authentication successful! Logged in as: {user['display_name']}")

        # Test a simple API call
        results = sp.search(q="Arijit Singh", limit=1)
        print(f"API call successful: {results['tracks']['items'][0]['name']}")

        return True
    except Exception as e:
        print(f"Authentication test failed: {e}")
        return False


if __name__ == "__main__":
    test_auth()