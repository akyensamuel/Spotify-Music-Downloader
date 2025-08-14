// Client-side Spotify Playlist Downloader
class PlaylistDownloader {
    constructor() {
        this.currentPlaylist = null;
        this.currentTracks = [];
        this.selectedTracks = new Set();
        this.downloadSession = null;
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

        playlistForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.loadPlaylist();
        });

        downloadAllButton.addEventListener('click', () => {
            this.downloadSelected();
        });

        selectAllButton.addEventListener('click', () => {
            this.toggleSelectAll();
        });

        chooseFolderButton.addEventListener('click', () => {
            this.chooseFolderPath();
        });

        // Settings change listeners
        document.getElementById('folderName').addEventListener('change', (e) => {
            this.downloadSettings.folderName = e.target.value;
        });

        document.getElementById('audioQuality').addEventListener('change', (e) => {
            this.downloadSettings.audioQuality = e.target.value;
        });

        document.getElementById('namingPattern').addEventListener('change', (e) => {
            this.downloadSettings.namingPattern = e.target.value;
        });
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
            // Use Vercel serverless function for playlist processing
            const response = await fetch('/api/download/playlist', {
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

            // Adapt the response format
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
        const playlistDisplay = document.getElementById('playlistDisplay');
        const playlistTitle = document.getElementById('playlistTitle');
        const playlistOwner = document.getElementById('playlistOwner');
        const playlistStats = document.getElementById('playlistStats');

        playlistTitle.textContent = this.currentPlaylist.title;
        playlistOwner.textContent = `by ${this.currentPlaylist.owner}`;
        playlistStats.textContent = `${this.currentPlaylist.total_tracks} tracks • ${this.currentPlaylist.is_public ? 'Public' : 'Private'}`;

        playlistDisplay.classList.remove('hidden');
    }

    displayTracks() {
        const trackList = document.getElementById('trackList');
        trackList.innerHTML = '';

        this.currentTracks.forEach((track, index) => {
            const trackElement = this.createTrackElement(track, index);
            trackList.appendChild(trackElement);
        });

        this.updateSelectedCount();
    }

    createTrackElement(track, index) {
        const trackDiv = document.createElement('div');
        trackDiv.className = 'flex items-center p-4 hover:bg-gray-700 border-b border-gray-700 last:border-b-0';
        
        trackDiv.innerHTML = `
            <div class="flex items-center mr-4">
                <input 
                    type="checkbox" 
                    class="track-checkbox w-4 h-4 text-green-600 bg-gray-700 border-gray-600 rounded focus:ring-green-500" 
                    data-track-id="${track.id}"
                    ${this.selectedTracks.has(track.id) ? 'checked' : ''}
                >
            </div>
            <div class="flex-1">
                <div class="flex items-center justify-between">
                    <div>
                        <h4 class="font-medium">${this.escapeHtml(track.title)}</h4>
                        <p class="text-sm text-gray-400">${this.escapeHtml(track.artist)}</p>
                        <p class="text-xs text-gray-500">${this.escapeHtml(track.album)}</p>
                    </div>
                    <div class="flex items-center space-x-2">
                        ${track.duration_formatted ? `<span class="text-xs text-gray-500">${track.duration_formatted}</span>` : ''}
                        <button 
                            class="download-single-btn bg-green-600 hover:bg-green-700 px-3 py-1 rounded text-sm transition duration-200"
                            data-track-id="${track.id}"
                        >
                            <i class="fas fa-download"></i>
                        </button>
                        ${track.preview_url ? `
                            <button 
                                class="preview-btn bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition duration-200"
                                data-preview-url="${track.preview_url}"
                            >
                                <i class="fas fa-play"></i>
                            </button>
                        ` : ''}
                    </div>
                </div>
                <div class="download-status mt-2 hidden">
                    <div class="flex items-center text-sm">
                        <div class="status-icon mr-2"></div>
                        <span class="status-text"></span>
                    </div>
                </div>
            </div>
        `;

        // Add event listeners
        const checkbox = trackDiv.querySelector('.track-checkbox');
        const downloadBtn = trackDiv.querySelector('.download-single-btn');
        const previewBtn = trackDiv.querySelector('.preview-btn');

        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.selectedTracks.add(track.id);
            } else {
                this.selectedTracks.delete(track.id);
            }
            this.updateSelectedCount();
        });

        downloadBtn.addEventListener('click', () => {
            this.downloadSingleTrack(track);
        });

        if (previewBtn) {
            previewBtn.addEventListener('click', () => {
                this.playPreview(track.preview_url);
            });
        }

        return trackDiv;
    }

    async chooseFolderPath() {
        try {
            // Use File System Access API for modern browsers
            if ('showDirectoryPicker' in window) {
                const directoryHandle = await window.showDirectoryPicker({
                    mode: 'readwrite'
                });
                
                this.downloadSettings.downloadPath = directoryHandle;
                
                // Update UI to show selected folder
                const chooseFolderButton = document.getElementById('chooseFolderButton');
                chooseFolderButton.innerHTML = `<i class="fas fa-check mr-2"></i>Folder: ${directoryHandle.name}`;
                chooseFolderButton.classList.remove('bg-blue-600', 'hover:bg-blue-700');
                chooseFolderButton.classList.add('bg-green-600', 'hover:bg-green-700');
                
                // Show folder info
                this.showNotification(`Folder selected: ${directoryHandle.name}`, 'success');
                
            } else {
                // Fallback for browsers that don't support File System Access API
                this.showNotification('Folder selection not supported in this browser. Downloads will go to default location.', 'warning');
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Error selecting folder:', error);
                this.showNotification('Failed to select folder. Downloads will go to default location.', 'error');
            }
        }
    }

    generateFileName(track) {
        const sanitize = (str) => {
            return str.replace(/[<>:"/\\|?*]/g, '').replace(/\s+/g, ' ').trim();
        };

        const artist = sanitize(track.artist);
        const title = sanitize(track.title);

        switch (this.downloadSettings.namingPattern) {
            case 'title-artist':
                return `${title} - ${artist}`;
            case 'artist_title':
                return `${artist}_${title}`;
            case 'title':
                return title;
            case 'artist-title':
            default:
                return `${artist} - ${title}`;
        }
    }

    async createDownloadFolder() {
        if (!this.downloadSettings.downloadPath) {
            return null; // Use browser default download location
        }

        try {
            let folderName = this.downloadSettings.folderName || this.currentPlaylist?.title || 'Spotify Downloads';
            folderName = folderName.replace(/[<>:"/\\|?*]/g, '').trim();

            // Create subdirectory if folder name is specified
            if (folderName) {
                const folderHandle = await this.downloadSettings.downloadPath.getDirectoryHandle(folderName, {
                    create: true
                });
                return folderHandle;
            }

            return this.downloadSettings.downloadPath;
        } catch (error) {
            console.error('Error creating download folder:', error);
            this.showNotification('Could not create download folder. Using default location.', 'warning');
            return null;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg text-white z-50 transition-opacity duration-300 ${
            type === 'success' ? 'bg-green-600' :
            type === 'warning' ? 'bg-yellow-600' :
            type === 'error' ? 'bg-red-600' :
            'bg-blue-600'
        }`;
        
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${
                    type === 'success' ? 'fa-check-circle' :
                    type === 'warning' ? 'fa-exclamation-triangle' :
                    type === 'error' ? 'fa-times-circle' :
                    'fa-info-circle'
                } mr-2"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 5000);
    }

    async downloadSingleTrack(track) {
        if (this.isDownloading) {
            return;
        }

        await this.performDownload([track]);
    }

    async downloadSelected() {
        if (this.selectedTracks.size === 0) {
            this.showError('Please select at least one track to download');
            return;
        }

        if (this.isDownloading) {
            return;
        }

        const selectedTrackData = this.currentTracks.filter(track => 
            this.selectedTracks.has(track.id)
        );

        await this.performDownload(selectedTrackData);
    }

    async performDownload(tracks) {
        this.isDownloading = true;
        this.showDownloadProgress(true);
        
        try {
            // Create download folder if path is selected
            const downloadFolder = await this.createDownloadFolder();
            
            // Create download session
            const sessionResponse = await fetch('/api/download/session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    playlist_id: this.currentPlaylist.id
                })
            });

            if (!sessionResponse.ok) {
                throw new Error('Failed to create download session');
            }

            const sessionData = await sessionResponse.json();
            this.downloadSession = sessionData.session_id;

            let successful = 0;
            let failed = 0;

            // Download each track
            for (let i = 0; i < tracks.length; i++) {
                const track = tracks[i];
                const progress = ((i + 1) / tracks.length) * 100;
                
                this.updateProgress(progress, successful, failed, track.title);
                
                try {
                    await this.downloadTrackFromYouTube(track, downloadFolder);
                    successful++;
                    this.updateTrackStatus(track.id, 'success', 'Downloaded successfully');
                } catch (error) {
                    console.error(`Failed to download ${track.title}:`, error);
                    failed++;
                    this.updateTrackStatus(track.id, 'error', error.message);
                }

                // Update session progress
                await this.updateSessionProgress(i + 1, successful, failed);
                
                // Add delay to avoid overwhelming YouTube
                if (i < tracks.length - 1) {
                    await this.delay(2000);
                }
            }

            // Mark session as completed
            await this.updateSessionProgress(tracks.length, successful, failed, 'completed');
            
            this.updateProgress(100, successful, failed, 'Download completed');
            this.showNotification(`Download completed! ${successful} successful, ${failed} failed`, successful > 0 ? 'success' : 'warning');
            
        } catch (error) {
            console.error('Download error:', error);
            this.showError(`Download failed: ${error.message}`);
        } finally {
            this.isDownloading = false;
        }
    }

    async downloadTrackFromYouTube(track, downloadFolder = null) {
        // This is where client-side downloading happens
        // We'll use a combination of YouTube search and download functionality
        
        return new Promise(async (resolve, reject) => {
            try {
                const searchQuery = track.search_query;
                const fileName = this.generateFileName(track);
                
                // Simulate YouTube search and download
                await this.simulateYouTubeDownload(searchQuery, fileName, downloadFolder);
                
                resolve();
            } catch (error) {
                reject(new Error(`Failed to download "${track.title}": ${error.message}`));
            }
        });
    }

    async simulateYouTubeDownload(query, fileName, downloadFolder = null) {
        // Use Vercel serverless function for real audio processing
        try {
            console.log(`Downloading audio for: ${query}`);
            
            // Call Vercel serverless function
            const response = await fetch('/api/download/audio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
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
        // Handle real audio data instead of dummy content
        if (!audioBlob || audioBlob.size === 0) {
            throw new Error('No audio data received');
        }
        
        if (downloadFolder && 'createWritable' in FileSystemFileHandle.prototype) {
            try {
                // Use File System Access API to save to selected folder
                const fileHandle = await downloadFolder.getFileHandle(`${filename}.mp3`, { create: true });
                const writable = await fileHandle.createWritable();
                await writable.write(audioBlob);
                await writable.close();
                
                console.log(`File saved to selected folder: ${filename}.mp3`);
                return;
            } catch (error) {
                console.error('Error saving to folder, falling back to browser download:', error);
                // Fall through to browser download
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
        
        // Clean up object URL
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        
        console.log(`File downloaded: ${filename}.mp3`);
    }

    updateTrackStatus(trackId, status, message) {
        const trackElements = document.querySelectorAll(`[data-track-id="${trackId}"]`);
        trackElements.forEach(element => {
            const trackDiv = element.closest('.flex.items-center.p-4');
            if (trackDiv) {
                const statusDiv = trackDiv.querySelector('.download-status');
                const statusIcon = statusDiv.querySelector('.status-icon');
                const statusText = statusDiv.querySelector('.status-text');
                
                statusDiv.classList.remove('hidden');
                statusText.textContent = message;
                
                if (status === 'success') {
                    statusIcon.innerHTML = '<i class="fas fa-check-circle text-green-500"></i>';
                } else if (status === 'error') {
                    statusIcon.innerHTML = '<i class="fas fa-times-circle text-red-500"></i>';
                } else {
                    statusIcon.innerHTML = '<i class="fas fa-spinner fa-spin text-blue-500"></i>';
                }
            }
        });
    }

    async updateSessionProgress(processed, successful, failed, status = 'processing') {
        if (!this.downloadSession) return;

        try {
            await fetch(`/api/download/session/${this.downloadSession}/update/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    tracks_processed: processed,
                    tracks_successful: successful,
                    tracks_failed: failed,
                    status: status
                })
            });
        } catch (error) {
            console.error('Failed to update session progress:', error);
        }
    }

    updateProgress(percentage, successful, failed, currentTrack = '') {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const successCount = document.getElementById('successCount');
        const failCount = document.getElementById('failCount');
        const currentTrackElement = document.getElementById('currentTrack');

        progressBar.style.width = `${percentage}%`;
        progressText.textContent = `${Math.round(percentage)}%`;
        successCount.textContent = successful;
        failCount.textContent = failed;
        
        if (currentTrack) {
            currentTrackElement.textContent = currentTrack;
        }
    }

    toggleSelectAll() {
        const checkboxes = document.querySelectorAll('.track-checkbox');
        const selectAllButton = document.getElementById('selectAllButton');
        
        if (this.selectedTracks.size === this.currentTracks.length) {
            // Deselect all
            this.selectedTracks.clear();
            checkboxes.forEach(cb => cb.checked = false);
            selectAllButton.textContent = 'Select All';
        } else {
            // Select all
            this.selectedTracks.clear();
            this.currentTracks.forEach(track => this.selectedTracks.add(track.id));
            checkboxes.forEach(cb => cb.checked = true);
            selectAllButton.textContent = 'Deselect All';
        }
        
        this.updateSelectedCount();
    }

    updateSelectedCount() {
        const selectedCount = document.getElementById('selectedCount');
        const selectAllButton = document.getElementById('selectAllButton');
        
        selectedCount.textContent = this.selectedTracks.size;
        
        if (this.selectedTracks.size === this.currentTracks.length && this.currentTracks.length > 0) {
            selectAllButton.textContent = 'Deselect All';
        } else {
            selectAllButton.textContent = 'Select All';
        }
    }

    playPreview(previewUrl) {
        // Stop any currently playing audio
        if (this.currentAudio) {
            this.currentAudio.pause();
        }
        
        // Play new audio
        this.currentAudio = new Audio(previewUrl);
        this.currentAudio.play();
        
        // Auto-stop after 30 seconds
        setTimeout(() => {
            if (this.currentAudio) {
                this.currentAudio.pause();
            }
        }, 30000);
    }

    showLoading(show) {
        const loadingState = document.getElementById('loadingState');
        if (show) {
            loadingState.classList.remove('hidden');
        } else {
            loadingState.classList.add('hidden');
        }
    }

    showDownloadProgress(show) {
        const downloadProgress = document.getElementById('downloadProgress');
        if (show) {
            downloadProgress.classList.remove('hidden');
            this.updateProgress(0, 0, 0, 'Starting download...');
        } else {
            downloadProgress.classList.add('hidden');
        }
    }

    showError(message) {
        const errorState = document.getElementById('errorState');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorState.classList.remove('hidden');
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            this.hideError();
        }, 10000);
    }

    hideError() {
        const errorState = document.getElementById('errorState');
        errorState.classList.add('hidden');
    }

    hidePlaylist() {
        const playlistDisplay = document.getElementById('playlistDisplay');
        playlistDisplay.classList.add('hidden');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PlaylistDownloader();
});

// Note: For actual YouTube downloading, you would need to integrate:
// 1. YouTube Data API for searching videos
// 2. ytdl-core or similar library for extracting audio streams
// 3. Web Audio API for audio processing/conversion
// 4. File API for handling downloads
// 
// This implementation provides the framework and simulates the process.
