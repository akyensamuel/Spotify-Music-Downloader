# 🚀 Deployment Guide - Reorganized Project

Complete deployment guide for the reorganized Spotify Playlist Downloader project.

## 📁 New Project Structure

The project has been reorganized with:
- **Django web app** at the root level (production-ready)
- **Legacy Python scripts** in `legacy/` folder (for local use)
- **Consolidated requirements.txt** with all dependencies
- **Unified .gitignore** for the entire project

## 🌟 Quick Deploy Commands

### Heroku (One-click deploy)
```bash
# From project root
git add .
git commit -m "Deploy reorganized Django app"
heroku create your-spotify-downloader
heroku config:set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
heroku config:set SPOTIFY_CLIENT_ID="your-client-id"
heroku config:set SPOTIFY_CLIENT_SECRET="your-client-secret"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-app.herokuapp.com"
git push heroku main
heroku run python manage.py migrate
```

### Railway
```bash
# Connect GitHub repo to Railway dashboard
# Set these environment variables:
SECRET_KEY=your-secret-key
SPOTIFY_CLIENT_ID=your-client-id  
SPOTIFY_CLIENT_SECRET=your-client-secret
DEBUG=False
ALLOWED_HOSTS=your-app.up.railway.app
```

### Render
```bash
# Connect GitHub repo to Render
# Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
# Start Command: gunicorn spotify_downloader.wsgi:application
```

## 📋 Pre-deployment Checklist

- [ ] **Repository organized**: Django app at root, legacy scripts in `legacy/`
- [ ] **Requirements merged**: Single `requirements.txt` with all dependencies
- [ ] **Environment variables**: All secrets in `.env` or hosting platform
- [ ] **Static files**: `python manage.py collectstatic` works
- [ ] **Database migrations**: All migrations created and tested
- [ ] **Spotify API**: Redirect URI updated to production URL

## 🔧 Environment Variables

### Required Variables
```bash
SECRET_KEY=your-django-secret-key-here
SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### Optional Variables
```bash
DATABASE_URL=postgres://user:pass@host:port/db  # For PostgreSQL
REDIS_URL=redis://host:port/0                   # For caching
```

## 🗂️ File Structure Reference

```
Spotify Downloader/                  # ← Root is now the Django project
├── manage.py                        # Django management
├── requirements.txt                 # Merged dependencies  
├── Procfile                         # Heroku config
├── setup.sh / setup.bat            # Development setup
├── .env                             # Local environment variables
├── .gitignore                       # Comprehensive ignore rules
│
├── spotify_downloader/              # Django project settings
├── playlist_app/                    # Main Django app
├── templates/                       # HTML templates  
├── static/                          # Frontend assets
│
├── legacy/                          # ← Original Python scripts
│   ├── music_script.py
│   ├── music_script_user_auth.py
│   └── README.md
│
├── downloads/                       # Downloaded music files
├── virtual/                         # Python virtual environment
└── README.md                        # Project documentation
```

## 🔄 Migration from Old Structure

If you're updating an existing deployment:

### 1. Update Repository
```bash
git pull origin main  # Get the reorganized structure
```

### 2. Update Deployment Settings
- **Build Command**: No change needed
- **Start Command**: `gunicorn spotify_downloader.wsgi:application` (no change)
- **Environment Variables**: Same as before

### 3. Re-deploy
Most platforms will automatically detect the changes and redeploy.

## 🎯 Platform-Specific Notes

### Heroku
- **Procfile** already configured at root level
- **Static files** handled automatically with Django
- **Database** uses SQLite by default, PostgreSQL available

### Railway
- **Auto-detection** works with manage.py at root
- **Environment variables** set in dashboard
- **Custom domains** available on paid plans

### Render
- **Build detection** automatic with manage.py
- **Static files** must be collected in build command
- **PostgreSQL** available as add-on

### Vercel (Serverless)
- **Serverless functions** work with reorganized structure  
- **Static files** served from `/static/`
- **Database** should use external service

## 🧪 Testing Deployment

### Local Production Test
```bash
# Test with production settings
DEBUG=False python manage.py runserver --insecure
```

### Health Check
```bash
curl https://your-app.herokuapp.com/health/
# Should return: {"status": "healthy", "timestamp": "..."}
```

## 🔍 Troubleshooting

### Common Issues After Reorganization

#### 1. **Import Errors**
- Make sure `spotify_downloader.settings` is in `DJANGO_SETTINGS_MODULE`
- Check that manage.py is at the root level

#### 2. **Static Files Not Loading**
```bash
python manage.py collectstatic --clear --noinput
```

#### 3. **Database Errors**
```bash
python manage.py migrate --run-syncdb
```

#### 4. **Environment Variables**
- Verify all environment variables are set correctly
- Check that `.env` file exists for local development

### Legacy Scripts Still Work
```bash
cd legacy
python music_script.py  # Original functionality preserved
```

## 📈 Benefits of New Structure

✅ **Simplified deployment** - Django app at root level  
✅ **Consolidated dependencies** - Single requirements.txt  
✅ **Better organization** - Clear separation of web app vs scripts  
✅ **Preserved legacy** - Original scripts still functional  
✅ **Production ready** - Optimized for hosting platforms  

## 🎉 Ready to Deploy!

Your reorganized Spotify Playlist Downloader is now optimized for deployment while preserving all original functionality. The web application provides a modern interface while the legacy scripts remain available for advanced users.

Choose your hosting platform and deploy with confidence! 🚀
