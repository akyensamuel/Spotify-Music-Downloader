# Django migrations
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spotify_url', models.URLField(max_length=500)),
                ('spotify_id', models.CharField(max_length=100, unique=True)),
                ('title', models.CharField(max_length=300)),
                ('owner', models.CharField(max_length=200)),
                ('total_tracks', models.IntegerField(default=0)),
                ('is_public', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DownloadSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=100, unique=True)),
                ('tracks_processed', models.IntegerField(default=0)),
                ('tracks_successful', models.IntegerField(default=0)),
                ('tracks_failed', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='playlist_app.playlist')),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('artist', models.CharField(max_length=300)),
                ('album', models.CharField(blank=True, max_length=300)),
                ('duration_ms', models.IntegerField(blank=True, null=True)),
                ('spotify_id', models.CharField(max_length=100)),
                ('preview_url', models.URLField(blank=True, null=True)),
                ('youtube_search_query', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='playlist_app.playlist')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
