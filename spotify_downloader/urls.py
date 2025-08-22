"""
URL configuration for spotify_downloader project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('playlist_app.api_urls')),  # API endpoints (playlist and audio)
    path('', include('playlist_app.urls')),          # Main app URLs (home page)
]
