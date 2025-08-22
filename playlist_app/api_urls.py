"""
API URLs for local development
Mirrors the Vercel serverless function endpoints
"""
from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    # Mirror Vercel serverless function endpoints
    path('download/playlist/', api_views.playlist_api, name='playlist_api'),
    path('download/audio/', api_views.audio_api, name='audio_api'),
]
