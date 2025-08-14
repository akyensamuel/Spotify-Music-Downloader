# Spotify Playlist Downloader - Usage Guide

This project provides multiple ways to download Spotify playlists as MP3 files. Choose the method that best fits your needs.

## 🌐 Web Application (Recommended)

The modern web interface provides the best user experience with client-side processing.

### Features
- ✅ No server-side processing needed (perfect for free hosting)
- ✅ Real-time download progress
- ✅ Custom folder selection using browser's File System Access API
- ✅ Audio quality selection (128, 192, 320 kbps)
- ✅ Responsive design works on mobile and desktop
- ✅ No authentication required for public playlists

### Quick Start
1. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Set up Spotify API credentials:**
   - Create a `.env` file in the project root
   - Add your Spotify API credentials:
     ```
     SPOTIFY_CLIENT_ID=your_client_id_here
     SPOTIFY_CLIENT_SECRET=your_client_secret_here
     ```

3. **Run the Django server:**
   ```cmd
   python manage.py migrate
   python manage.py runserver
   ```

4. **Open your browser:**
   - Go to `http://127.0.0.1:8000`
   - Paste your Spotify playlist URL
   - Choose download settings (folder, quality)
   - Select tracks to download
   - Click "Download Selected"

### Browser Requirements
- **Chrome/Edge 86+** - Full File System Access API support
- **Firefox/Safari** - Downloads to default Downloads folder

## 🖥️ Desktop Scripts (Legacy)

For users who prefer command-line tools or need specific functionality.

### Option 1: Simple Script (Public Playlists Only)
```cmd
cd legacy
python music_script.py
```
- Enter playlist URL when prompted
- Choose download folder and quality settings
- Wait for downloads to complete

### Option 2: Authenticated Script (Public + Private Playlists)
```cmd
cd legacy  
python music_script_user_auth.py
```
- First run will open browser for Spotify authentication
- Can access your private playlists
- Choose download folder and quality settings
- Enter playlist URL when prompted

## 📁 Download Settings

Both web app and desktop scripts now support:

### Folder Selection
- **Web App**: Browser's native folder picker (Chrome/Edge) or Downloads folder
- **Desktop Scripts**: GUI folder picker dialog or manual path entry

### Audio Quality Options
- **128 kbps** - Smaller file size, lower quality
- **192 kbps** - Standard quality (recommended)
- **320 kbps** - High quality, larger file size

### File Naming
Files are automatically named as: `Artist - Song Title.mp3`

## 🛠️ Troubleshooting

### Common Issues

**"No tracks found"**
- Check if playlist URL is correct
- Ensure playlist is public (for web app)
- Try the authenticated script for private playlists

**"Download failed"**
- Some songs may not be available on YouTube
- Check your internet connection
- Verify FFmpeg is installed and in PATH

**"GUI folder selection not available"**
- Install tkinter: `pip install tkinter` (usually included with Python)
- Or manually enter folder path when prompted

### Dependencies
Make sure you have installed:
- Python 3.8+
- FFmpeg (for audio conversion)
- All packages from requirements.txt

### FFmpeg Installation
**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

## 🚀 Deployment (Web App)

The web app is configured for easy deployment on:
- **Heroku** - Free tier available
- **Railway** - Simple Git-based deployment  
- **Render** - Free static site hosting
- **Vercel** - Free for personal projects

All processing happens client-side, so no server resources are needed for downloads.

## 📋 Project Structure

```
spotify_downloader/           # Django project root
├── playlist_app/            # Main Django app
├── templates/               # HTML templates
├── static/                  # CSS, JavaScript, images
├── legacy/                  # Original Python scripts
│   ├── music_script.py      # Simple downloader
│   └── music_script_user_auth.py  # Authenticated version
├── downloads/               # Default download folder
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── manage.py               # Django management script
```

## 📝 Notes

- **Legal**: Only download music you own or have permission to download
- **Quality**: YouTube compression affects final audio quality regardless of bitrate setting
- **Rate Limits**: Large playlists may trigger YouTube rate limiting - script will retry automatically
- **Storage**: Check available disk space before downloading large playlists

## 🤝 Support

If you encounter issues:
1. Check this guide first
2. Ensure all dependencies are installed correctly
3. Verify your Spotify API credentials (for web app)
4. Test with a small public playlist first

---

**Happy downloading! 🎵**
