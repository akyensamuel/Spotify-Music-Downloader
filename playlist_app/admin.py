from django.contrib import admin
from .models import Playlist, Track, DownloadSession


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'total_tracks', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['title', 'owner']
    readonly_fields = ['spotify_id', 'created_at', 'updated_at']


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'album', 'playlist', 'duration_formatted']
    list_filter = ['playlist', 'created_at']
    search_fields = ['title', 'artist', 'album']


@admin.register(DownloadSession)
class DownloadSessionAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'session_id', 'status', 'tracks_successful', 'tracks_failed', 'created_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['session_id', 'created_at']
