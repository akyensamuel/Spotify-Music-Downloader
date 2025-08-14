@echo off
REM Development setup script for Spotify Playlist Downloader (Windows)

echo 🎵 Setting up Spotify Playlist Downloader...
echo    📁 Project structure reorganized - Django app is now at root level
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing requirements...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚙️ Creating .env file...
    (
    echo # Django settings
    echo SECRET_KEY=django-insecure-change-this-in-production
    echo DEBUG=True
    echo ALLOWED_HOSTS=localhost,127.0.0.1
    echo.
    echo # Spotify API credentials
    echo SPOTIFY_CLIENT_ID=your-spotify-client-id
    echo SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
    echo SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback/
    ) > .env
    echo.
    echo 🔴 IMPORTANT: Please edit .env file with your Spotify API credentials!
    echo    1. Go to https://developer.spotify.com/dashboard
    echo    2. Create a new app
    echo    3. Copy Client ID and Client Secret to .env
    echo    4. Set redirect URI to: http://127.0.0.1:8000/callback/
)

REM Run migrations
echo.
echo 🗄️ Running database migrations...
python manage.py migrate

REM Collect static files
echo 📂 Collecting static files...
python manage.py collectstatic --noinput

REM Create superuser prompt
echo.
echo 👤 Do you want to create a superuser account? (y/n)
set /p response=
if /i "%response%"=="y" (
    python manage.py createsuperuser
)

echo.
echo ✅ Setup complete!
echo.
echo � Project Structure:
echo    🌐 Web App: Root directory (Django)
echo    📜 Legacy Scripts: legacy\ folder
echo    📁 Downloads: downloads\ folder
echo.
echo 🚀 To start the web application:
echo    python manage.py runserver
echo.
echo 🌐 Then visit:
echo    • Main App: http://127.0.0.1:8000
echo    • Admin Panel: http://127.0.0.1:8000/admin
echo.
echo 📜 To use legacy Python scripts:
echo    cd legacy && python music_script.py
echo.
pause
