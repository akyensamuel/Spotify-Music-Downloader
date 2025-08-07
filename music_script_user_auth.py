import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import yt_dlp

# ---- CONFIGURE YOUR SPOTIFY CREDENTIALS ----
SPOTIFY_CLIENT_ID = '38d0826cbb684e5bbaf5b7e31025046b'
SPOTIFY_CLIENT_SECRET = '45d40b9d6d11466e8bdb44ba73721373'
SPOTIFY_REDIRECT_URI = 'http://localhost:8080'  # Must match your Spotify app settings

# ---- Set up Spotify API with User Authentication ----
def get_spotify_tracks_user_auth(playlist_url):
    # Extract playlist ID from URL
    if "playlist/" in playlist_url:
        playlist_id = playlist_url.split("playlist/")[1].split("?")[0]
    else:
        playlist_id = playlist_url

    print(f"Extracted Playlist ID: {playlist_id}")

    try:
        # User authentication - can access private playlists if user owns them
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope="playlist-read-private playlist-read-collaborative"
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)

        # First, check if playlist exists and is accessible
        try:
            playlist_info = sp.playlist(playlist_id)
            print(f"Found playlist: '{playlist_info['name']}' by {playlist_info['owner']['display_name']}")
            print(f"Total tracks: {playlist_info['tracks']['total']}")
            print(f"Public: {playlist_info['public']}")
        
        except spotipy.exceptions.SpotifyException as e:
            if "404" in str(e):
                print("✗ Error: Playlist not found or not accessible.")
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
                
                if track is None:
                    print(f"⚠ Track {total_tracks}: [UNAVAILABLE/REMOVED]")
                    unavailable_tracks += 1
                    continue
                
                if not track['artists']:
                    print(f"⚠ Track {total_tracks}: '{track['name']}' has no artist info")
                    unavailable_tracks += 1
                    continue
                
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

        print(f"Successfully extracted {len(tracks)} playable tracks")
        if unavailable_tracks > 0:
            print(f"⚠ {unavailable_tracks} tracks were unavailable or not playable")

        return tracks

    except spotipy.exceptions.SpotifyException as e:
        print(f"✗ Spotify API Error: {e}")
        return []
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return []

# ---- Download from YouTube ----
def download_from_youtube(search_query, output_folder='downloads'):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': False,
        'extractaudio': True,
        'audioformat': 'mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([f"ytsearch1:{search_query}"])
        except Exception as e:
            print(f"Failed to download {search_query}: {e}")

# ---- Main Function ----
def download_spotify_playlist(playlist_url):
    print("Fetching tracks from Spotify playlist (with user authentication)...")
    tracks = get_spotify_tracks_user_auth(playlist_url)
    
    if not tracks:
        print("✗ No tracks found or playlist is not accessible.")
        return
    
    print(f"Found {len(tracks)} tracks. Starting download...\n")
    
    successful_downloads = 0
    failed_downloads = 0
    
    for i, track in enumerate(tracks, 1):
        print(f"[{i}/{len(tracks)}] Downloading: {track}")
        try:
            download_from_youtube(track)
            successful_downloads += 1
        except Exception as e:
            print(f"Failed to download '{track}': {e}")
            failed_downloads += 1
    
    print(f"\n=== Download Summary ===")
    print(f"✓ Successful: {successful_downloads}")
    if failed_downloads > 0:
        print(f"✗ Failed: {failed_downloads}")
    print(f"Total processed: {len(tracks)}")

# ---- Run the Script ----
if __name__ == "__main__":
    print("=== Spotify Playlist Downloader (User Authentication) ===")
    print("This version can access both public and private playlists (if you have access).")
    print("You'll need to authorize the app in your browser on first run.\n")
    
    spotify_url = input("Enter Spotify playlist URL: ").strip()
    
    if not spotify_url:
        print("✗ Error: No URL provided")
        exit(1)
    
    if "spotify.com" not in spotify_url and len(spotify_url) != 22:
        print("✗ Error: Invalid Spotify URL or playlist ID")
        exit(1)
    
    download_spotify_playlist(spotify_url)
