// Client-side Spotify Playlist Downloader
class PlaylistDownloader {
    constructor() {
        this.currentPlaylist = null;
        this.currentTracks = [];
        this.selectedTracks = new Set();
        this.isDownloading = false;
        this.downloadSettings = {
            folderName: '',
            audioQuality: '192',
            namingPattern: 'artist-title',
            downloadPath: null
        };
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const playlistForm = document.getElementById('playlistForm');
        const downloadAllButton = document.getElementById('downloadAllButton');
        const selectAllButton = document.getElementById('selectAllButton');
        const chooseFolderButton = document.getElementById('chooseFolderButton');

        if (playlistForm) {
            playlistForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.loadPlaylist();
            });
        }

        if (downloadAllButton) {
            downloadAllButton.addEventListener('click', () => {
                this.downloadSelected();
            });
        }

        if (selectAllButton) {
            selectAllButton.addEventListener('click', () => {
                this.toggleSelectAll();
            });
        }

        if (chooseFolderButton) {
            chooseFolderButton.addEventListener('click', () => {
                this.chooseFolderPath();
            });
        }

        // Settings change listeners
        const folderNameInput = document.getElementById('folderName');
        const audioQualitySelect = document.getElementById('audioQuality');
        const namingPatternSelect = document.getElementById('namingPattern');

        if (folderNameInput) {
            folderNameInput.addEventListener('change', (e) => {
                this.downloadSettings.folderName = e.target.value;
            });
        }

        if (audioQualitySelect) {
            audioQualitySelect.addEventListener('change', (e) => {
                this.downloadSettings.audioQuality = e.target.value;
            });
        }

        if (namingPatternSelect) {
            namingPatternSelect.addEventListener('change', (e) => {
                this.downloadSettings.namingPattern = e.target.value;
            });
        }
    }

    async loadPlaylist() {
        const playlistUrl = document.getElementById('playlistUrl').value.trim();
        
        if (!playlistUrl) {
            this.showError('Please enter a Spotify playlist URL');
            return;
        }

        this.showLoading(true);
        this.hideError();
        this.hidePlaylist();

        try {
            // Use Django API for local dev, Vercel for production
            const response = await fetch('/api/download/playlist/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    playlist_url: playlistUrl
                })
            });

            const data = await response.json();

            if (!data.success && data.error) {
                throw new Error(data.error);
            }

            // Handle the response format
            this.currentPlaylist = {
                name: data.name,
                description: data.description,
                owner: data.owner,
                total_tracks: data.total_tracks,
                public: data.public
            };
            
            this.currentTracks = data.tracks;
            this.selectedTracks.clear();

            this.displayPlaylist();
            this.displayTracks();

        } catch (error) {
            console.error('Error loading playlist:', error);
            this.showError(error.message || 'Failed to load playlist');
        } finally {
            this.showLoading(false);
        }
    }

    displayPlaylist() {
        const playlistInfo = document.getElementById('playlistInfo');
        if (!playlistInfo || !this.currentPlaylist) return;

        playlistInfo.innerHTML = `
            <h2 class="text-2xl font-bold mb-2">${this.currentPlaylist.name}</h2>
            <p class="text-gray-400 mb-2">by ${this.currentPlaylist.owner}</p>
            <p class="text-gray-300">${this.currentPlaylist.total_tracks} tracks</p>
        `;
        
        this.showPlaylist();
    }

    displayTracks() {
        const tracksList = document.getElementById('tracksList');
        if (!tracksList) return;

        tracksList.innerHTML = '';

        this.currentTracks.forEach((track, index) => {
            const trackElement = this.createTrackElement(track, index);
            tracksList.appendChild(trackElement);
        });
    }

    createTrackElement(track, index) {
        const div = document.createElement('div');
        div.className = 'flex items-center p-4 border-b border-gray-700 hover:bg-gray-700 transition-colors';
        
        div.innerHTML = `
            <input type="checkbox" 
                   class="mr-3 h-4 w-4 text-green-600 rounded" 
                   data-track-id="${track.id}"
                   onchange="downloader.toggleTrackSelection('${track.id}')">
            <div class="flex-1">
                <div class="font-medium text-white">${track.name}</div>
                <div class="text-sm text-gray-400">${track.artist}</div>
            </div>
            <div class="text-right">
                <div class="text-sm text-gray-400">${this.formatDuration(track.duration_ms)}</div>
                ${track.preview_url ? 
                    `<button onclick="downloader.playPreview('${track.preview_url}')" 
                             class="text-green-500 hover:text-green-400 text-sm">▶ Preview</button>` : 
                    '<span class="text-gray-500 text-sm">No preview</span>'
                }
            </div>
        `;

        return div;
    }

    toggleTrackSelection(trackId) {
        if (this.selectedTracks.has(trackId)) {
            this.selectedTracks.delete(trackId);
        } else {
            this.selectedTracks.add(trackId);
        }
        
        this.updateDownloadButton();
    }

    toggleSelectAll() {
        const checkboxes = document.querySelectorAll('input[data-track-id]');
        const allSelected = this.selectedTracks.size === this.currentTracks.length;

        if (allSelected) {
            this.selectedTracks.clear();
            checkboxes.forEach(cb => cb.checked = false);
        } else {
            this.selectedTracks.clear();
            this.currentTracks.forEach(track => this.selectedTracks.add(track.id));
            checkboxes.forEach(cb => cb.checked = true);
        }

        this.updateDownloadButton();
    }

    updateDownloadButton() {
        const downloadButton = document.getElementById('downloadAllButton');
        const selectAllButton = document.getElementById('selectAllButton');
        
        if (downloadButton) {
            downloadButton.disabled = this.selectedTracks.size === 0;
            downloadButton.textContent = `Download Selected (${this.selectedTracks.size})`;
        }

        if (selectAllButton) {
            const allSelected = this.selectedTracks.size === this.currentTracks.length;
            selectAllButton.textContent = allSelected ? 'Deselect All' : 'Select All';
        }
    }

    async chooseFolderPath() {
        try {
            if ('showDirectoryPicker' in window) {
                const directoryHandle = await window.showDirectoryPicker();
                this.downloadSettings.downloadPath = directoryHandle;
                
                const folderDisplay = document.getElementById('selectedFolderDisplay');
                if (folderDisplay) {
                    folderDisplay.textContent = `Selected: ${directoryHandle.name}`;
                    folderDisplay.style.display = 'block';
                }
                
                this.showNotification('Download folder selected!', 'success');
            } else {
                this.showNotification('Folder selection not supported in this browser. Files will download to your default Downloads folder.', 'warning');
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Error selecting folder:', error);
                this.showNotification('Error selecting folder', 'error');
            }
        }
    }

    async downloadSelected() {
        if (this.selectedTracks.size === 0) {
            this.showError('Please select at least one track');
            return;
        }

        if (this.isDownloading) {
            this.showError('Download already in progress');
            return;
        }

        const selectedTracksData = this.currentTracks.filter(track => 
            this.selectedTracks.has(track.id)
        );

        await this.performDownload(selectedTracksData);
    }

    async performDownload(tracks) {
        this.isDownloading = true;
        let successful = 0;
        let failed = 0;

        try {
            // Create download folder if using File System Access API
            let downloadFolder = null;
            if (this.downloadSettings.downloadPath) {
                downloadFolder = await this.createDownloadFolder();
            }

            for (let i = 0; i < tracks.length; i++) {
                const track = tracks[i];
                
                try {
                    this.updateProgress(
                        ((i) / tracks.length) * 100,
                        successful,
                        failed,
                        `Downloading: ${track.artist} - ${track.name}`
                    );

                    await this.downloadTrackFromYouTube(track, downloadFolder);
                    successful++;
                    
                } catch (error) {
                    console.error(`Failed to download ${track.name}:`, error);
                    failed++;
                }
            }

            this.updateProgress(100, successful, failed, 'Download complete!');
            this.showNotification(`Download complete! ${successful} successful, ${failed} failed`, 'success');

        } catch (error) {
            console.error('Download error:', error);
            this.showError('Download failed: ' + error.message);
        } finally {
            this.isDownloading = false;
        }
    }

    async downloadTrackFromYouTube(track, downloadFolder = null) {
        const searchQuery = `${track.artist} ${track.name}`;
        const fileName = this.generateFileName(track);

        try {
            console.log(`Downloading audio for: ${searchQuery}`);
            
            // Call Django API for local dev, Vercel for production
            const response = await fetch('/api/download/audio/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: searchQuery,
                    quality: this.downloadSettings.audioQuality
                })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Download failed');
            }
            
            // Convert base64 audio data to blob
            const audioBytes = atob(data.audio_data);
            const audioArray = new Uint8Array(audioBytes.length);
            for (let i = 0; i < audioBytes.length; i++) {
                audioArray[i] = audioBytes.charCodeAt(i);
            }
            const audioBlob = new Blob([audioArray], { type: 'audio/mpeg' });
            
            // Trigger download with real audio data
            await this.triggerDownloadWithFolder(fileName, downloadFolder, audioBlob);
            
            console.log(`Successfully downloaded: ${fileName}`);
            return true;
            
        } catch (error) {
            console.error(`Failed to download ${fileName}:`, error);
            throw error;
        }
    }

    async triggerDownloadWithFolder(filename, downloadFolder, audioBlob) {
        if (!audioBlob || audioBlob.size === 0) {
            throw new Error('No audio data received');
        }
        
        if (downloadFolder && 'createWritable' in FileSystemFileHandle.prototype) {
            try {
                const fileHandle = await downloadFolder.getFileHandle(`${filename}.mp3`, { create: true });
                const writable = await fileHandle.createWritable();
                await writable.write(audioBlob);
                await writable.close();
                
                console.log(`File saved to selected folder: ${filename}.mp3`);
                return;
            } catch (error) {
                console.error('Error saving to folder, falling back to browser download:', error);
            }
        }
        
        // Fallback to browser download
        const url = URL.createObjectURL(audioBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}.mp3`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        console.log(`File downloaded: ${filename}.mp3`);
    }

    generateFileName(track) {
        switch (this.downloadSettings.namingPattern) {
            case 'title-artist':
                return `${track.name} - ${track.artist}`;
            case 'artist-title':
            default:
                return `${track.artist} - ${track.name}`;
        }
    }

    async createDownloadFolder() {
        if (!this.downloadSettings.downloadPath) return null;

        try {
            const folderName = this.downloadSettings.folderName || 'spotify-downloads';
            return await this.downloadSettings.downloadPath.getDirectoryHandle(folderName, { create: true });
        } catch (error) {
            console.error('Error creating download folder:', error);
            return null;
        }
    }

    formatDuration(ms) {
        const minutes = Math.floor(ms / 60000);
        const seconds = Math.floor((ms % 60000) / 1000);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    updateProgress(percentage, successful, failed, currentTrack = '') {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const progressStats = document.getElementById('progressStats');

        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
        }

        if (progressText) {
            progressText.textContent = currentTrack;
        }

        if (progressStats) {
            progressStats.textContent = `Success: ${successful}, Failed: ${failed}`;
        }
    }

    showNotification(message, type = 'info') {
        // Simple console notification for now
        console.log(`${type.toUpperCase()}: ${message}`);
        
        // You can implement a proper notification system here
        if (type === 'error') {
            this.showError(message);
        }
    }

    playPreview(previewUrl) {
        if (this.currentAudio) {
            this.currentAudio.pause();
        }

        this.currentAudio = new Audio(previewUrl);
        this.currentAudio.play();

        setTimeout(() => {
            if (this.currentAudio) {
                this.currentAudio.pause();
            }
        }, 30000);
    }

    // Utility methods
    showLoading(show) {
        const button = document.getElementById('loadButton');
        if (button) {
            button.disabled = show;
            button.innerHTML = show ? 
                '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...' : 
                '<i class="fas fa-search mr-2"></i>Load Playlist';
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }

    hideError() {
        const errorDiv = document.getElementById('errorMessage');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    showPlaylist() {
        const playlistContainer = document.getElementById('playlistContainer');
        if (playlistContainer) {
            playlistContainer.style.display = 'block';
        }
    }

    hidePlaylist() {
        const playlistContainer = document.getElementById('playlistContainer');
        if (playlistContainer) {
            playlistContainer.style.display = 'none';
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// Initialize the downloader when the page loads
let downloader;
document.addEventListener('DOMContentLoaded', function() {
    downloader = new PlaylistDownloader();
});
