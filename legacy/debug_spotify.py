import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys

# Test with your credentials
SPOTIFY_CLIENT_ID = '38d0826cbb684e5bbaf5b7e31025046b'
SPOTIFY_CLIENT_SECRET = '45d40b9d6d11466e8bdb44ba73721373'

print("Testing Spotify API connection...")

try:
    credentials = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager=credentials)
    print("✓ Spotify client initialized successfully")
    
    # Test with a known public playlist
    playlist_id = '37i9dQZF1DXcBWIGoYBM5M'  # Today's Top Hits
    print(f"Testing with playlist ID: {playlist_id}")
    
    results = sp.playlist_tracks(playlist_id)
    print(f'✓ Successfully fetched playlist tracks')
    print(f'✓ Found {len(results["items"])} tracks')
    
    if results['items']:
        first_track = results['items'][0]['track']
        if first_track:  # Check if track is not None
            print(f'✓ First track: {first_track["name"]} by {first_track["artists"][0]["name"]}')
        else:
            print('⚠ First track is None - this might be a removed or unavailable track')
    
    # Test authentication by trying to get user info (this will fail with client credentials)
    try:
        user_info = sp.current_user()
        print("✓ User authentication working")
    except Exception as user_e:
        print(f"⚠ User authentication failed (expected with client credentials): {user_e}")

except spotipy.exceptions.SpotifyException as spotify_e:
    print(f"✗ Spotify API Error: {spotify_e}")
    if "Invalid client id" in str(spotify_e):
        print("  → Check your SPOTIFY_CLIENT_ID")
    elif "Invalid client secret" in str(spotify_e):
        print("  → Check your SPOTIFY_CLIENT_SECRET")
    elif "insufficient client scope" in str(spotify_e):
        print("  → This playlist might require user authentication instead of client credentials")
except Exception as e:
    print(f"✗ General Error: {e}")
    print(f"✗ Error type: {type(e)}")
    import traceback
    traceback.print_exc()
