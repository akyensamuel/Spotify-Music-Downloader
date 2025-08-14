"""
URL configuration for spotify_downloader project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('playlist_app.urls')),
    path('', include('playlist_app.urls')),
]
