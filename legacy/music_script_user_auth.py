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
def download_from_youtube(search_query, output_folder='downloads', quality='192'):
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")
        
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
            'preferredquality': quality,
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([f"ytsearch1:{search_query}"])
            return True
        except Exception as e:
            print(f"Failed to download {search_query}: {e}")
            return False

def get_download_settings():
    """Get download folder and settings from user"""
    print("\n=== Download Settings ===")
    
    # Get custom folder name
    folder_name = input("Enter custom folder name (or press Enter for 'downloads'): ").strip()
    if not folder_name:
        folder_name = "downloads"
    
    # Get audio quality
    print("\nSelect audio quality:")
    print("1. 128 kbps (Low)")
    print("2. 192 kbps (Standard) - Default")
    print("3. 320 kbps (High)")
    
    while True:
        quality_choice = input("Choose quality (1-3, or press Enter for default): ").strip()
        if quality_choice == "1":
            quality = "128"
            break
        elif quality_choice == "3":
            quality = "320"
            break
        elif quality_choice == "2" or quality_choice == "":
            quality = "192"
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    # Ask if user wants to select custom path
    print(f"\nCurrent download folder will be: {os.path.abspath(folder_name)}")
    change_path = input("Do you want to choose a different location? (y/n): ").lower().strip()
    
    if change_path in ['y', 'yes']:
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            custom_path = filedialog.askdirectory(
                title="Select Download Folder",
                initialdir=os.path.expanduser("~")
            )
            root.destroy()
            
            if custom_path:
                folder_name = os.path.join(custom_path, folder_name)
            else:
                print("No folder selected. Using default location.")
                
        except ImportError:
            print("GUI folder selection not available. Please install tkinter.")
            custom_path = input("Enter full path to download folder (or press Enter for current directory): ").strip()
            if custom_path and os.path.exists(os.path.dirname(custom_path)):
                folder_name = custom_path
    
    return folder_name, quality

# ---- Main Function ----
def download_spotify_playlist(playlist_url, output_folder='downloads', quality='192'):
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
            if download_from_youtube(track, output_folder, quality):
                successful_downloads += 1
                print(f"✓ Successfully downloaded")
            else:
                failed_downloads += 1
        except Exception as e:
            print(f"✗ Failed to download '{track}': {e}")
            failed_downloads += 1
    
    print(f"\n=== Download Summary ===")
    print(f"✓ Successful: {successful_downloads}")
    if failed_downloads > 0:
        print(f"✗ Failed: {failed_downloads}")
    print(f"Total processed: {len(tracks)}")
    print(f"Files saved to: {os.path.abspath(output_folder)}")

# ---- Run the Script ----
if __name__ == "__main__":
    print("=== Spotify Playlist Downloader (User Authentication) ===")
    print("This version can access both public and private playlists (if you have access).")
    print("You'll need to authorize the app in your browser on first run.\n")
    
    # Get download settings first
    output_folder, audio_quality = get_download_settings()
    print(f"\nDownload settings configured:")
    print(f"📁 Folder: {output_folder}")
    print(f"🎵 Quality: {audio_quality} kbps")
    
    spotify_url = input("\nEnter Spotify playlist URL: ").strip()
    
    if not spotify_url:
        print("✗ Error: No URL provided")
        input("Press Enter to exit...")
        exit(1)
    
    if "spotify.com" not in spotify_url and len(spotify_url) != 22:
        print("✗ Error: Invalid Spotify URL or playlist ID")
        input("Press Enter to exit...")
        exit(1)
    
    download_spotify_playlist(spotify_url, output_folder, audio_quality)
    input("\nPress Enter to exit...")
