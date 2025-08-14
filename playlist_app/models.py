from django.db import models


class Playlist(models.Model):
    """Model to store playlist information"""
    spotify_url = models.URLField(max_length=500)
    spotify_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=300)
    owner = models.CharField(max_length=200)
    total_tracks = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.owner}"


class Track(models.Model):
    """Model to store individual track information"""
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='tracks')
    title = models.CharField(max_length=300)
    artist = models.CharField(max_length=300)
    album = models.CharField(max_length=300, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    spotify_id = models.CharField(max_length=100)
    preview_url = models.URLField(blank=True, null=True)
    
    # Fields for YouTube data (populated client-side)
    youtube_search_query = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.title} by {self.artist}"
    
    @property 
    def search_query(self):
        """Generate search query for YouTube"""
        return f"{self.artist} {self.title}"
    
    @property
    def duration_formatted(self):
        """Format duration from milliseconds to mm:ss"""
        if self.duration_ms:
            seconds = self.duration_ms // 1000
            minutes = seconds // 60
            seconds = seconds % 60
            return f"{minutes}:{seconds:02d}"
        return "Unknown"


class DownloadSession(models.Model):
    """Model to track download sessions"""
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    tracks_processed = models.IntegerField(default=0)
    tracks_successful = models.IntegerField(default=0)
    tracks_failed = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Download session for {self.playlist.title}"
