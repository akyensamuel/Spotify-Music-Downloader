from django.urls import path
from . import views

urlpatterns = [
    # Main page
    path('', views.index, name='index'),
    
    # API endpoints
    path('api/playlist/tracks/', views.get_playlist_tracks, name='get_playlist_tracks'),
    path('api/download/session/', views.create_download_session, name='create_download_session'),
    path('api/download/session/<str:session_id>/', views.get_download_session, name='get_download_session'),
    path('api/download/session/<str:session_id>/update/', views.update_download_progress, name='update_download_progress'),
]
