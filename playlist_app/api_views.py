"""
Django API views for local development
These handle the same functionality as Vercel serverless functions
"""
import json
import tempfile
import os
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from decouple import config
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def playlist_api(request):
    """Handle playlist metadata extraction (same as /api/download/playlist)"""
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        playlist_url = data.get('playlist_url', '')
        
        if not playlist_url:
            return JsonResponse({'success': False, 'error': 'Missing playlist URL'}, status=400)
        
        # Get playlist data
        playlist_data = get_playlist_data(playlist_url)
        
        if playlist_data:
            response = JsonResponse(playlist_data)
            response["Access-Control-Allow-Origin"] = "*"
            return response
        else:
            return JsonResponse({'success': False, 'error': 'Playlist not found or not accessible'}, status=404)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def audio_api(request):
    """Handle audio download and conversion (same as /api/download/audio)"""
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        search_query = data.get('query', '')
        quality = data.get('quality', '192')
        
        if not search_query:
            return JsonResponse({'success': False, 'error': 'Missing search query'}, status=400)
        
        # Download and process audio
        audio_data = download_audio(search_query, quality)
        
        if audio_data:
            # Return base64 encoded audio data
            encoded_audio = base64.b64encode(audio_data).decode('utf-8')
            
            response_data = {
                'success': True,
                'audio_data': encoded_audio,
                'content_type': 'audio/mpeg',
                'filename': f"{search_query[:50]}.mp3"
            }
            
            response = JsonResponse(response_data)
            response["Access-Control-Allow-Origin"] = "*"
            return response
        else:
            return JsonResponse({'success': False, 'error': 'Audio not found'}, status=404)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'}, status=500)

def get_playlist_data(playlist_url):
    """Extract playlist data using Spotify API"""
    try:
        # Get Spotify credentials using decouple (same as Django settings)
        client_id = config('SPOTIFY_CLIENT_ID', default='')
        client_secret = config('SPOTIFY_CLIENT_SECRET', default='')
        
        if not client_id or not client_secret:
            raise ValueError("Spotify API credentials not configured. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in your .env file")
        
        print(f"Using Spotify credentials: {client_id[:8]}... (Client ID)")
        
        # Initialize Spotify client
        credentials = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(client_credentials_manager=credentials)
        
        # Extract playlist ID
        playlist_id = extract_playlist_id(playlist_url)
        if not playlist_id:
            return None
        
        # Get playlist info
        playlist_info = sp.playlist(playlist_id)
        
        # Get all tracks (handle pagination)
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        
        while results:
            for item in results['items']:
                if item['track'] and item['track']['type'] == 'track':
                    track = item['track']
                    
                    # Get artist names
                    artists = [artist['name'] for artist in track['artists']]
                    
                    track_data = {
                        'id': track['id'],
                        'name': track['name'],
                        'artists': artists,
                        'artist': ', '.join(artists),
                        'duration_ms': track['duration_ms'],
                        'preview_url': track['preview_url'],
                        'external_urls': track['external_urls'],
                        'popularity': track['popularity']
                    }
                    tracks.append(track_data)
            
            # Get next page if available
            results = sp.next(results) if results['next'] else None
        
        playlist_data = {
            'id': playlist_info['id'],
            'name': playlist_info['name'],
            'description': playlist_info['description'],
            'total_tracks': len(tracks),
            'owner': playlist_info['owner']['display_name'],
            'public': playlist_info['public'],
            'tracks': tracks
        }
        
        return playlist_data
        
    except Exception as e:
        print(f"Spotify API error: {str(e)}")
        return None

def download_audio(search_query, quality='192'):
    """Download and convert audio using yt-dlp"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'audio.%(ext)s')
            
            # yt-dlp configuration
            ydl_opts = {
                'format': 'bestaudio[filesize<50M]/best[filesize<50M]',  # Limit file size
                'outtmpl': output_path,
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'extractaudio': True,
                'audioformat': 'mp3',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
                # Optimize for local development
                'socket_timeout': 30,
                'retries': 1,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search and download
                ydl.download([f"ytsearch1:{search_query}"])
                
                # Find the downloaded file
                for file in os.listdir(temp_dir):
                    if file.endswith('.mp3'):
                        file_path = os.path.join(temp_dir, file)
                        with open(file_path, 'rb') as f:
                            return f.read()
            
            return None
            
    except Exception as e:
        print(f"Download error: {str(e)}")
        return None

def extract_playlist_id(url):
    """Extract playlist ID from Spotify URL"""
    try:
        if 'playlist/' in url:
            return url.split('playlist/')[1].split('?')[0]
        elif len(url) == 22 and url.isalnum():
            return url
        return None
    except:
        return None
