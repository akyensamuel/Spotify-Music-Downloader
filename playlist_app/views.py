import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from .models import Playlist, Track, DownloadSession
from .serializers import PlaylistSerializer, TrackSerializer


def index(request):
    """Main page with the client-side downloader interface"""
    return render(request, 'index.html')


def create_spotify_client():
    """Create Spotify client with client credentials flow"""
    auth_manager = SpotifyClientCredentials(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def extract_playlist_id(playlist_url):
    """Extract playlist ID from Spotify URL"""
    if "playlist/" in playlist_url:
        return playlist_url.split("playlist/")[1].split("?")[0]
    return playlist_url  # Assume it's already an ID


@api_view(['POST'])
def get_playlist_tracks(request):
    """API endpoint to get playlist tracks from Spotify"""
    try:
        data = request.data
        playlist_url = data.get('playlist_url', '').strip()
        
        if not playlist_url:
            return Response(
                {'error': 'Playlist URL is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        playlist_id = extract_playlist_id(playlist_url)
        sp = create_spotify_client()
        
        # Check if playlist already exists in database
        existing_playlist = Playlist.objects.filter(spotify_id=playlist_id).first()
        if existing_playlist:
            serializer = PlaylistSerializer(existing_playlist)
            return Response({
                'playlist': serializer.data,
                'tracks': TrackSerializer(existing_playlist.tracks.all(), many=True).data
            })
        
        # Get playlist info from Spotify
        try:
            playlist_info = sp.playlist(playlist_id)
        except spotipy.exceptions.SpotifyException as e:
            return Response(
                {'error': f'Playlist not found or not accessible: {str(e)}'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create playlist record
        playlist = Playlist.objects.create(
            spotify_url=playlist_url,
            spotify_id=playlist_id,
            title=playlist_info['name'],
            owner=playlist_info['owner']['display_name'],
            total_tracks=playlist_info['tracks']['total'],
            is_public=playlist_info.get('public', True)
        )
        
        # Get all tracks
        tracks_data = []
        results = sp.playlist_tracks(playlist_id)
        track_objects = []
        
        while results:
            for item in results['items']:
                track_info = item.get('track')
                if track_info and track_info['type'] == 'track':
                    # Create track object
                    track = Track(
                        playlist=playlist,
                        title=track_info['name'],
                        artist=', '.join([artist['name'] for artist in track_info['artists']]),
                        album=track_info['album']['name'],
                        duration_ms=track_info.get('duration_ms'),
                        spotify_id=track_info['id'],
                        preview_url=track_info.get('preview_url'),
                        youtube_search_query=f"{', '.join([artist['name'] for artist in track_info['artists']])} {track_info['name']}"
                    )
                    track_objects.append(track)
            
            # Get next page
            results = sp.next(results) if results['next'] else None
        
        # Bulk create tracks
        Track.objects.bulk_create(track_objects)
        
        # Update playlist track count
        playlist.total_tracks = len(track_objects)
        playlist.save()
        
        # Return playlist and tracks data
        playlist_serializer = PlaylistSerializer(playlist)
        track_serializer = TrackSerializer(track_objects, many=True)
        
        return Response({
            'playlist': playlist_serializer.data,
            'tracks': track_serializer.data
        })
        
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def create_download_session(request):
    """Create a new download session"""
    try:
        data = request.data
        playlist_id = data.get('playlist_id')
        
        if not playlist_id:
            return Response(
                {'error': 'Playlist ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            playlist = Playlist.objects.get(id=playlist_id)
        except Playlist.DoesNotExist:
            return Response(
                {'error': 'Playlist not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create download session
        session = DownloadSession.objects.create(
            playlist=playlist,
            session_id=str(uuid.uuid4()),
            status='pending'
        )
        
        return Response({
            'session_id': session.session_id,
            'playlist_title': playlist.title,
            'total_tracks': playlist.total_tracks,
            'status': session.status
        })
        
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_download_session(request, session_id):
    """Get download session status"""
    try:
        session = DownloadSession.objects.get(session_id=session_id)
        return Response({
            'session_id': session.session_id,
            'playlist_title': session.playlist.title,
            'total_tracks': session.playlist.total_tracks,
            'tracks_processed': session.tracks_processed,
            'tracks_successful': session.tracks_successful,
            'tracks_failed': session.tracks_failed,
            'status': session.status,
            'created_at': session.created_at,
            'completed_at': session.completed_at
        })
    except DownloadSession.DoesNotExist:
        return Response(
            {'error': 'Download session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def update_download_progress(request, session_id):
    """Update download progress from client-side"""
    try:
        session = DownloadSession.objects.get(session_id=session_id)
        data = request.data
        
        session.tracks_processed = data.get('tracks_processed', session.tracks_processed)
        session.tracks_successful = data.get('tracks_successful', session.tracks_successful)
        session.tracks_failed = data.get('tracks_failed', session.tracks_failed)
        session.status = data.get('status', session.status)
        
        if session.status == 'completed':
            from django.utils import timezone
            session.completed_at = timezone.now()
        
        session.save()
        
        return Response({'success': True})
        
    except DownloadSession.DoesNotExist:
        return Response(
            {'error': 'Download session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
