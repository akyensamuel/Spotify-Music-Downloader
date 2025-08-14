"""
WSGI config for Vercel deployment
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotify_downloader.settings')

application = get_wsgi_application()
