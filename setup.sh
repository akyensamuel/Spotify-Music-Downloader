#!/bin/bash
# Development setup script for Spotify Playlist Downloader

echo "🎵 Setting up Spotify Playlist Downloader..."
echo "   📁 Project structure reorganized - Django app is now at root level"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOL
# Django settings
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Spotify API credentials
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback/
EOL
    echo ""
    echo "🔴 IMPORTANT: Please edit .env file with your Spotify API credentials!"
    echo "   1. Go to https://developer.spotify.com/dashboard"
    echo "   2. Create a new app"  
    echo "   3. Copy Client ID and Client Secret to .env"
    echo "   4. Set redirect URI to: http://127.0.0.1:8000/callback/"
fi

# Run migrations
echo ""
echo "🗄️ Running database migrations..."
python manage.py migrate

# Collect static files
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser prompt
echo ""
echo "👤 Do you want to create a superuser account? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "� Project Structure:"
echo "   🌐 Web App: Root directory (Django)"
echo "   📜 Legacy Scripts: legacy/ folder"
echo "   📁 Downloads: downloads/ folder"
echo ""
echo "🚀 To start the web application:"
echo "   python manage.py runserver"
echo ""
echo "🌐 Then visit:"
echo "   • Main App: http://127.0.0.1:8000"  
echo "   • Admin Panel: http://127.0.0.1:8000/admin"
echo ""
echo "📜 To use legacy Python scripts:"
echo "   cd legacy && python music_script.py"
echo ""
