"""
Vercel Serverless Function for YouTube Audio Download
Handles the audio download and conversion process
"""
import json
import tempfile
import os
from http.server import BaseHTTPRequestHandler
import yt_dlp
import base64

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            search_query = data.get('query', '')
            quality = data.get('quality', '192')
            
            if not search_query:
                self.send_error_response(400, "Missing search query")
                return
            
            # Download and process audio
            audio_data = self.download_audio(search_query, quality)
            
            if audio_data:
                # Return base64 encoded audio data
                encoded_audio = base64.b64encode(audio_data).decode('utf-8')
                
                response = {
                    'success': True,
                    'audio_data': encoded_audio,
                    'content_type': 'audio/mpeg',
                    'filename': f"{search_query[:50]}.mp3"
                }
                
                self.send_json_response(response)
            else:
                self.send_error_response(404, "Audio not found")
                
        except Exception as e:
            print(f"Error: {str(e)}")
            self.send_error_response(500, f"Server error: {str(e)}")
    
    def download_audio(self, search_query, quality='192'):
        """Download and convert audio using yt-dlp"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = os.path.join(temp_dir, 'audio.%(ext)s')
                
                # yt-dlp configuration for Vercel environment
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
                    # Optimize for serverless environment
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
