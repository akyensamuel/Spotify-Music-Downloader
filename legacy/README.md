# 📜 Legacy Python Scripts

These are the original Python scripts that formed the foundation of this project. They work locally and require FFmpeg for MP3 conversion.

## 🗂️ Files

- **`music_script.py`** - Main script with dual authentication support
- **`music_script_user_auth.py`** - User authentication version  
- **`debug_spotify.py`** - Debugging and testing script
- **`test_*.py`** - Various test scripts

## 🚀 Usage

1. **Install dependencies:**
   ```bash
   cd ../  # Go back to root
   pip install -r requirements.txt
   ```

2. **Configure credentials:**
   - Edit the script files directly with your Spotify API credentials
   - Or create a `.env` file in the root directory

3. **Run a script:**
   ```bash
   python music_script.py
   ```

4. **Enter playlist URL when prompted**

## ⚙️ Requirements

- **Python 3.7+**
- **FFmpeg** (for MP3 conversion)
- **Spotify API credentials**

## 💡 Why Legacy?

These scripts were moved to preserve the original functionality while the project evolved into a modern web application. They're still fully functional and useful for:

- **Local usage** with full control
- **Batch processing** of multiple playlists
- **Server-side conversion** with FFmpeg
- **Learning** how the core functionality works

## 🔄 Migration

If you're migrating from these scripts to the web app:

1. Your **Spotify API credentials** can be reused
2. **Downloaded files** in `../downloads/` are preserved  
3. **Functionality** is the same, just with a web interface
4. **Client-side processing** replaces server-side conversion

## 🛠️ Maintenance

These legacy scripts are maintained for compatibility but new features will be added to the web application. For the latest functionality, use the Django web app in the root directory.

---

**📈 Ready to upgrade? Try the modern web interface by running `python ../manage.py runserver` from the root directory!**
