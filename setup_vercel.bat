@echo off
echo 🚀 Spotify Downloader - Vercel Setup
echo =====================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    pause
    exit /b 1
)

:: Check if Node.js is installed (for Vercel CLI)
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found! Please install Node.js first.
    echo    Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Python found
echo ✅ Node.js found
echo.

:: Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

:: Install Vercel CLI
echo 📦 Installing Vercel CLI...
npm install -g vercel
if errorlevel 1 (
    echo ❌ Failed to install Vercel CLI
    pause
    exit /b 1
)

:: Check for .env file
if not exist .env (
    if exist .env.example (
        echo 📝 Copying .env.example to .env
        copy .env.example .env
        echo.
        echo ⚠️  Please edit .env file with your Spotify API credentials:
        echo    - Get them from: https://developer.spotify.com/dashboard
        echo    - Add your SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET
        echo.
    ) else (
        echo ⚠️  No .env file found. Please create one with your Spotify API credentials.
    )
)

:: Run Django migrations
echo 🔄 Setting up Django database...
python manage.py migrate
if errorlevel 1 (
    echo ❌ Database setup failed
    pause
    exit /b 1
)

echo.
echo 🎉 Setup complete! Next steps:
echo.
echo 1. Edit your .env file with Spotify API credentials
echo 2. Test locally: python manage.py runserver
echo 3. Test Vercel functions: vercel dev
echo 4. Deploy: vercel --prod
echo.
echo 📖 See VERCEL_DEPLOYMENT.md for detailed instructions
echo.
pause
