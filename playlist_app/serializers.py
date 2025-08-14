from rest_framework import serializers
from .models import Playlist, Track, DownloadSession


class TrackSerializer(serializers.ModelSerializer):
    search_query = serializers.ReadOnlyField()
    duration_formatted = serializers.ReadOnlyField()
    
    class Meta:
        model = Track
        fields = [
            'id', 'title', 'artist', 'album', 'duration_ms', 
            'duration_formatted', 'spotify_id', 'preview_url', 
            'search_query', 'youtube_search_query'
        ]


class PlaylistSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True, read_only=True)
    
    class Meta:
        model = Playlist
        fields = [
            'id', 'spotify_url', 'spotify_id', 'title', 'owner', 
            'total_tracks', 'is_public', 'created_at', 'updated_at', 
            'tracks'
        ]


class DownloadSessionSerializer(serializers.ModelSerializer):
    playlist_title = serializers.CharField(source='playlist.title', read_only=True)
    
    class Meta:
        model = DownloadSession
        fields = [
            'id', 'session_id', 'playlist', 'playlist_title',
            'tracks_processed', 'tracks_successful', 'tracks_failed',
            'status', 'created_at', 'completed_at'
        ]
