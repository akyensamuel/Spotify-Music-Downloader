"""
Vercel Serverless Function for Spotify Playlist Processing
Handles playlist metadata extraction
"""
import json
import os
from http.server import BaseHTTPRequestHandler
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            playlist_url = data.get('playlist_url', '')
            
            if not playlist_url:
                self.send_error_response(400, "Missing playlist URL")
                return
            
            # Get playlist data
            playlist_data = self.get_playlist_data(playlist_url)
            
            if playlist_data:
                self.send_json_response(playlist_data)
            else:
                self.send_error_response(404, "Playlist not found or not accessible")
                
        except Exception as e:
            print(f"Error: {str(e)}")
            self.send_error_response(500, f"Server error: {str(e)}")
    
    def get_playlist_data(self, playlist_url):
        """Extract playlist data using Spotify API"""
        try:
            # Get Spotify credentials from environment
            client_id = os.environ.get('SPOTIFY_CLIENT_ID')
            client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                raise ValueError("Spotify API credentials not configured")
            
            # Initialize Spotify client
            credentials = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            sp = spotipy.Spotify(client_credentials_manager=credentials)
            
            # Extract playlist ID
            playlist_id = self.extract_playlist_id(playlist_url)
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
    
    def extract_playlist_id(self, url):
        """Extract playlist ID from Spotify URL"""
        try:
            if 'playlist/' in url:
                return url.split('playlist/')[1].split('?')[0]
            elif len(url) == 22 and url.isalnum():
                return url
            return None
        except:
            return None
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data)
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, status_code, message):
        """Send error response"""
        error_data = {'success': False, 'error': message}
        self.send_json_response(error_data, status_code)
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
