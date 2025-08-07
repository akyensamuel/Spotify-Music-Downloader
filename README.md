# 🎵 Spotify Playlist Downloader

A Python script that downloads music from YouTube based on tracks from Spotify playlists. This tool extracts track information from Spotify and searches for the corresponding audio on YouTube, then downloads it as MP3 files (when FFmpeg is available).

## ✨ Features

- **Dual Authentication Support**: Works with both public playlists (no login required) and private playlists (requires Spotify login)
- **Smart Fallback System**: Automatically tries user authentication first, falls back to public access if needed
- **MP3 Conversion**: Automatically converts downloaded files to MP3 format when FFmpeg is available
- **Comprehensive Error Handling**: Handles unavailable tracks, region restrictions, and API errors gracefully
- **Progress Tracking**: Shows detailed progress and download statistics
- **Debug Mode**: Includes diagnostic tools to troubleshoot playlist access issues
- **Respectful Downloads**: Includes delays between downloads to avoid overwhelming services

## 📋 Prerequisites

### Required Software

1. **Python 3.7+**
2. **FFmpeg** (strongly recommended for MP3 conversion)

### Required Python Packages

Install the required packages using pip:

```bash
pip install spotipy yt-dlp
```

Or if you have a requirements.txt file:
```bash
pip install -r requirements.txt
```

### FFmpeg Installation

**FFmpeg is essential for converting downloaded audio files (usually WebM/MP4) to MP3 format.**

#### Windows:
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract the files to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your system PATH environment variable
4. Test installation: Open Command Prompt and run `ffmpeg -version`

#### macOS:
```bash
# Using Homebrew
brew install ffmpeg

# Using MacPorts
port install ffmpeg
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Linux (CentOS/RHEL):
```bash
sudo yum install ffmpeg
# or
sudo dnf install ffmpeg
```

### Verify FFmpeg Installation:
```bash
ffmpeg -version
```
If FFmpeg is properly installed, you should see version information. If not, the script will still work but will download files in their original format (WebM/MP4) instead of converting to MP3.

## 🔧 Setup

### 1. Spotify API Credentials

You need to create a Spotify application to get API credentials:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app details:
   - **App Name**: Choose any name (e.g., "Playlist Downloader")
   - **App Description**: Brief description of your use
   - **Redirect URI**: `http://127.0.0.1:8888/callback`
5. Accept the terms and create the app
6. Note down your **Client ID** and **Client Secret**
7. Update the credentials in the script:

```python
SPOTIFY_CLIENT_ID = 'your_client_id_here'
SPOTIFY_CLIENT_SECRET = 'your_client_secret_here'
```

### 2. File Structure

Make sure your project directory looks like this:

```
Spotify Downloader/
├── music_script.py
├── downloads/          # Created automatically
├── .virtualEnv/        # Python virtual environment (optional)
├── .cache             # Spotify auth cache (created automatically)
├── .gitignore
└── README.md
```

## 🚀 Usage

### Basic Usage

1. **Run the script:**
   ```bash
   python music_script.py
   ```

2. **Enter a Spotify playlist URL when prompted:**
   ```
   Enter Spotify playlist URL: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
   ```

3. **Authentication (if needed):**
   - For public playlists: No authentication required
   - For private playlists: A browser window will open for Spotify login
   - Complete the login process and return to the terminal

4. **Confirm download:**
   - The script will show how many tracks were found
   - Confirm if you want to proceed with the download

### Supported URL Formats

- Full playlist URL: `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`
- Playlist URL with parameters: `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=abcd1234`
- Just the playlist ID: `37i9dQZF1DXcBWIGoYBM5M`

### Example Output

```
=== Spotify Playlist Downloader ===
This tool downloads audio from YouTube based on Spotify playlist tracks.
Note: For private playlists, you'll need to authenticate with your Spotify account.

Enter Spotify playlist URL: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
Extracted Playlist ID: 37i9dQZF1DXcBWIGoYBM5M
Starting authentication process...

Setting up user authentication...
⚠ A browser window will open for Spotify login.
Please complete the authentication in your browser and return here.

✓ Successfully authenticated as: YourUsername
Found playlist: 'Today's Top Hits' by Spotify
Total tracks: 50
Public: True
Successfully extracted 48 playable tracks using user authentication
⚠ 2 tracks were unavailable or not playable

✓ Found 48 tracks!

Proceed with downloading 48 tracks? (y/n): y

Starting download in 3 seconds...
3...
2...
1...
Starting downloads!

FFmpeg detected - will convert to MP3
[1/48] Downloading: Anti-Hero Taylor Swift
[2/48] Downloading: As It Was Harry Styles
...

=== Download Summary ===
✓ Successful: 46
✗ Failed: 2
Total processed: 48
Downloads completed!
```

## 📁 Output

### File Locations

- **Downloads folder**: `downloads/` (created automatically)
- **File format**: MP3 (if FFmpeg is available) or original format (WebM/MP4)
- **File names**: Based on YouTube video titles
- **Audio quality**: 192 kbps MP3 (when converted)

### Without FFmpeg
If FFmpeg is not installed, files will be downloaded in their original format:
- **.webm** files (most common)
- **.mp4** files (some videos)
- **.m4a** files (audio-only)

These files can be manually converted to MP3 later using FFmpeg:
```bash
ffmpeg -i "input_file.webm" -b:a 192k "output_file.mp3"
```

### With FFmpeg
When FFmpeg is available, all files are automatically converted to MP3 format with:
- **Codec**: MP3
- **Bitrate**: 192 kbps
- **Quality**: High quality audio suitable for most uses

## 🔍 Troubleshooting

### Common Issues

#### "Playlist not found or not accessible"
- **Solution**: Check if the playlist URL is correct
- **Solution**: Ensure the playlist is public or you have access to it
- **Solution**: Try with user authentication (the script will prompt you)

#### "FFmpeg not found"
- **Solution**: Install FFmpeg (see installation instructions above)
- **Alternative**: Downloads will work but in original format (WebM/MP4)

#### "Authentication failed"
- **Solution**: Check your Spotify Client ID and Client Secret
- **Solution**: Ensure the redirect URI in your Spotify app settings matches: `http://127.0.0.1:8888/callback`
- **Solution**: Try deleting the `.cache` file and re-authenticating

#### "Failed to download" messages
- **Common causes**: Video not available, age-restricted content, geo-blocked content
- **Solution**: These are usually individual track issues and don't affect the overall download process

#### Downloads are slow
- The script includes intentional delays between downloads to be respectful to services
- This is normal behavior and helps avoid rate limiting

### Debug Mode

The script includes automatic debug mode that activates when playlist access fails:

```
Running diagnostic tests...
Test 1: Basic playlist access...
Test 2: Trying with market=US...
Test 3: Searching for playlist...
```

### Test Playlists

If you're having issues, try these known working public playlists:

- **Today's Top Hits**: `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`
- **RapCaviar**: `https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd`
- **Global Top 50**: `https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF`

## ⚖️ Legal and Ethical Considerations

### Important Notes

1. **Personal Use Only**: This tool is intended for personal use only
2. **Respect Copyright**: Only download music you have the right to download
3. **Support Artists**: Consider purchasing or streaming music through official channels
4. **YouTube Terms**: Ensure your usage complies with YouTube's Terms of Service
5. **Rate Limiting**: The script includes delays to be respectful to services

### Recommendations

- Use this tool to discover new music, then support artists through official channels
- Consider this a way to create personal backups of music you already own
- Be mindful of download volumes and frequency

## 🛠️ Advanced Configuration

### Customizing Download Settings

You can modify the `download_from_youtube` function to change:

- **Audio quality**: Change `'preferredquality': '192'` to desired bitrate
- **Output format**: Change `'audioformat': 'mp3'` to other formats
- **Output directory**: Change `output_folder='downloads'` to your preferred location

### Batch Processing

To process multiple playlists, you can modify the main section:

```python
playlists = [
    "https://open.spotify.com/playlist/playlist1",
    "https://open.spotify.com/playlist/playlist2",
]

for playlist in playlists:
    download_spotify_playlist(playlist)
```

## 📝 Version History

### Current Features
- Dual authentication support (public and private playlists)
- Automatic FFmpeg detection and MP3 conversion
- Comprehensive error handling and user feedback
- Debug mode for troubleshooting
- Progress tracking and download summaries
- Respectful rate limiting

## 🤝 Contributing

If you encounter issues or have suggestions for improvements, please:

1. Check the troubleshooting section first
2. Test with known working playlists
3. Ensure FFmpeg is properly installed
4. Verify your Spotify API credentials

## 📜 License

This project is for educational and personal use only. Please respect copyright laws and the terms of service of all involved platforms.

---

**Happy downloading! 🎵**
