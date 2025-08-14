from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json
from .models import Playlist, Track, DownloadSession


class PlaylistAppTestCase(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.playlist_data = {
            'spotify_url': 'https://open.spotify.com/playlist/test123',
            'spotify_id': 'test123',
            'title': 'Test Playlist',
            'owner': 'Test User',
            'total_tracks': 2,
            'is_public': True
        }
        
    def test_index_view(self):
        """Test that the main page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Spotify Playlist Downloader')
        
    @patch('playlist_app.views.spotipy.Spotify')
    def test_get_playlist_tracks_success(self, mock_spotify):
        """Test successful playlist track fetching"""
        # Mock Spotify API response
        mock_sp = MagicMock()
        mock_spotify.return_value = mock_sp
        
        mock_sp.playlist.return_value = {
            'name': 'Test Playlist',
            'owner': {'display_name': 'Test User'},
            'tracks': {'total': 2},
            'public': True
        }
        
        mock_sp.playlist_tracks.return_value = {
            'items': [
                {
                    'track': {
                        'type': 'track',
                        'id': 'track1',
                        'name': 'Test Song 1',
                        'artists': [{'name': 'Artist 1'}],
                        'album': {'name': 'Album 1'},
                        'duration_ms': 180000,
                        'preview_url': 'http://example.com/preview1.mp3'
                    }
                },
                {
                    'track': {
                        'type': 'track',
                        'id': 'track2',
                        'name': 'Test Song 2',
                        'artists': [{'name': 'Artist 2'}],
                        'album': {'name': 'Album 2'},
                        'duration_ms': 200000,
                        'preview_url': None
                    }
                }
            ],
            'next': None
        }
        
        mock_sp.next.return_value = None
        
        # Make request
        response = self.client.post(
            reverse('get_playlist_tracks'),
            data=json.dumps({'playlist_url': 'https://open.spotify.com/playlist/test123'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Verify response structure
        self.assertIn('playlist', data)
        self.assertIn('tracks', data)
        self.assertEqual(data['playlist']['title'], 'Test Playlist')
        self.assertEqual(len(data['tracks']), 2)
        
        # Verify database records were created
        self.assertTrue(Playlist.objects.filter(spotify_id='test123').exists())
        self.assertEqual(Track.objects.count(), 2)
        
    def test_get_playlist_tracks_missing_url(self):
        """Test playlist tracks endpoint with missing URL"""
        response = self.client.post(
            reverse('get_playlist_tracks'),
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)
        
    def test_create_download_session(self):
        """Test creating a download session"""
        # Create a playlist first
        playlist = Playlist.objects.create(**self.playlist_data)
        
        response = self.client.post(
            reverse('create_download_session'),
            data=json.dumps({'playlist_id': playlist.id}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('session_id', data)
        self.assertIn('playlist_title', data)
        self.assertEqual(data['playlist_title'], 'Test Playlist')
        
        # Verify session was created in database
        self.assertTrue(DownloadSession.objects.filter(session_id=data['session_id']).exists())
        
    def test_update_download_progress(self):
        """Test updating download session progress"""
        # Create playlist and session
        playlist = Playlist.objects.create(**self.playlist_data)
        session = DownloadSession.objects.create(
            playlist=playlist,
            session_id='test-session-123'
        )
        
        # Update progress
        progress_data = {
            'tracks_processed': 1,
            'tracks_successful': 1,
            'tracks_failed': 0,
            'status': 'processing'
        }
        
        response = self.client.post(
            reverse('update_download_progress', kwargs={'session_id': session.session_id}),
            data=json.dumps(progress_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify database was updated
        session.refresh_from_db()
        self.assertEqual(session.tracks_processed, 1)
        self.assertEqual(session.tracks_successful, 1)
        self.assertEqual(session.status, 'processing')


class ModelTestCase(TestCase):
    
    def setUp(self):
        self.playlist = Playlist.objects.create(
            spotify_url='https://open.spotify.com/playlist/test123',
            spotify_id='test123',
            title='Test Playlist',
            owner='Test User',
            total_tracks=1
        )
        
    def test_playlist_str(self):
        """Test playlist string representation"""
        self.assertEqual(str(self.playlist), 'Test Playlist by Test User')
        
    def test_track_creation(self):
        """Test track creation and properties"""
        track = Track.objects.create(
            playlist=self.playlist,
            title='Test Song',
            artist='Test Artist',
            album='Test Album',
            duration_ms=180000,
            spotify_id='track123'
        )
        
        self.assertEqual(str(track), 'Test Song by Test Artist')
        self.assertEqual(track.search_query, 'Test Artist Test Song')
        self.assertEqual(track.duration_formatted, '3:00')
        
    def test_download_session_creation(self):
        """Test download session creation"""
        session = DownloadSession.objects.create(
            playlist=self.playlist,
            session_id='test-session'
        )
        
        self.assertEqual(str(session), 'Download session for Test Playlist')
        self.assertEqual(session.status, 'pending')
        self.assertEqual(session.tracks_processed, 0)
