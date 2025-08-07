import os
import time
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import spotipy
import yt_dlp

SPOTIFY_CLIENT_ID = '38d0826cbb684e5bbaf5b7e31025046b'
SPOTIFY_CLIENT_SECRET = '45d40b9d6d11466e8bdb44ba73721373'
SPOTIFY_REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SCOPE = 'playlist-read-private playlist-read-collaborative'

def create_spotify_client_with_user_auth():
    """Create Spotify client with user authentication (can access private playlists)"""
    print("Setting up user authentication...")
    print("⚠ A browser window will open for Spotify login.")
    print("Please complete the authentication in your browser and return here.")
    
    # Small delay to let user read the message
    time.sleep(2)
    
    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True,
        cache_path=".cache"  # Cache the token to avoid re-authentication
    )
    
    # Create client and trigger authentication
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    print("Waiting for authentication to complete...")
    print("If browser didn't open automatically, check the console for the authorization URL.")
    
    # Give user time to complete authentication
    time.sleep(5)
    
    # Test authentication with a simple call
    try:
        user_info = sp.current_user()
        print(f"✓ Successfully authenticated as: {user_info.get('display_name', 'Unknown User')}")
        time.sleep(1)  # Brief pause for user to see success message
        return sp
    except Exception as e:
        print(f"✗ Authentication test failed: {e}")
        print("Please try again and make sure to complete the browser authentication.")
        raise e

def create_spotify_client_public():
    """Create Spotify client for public data only (no user authentication)"""
    return spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
    )

def debug_playlist_access(sp, playlist_id):
    """Debug function to test different ways of accessing a playlist"""
    print(f"\n=== Debugging Playlist Access for ID: {playlist_id} ===")
    
    # Test 1: Basic playlist info without market
    try:
        print("Test 1: Basic playlist access...")
        playlist = sp.playlist(playlist_id, fields="id,name,public,owner,tracks.total")
        print(f"✓ Basic access successful: '{playlist['name']}' by {playlist['owner']['display_name']}")
        return True
    except spotipy.exceptions.SpotifyException as e:
        print(f"✗ Basic access failed: {e}")
    
    # Test 2: Try with different markets
    markets = ['US', 'GB', 'CA', 'AU', 'DE', None]
    for market in markets:
        try:
            print(f"Test 2: Trying with market={market}...")
            playlist = sp.playlist(playlist_id, market=market, fields="id,name,public,owner")
            print(f"✓ Success with market {market}: '{playlist['name']}'")
            return True
        except spotipy.exceptions.SpotifyException as e:
            print(f"✗ Failed with market {market}: {e}")
    
    # Test 3: Try to search for the playlist
    try:
        print("Test 3: Searching for playlist...")
        results = sp.search(f"playlist:{playlist_id}", type='playlist', limit=1)
        if results['playlists']['items']:
            found_playlist = results['playlists']['items'][0]
            found_id = found_playlist['id']
            print(f"✓ Found via search: '{found_playlist['name']}' by {found_playlist['owner']['display_name']}")
            print(f"  Search returned ID: {found_id}")
            print(f"  Original ID:        {playlist_id}")
            if found_id != playlist_id:
                print("  ⚠ Note: Search returned a different playlist ID!")
            return True
        else:
            print("✗ No results found via search")
    except Exception as e:
        print(f"✗ Search failed: {e}")
    
    return False

def fetch_playlist_tracks(sp, playlist_id, auth_type="user"):
    """Fetch tracks from playlist using the provided Spotify client"""
    try:
        # First, check if playlist exists and is accessible
        try:
            playlist_info = sp.playlist(playlist_id)
            print(f"Found playlist: '{playlist_info['name']}' by {playlist_info['owner']['display_name']}")
            print(f"Total tracks: {playlist_info['tracks']['total']}")
            print(f"Public: {playlist_info.get('public', 'Unknown')}")
            
        except spotipy.exceptions.SpotifyException as e:
            if "404" in str(e):
                print("✗ Error: Playlist not found or not accessible.")
                
                # Run debug tests
                print("Running diagnostic tests...")
                if debug_playlist_access(sp, playlist_id):
                    print("Debug tests found the playlist! Trying to get the correct playlist ID from search results...")
                    # Try to get the correct playlist from search results
                    try:
                        search_results = sp.search(f"playlist:{playlist_id}", type='playlist', limit=1)
                        if search_results['playlists']['items']:
                            correct_playlist = search_results['playlists']['items'][0]
                            correct_id = correct_playlist['id']
                            print(f"Found correct playlist ID: {correct_id}")
                            print(f"Playlist name: '{correct_playlist['name']}' by {correct_playlist['owner']['display_name']}")
                            
                            # Try with the correct ID
                            playlist_info = sp.playlist(correct_id)
                            print(f"✓ Successfully accessed playlist with correct ID!")
                            # Update playlist_id for the rest of the function
                            playlist_id = correct_id
                        else:
                            print("✗ Could not find playlist in search results")
                            return []
                    except Exception as e:
                        print(f"✗ Failed to use search results: {e}")
                        return []
                else:
                    if auth_type == "public":
                        print("This playlist might be private. Try running the script again to use user authentication.")
                    else:
                        print("This could mean:")
                        print("  - The playlist has been deleted")
                        print("  - The playlist ID is incorrect")
                        print("  - The playlist is region-restricted")
                        print("  - You don't have permission to access this playlist")
                    return []
            else:
                raise e

        # Get tracks with pagination
        results = sp.playlist_tracks(playlist_id, market='US')
        tracks = []
        total_tracks = 0
        unavailable_tracks = 0

        while results:
            for item in results['items']:
                total_tracks += 1
                track = item['track']
                
                # Handle unavailable/removed tracks
                if track is None:
                    print(f"⚠ Track {total_tracks}: [UNAVAILABLE/REMOVED]")
                    unavailable_tracks += 1
                    continue
                
                # Handle tracks without artists (edge case)
                if not track['artists']:
                    print(f"⚠ Track {total_tracks}: '{track['name']}' has no artist info")
                    unavailable_tracks += 1
                    continue
                
                # Check if track is playable
                if track.get('is_playable', True) == False:
                    print(f"⚠ Track {total_tracks}: '{track['name']}' is not playable in your region")
                    unavailable_tracks += 1
                    continue
                
                title = track['name']
                artist = track['artists'][0]['name']
                tracks.append(f"{title} {artist}")
            
            if results['next']:
                results = sp.next(results)
            else:
                break

        print(f"Successfully extracted {len(tracks)} playable tracks using {auth_type} authentication")
        if unavailable_tracks > 0:
            print(f"⚠ {unavailable_tracks} tracks were unavailable or not playable")

        return tracks

    except spotipy.exceptions.SpotifyException as e:
        print(f"✗ Spotify API Error: {e}")
        if "Invalid client" in str(e):
            print("→ Check your Spotify API credentials (Client ID and Client Secret)")
        elif "401" in str(e):
            print("→ Authentication failed. Your credentials may be invalid or expired.")
        elif "403" in str(e):
            print("→ Access forbidden. You may not have permission to access this playlist.")
        raise e
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise e

def get_spotify_tracks(playlist_url):
    # Extract playlist ID from URL
    if "playlist/" in playlist_url:
        playlist_id = playlist_url.split("playlist/")[1].split("?")[0]
    else:
        playlist_id = playlist_url  # in case user already passed the ID

    print(f"Extracted Playlist ID: {playlist_id}")
    print("Starting authentication process...\n")

    # Try with user authentication first (can access both public and private)
    try:
        sp = create_spotify_client_with_user_auth()
        print("Proceeding to fetch playlist data...")
        time.sleep(1)  # Brief pause before making API calls
        return fetch_playlist_tracks(sp, playlist_id, auth_type="user")
    except Exception as e:
        print(f"User authentication failed: {e}")
        print("Trying with public client credentials...")
        time.sleep(2)  # Give user time to read the message
        
        # Fall back to public client credentials
        try:
            sp = create_spotify_client_public()
            return fetch_playlist_tracks(sp, playlist_id, auth_type="public")
        except Exception as e:
            print(f"Public client credentials also failed: {e}")
            return []

# ---- Download from YouTube ----
def download_from_youtube(search_query, output_folder='downloads'):
    # Check if FFmpeg is available
    try:
        import subprocess
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        ffmpeg_available = True
        print("FFmpeg detected - will convert to MP3")
    except:
        ffmpeg_available = False
        print("⚠ FFmpeg not found - will download as original format (webm/mp4)")
    
    if ffmpeg_available:
        # With FFmpeg - convert to MP3
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
            'extractaudio': True,
            'audioformat': 'mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        # Without FFmpeg - download original format
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
            'noplaylist': True,
            'quiet': True,
        }
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([f"ytsearch1:{search_query}"])
            return True
        except Exception as e:
            print(f"Failed to download {search_query}: {e}")
            return False

# ---- Main Function ----
def download_spotify_playlist(playlist_url):
    print("Fetching tracks from Spotify playlist...")
    tracks = get_spotify_tracks(playlist_url)
    
    if not tracks:
        print("✗ No tracks found or playlist is not accessible.")
        print("\nTroubleshooting tips:")
        print("  1. Make sure the playlist URL is correct")
        print("  2. Check if the playlist is public or if you have access to it")
        print("  3. Verify your Spotify API credentials")
        print("  4. Try with a different playlist to test if the script works")
        print("\nSuggested test playlists:")
        print("  - Today's Top Hits: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
        print("  - RapCaviar: https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd")
        return
    
    print(f"\n✓ Found {len(tracks)} tracks!")
    
    # Ask user if they want to proceed with download
    while True:
        proceed = input(f"\nProceed with downloading {len(tracks)} tracks? (y/n): ").lower().strip()
        if proceed in ['y', 'yes']:
            break
        elif proceed in ['n', 'no']:
            print("Download cancelled.")
            return
        else:
            print("Please enter 'y' for yes or 'n' for no.")
    
    print(f"\nStarting download in 3 seconds...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    print("Starting downloads!\n")
    
    successful_downloads = 0
    failed_downloads = 0
    
    for i, track in enumerate(tracks, 1):
        print(f"[{i}/{len(tracks)}] Downloading: {track}")
        try:
            if download_from_youtube(track):
                successful_downloads += 1
            else:
                failed_downloads += 1
            # Brief delay between downloads to be respectful to YouTube
            time.sleep(1)
        except Exception as e:
            print(f"Failed to download '{track}': {e}")
            failed_downloads += 1
            time.sleep(0.5)  # Shorter delay for failed downloads
    
    print(f"\n=== Download Summary ===")
    print(f"✓ Successful: {successful_downloads}")
    if failed_downloads > 0:
        print(f"✗ Failed: {failed_downloads}")
    print(f"Total processed: {len(tracks)}")
    print("Downloads completed!")

# ---- Run the Script ----
if __name__ == "__main__":
    print("=== Spotify Playlist Downloader ===")
    print("This tool downloads audio from YouTube based on Spotify playlist tracks.")
    print("Note: For private playlists, you'll need to authenticate with your Spotify account.\n")
    
    spotify_url = input("Enter Spotify playlist URL: ").strip()
    
    if not spotify_url:
        print("✗ Error: No URL provided")
        exit(1)
    
    if "spotify.com" not in spotify_url and len(spotify_url) != 22:
        print("✗ Error: Invalid Spotify URL or playlist ID")
        print("Please provide either:")
        print("  - Full Spotify playlist URL (https://open.spotify.com/playlist/...)")
        print("  - Just the playlist ID (22 characters)")
        exit(1)
    
    download_spotify_playlist(spotify_url)

# https://open.spotify.com/playlist/2rL7J8CJrdksF944XqcYjr?si=sCBi5dnaQi-MiW1Sy5DnxA