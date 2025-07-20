// YouTube Downloader App JavaScript

class YouTubeDownloader {
    constructor() {
        this.currentDownload = null;
        this.activeDownloads = new Map();
        this.pollInterval = null;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Search functionality
        document.getElementById('searchBtn').addEventListener('click', () => this.searchVideos());
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchVideos();
        });

        // Direct URL functionality
        document.getElementById('getInfoBtn').addEventListener('click', () => this.getVideoInfo());
        document.getElementById('urlInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.getVideoInfo();
        });

        // Download button
        document.getElementById('downloadBtn').addEventListener('click', () => this.startDownload());

        // Format selection change
        document.getElementById('formatSelect').addEventListener('change', () => this.updateQualityOptions());
    }

    async searchVideos() {
        const query = document.getElementById('searchInput').value.trim();
        if (!query) {
            this.showAlert('Please enter a search query', 'warning');
            return;
        }

        const resultsContainer = document.getElementById('searchResults');
        const loadingIndicator = document.getElementById('searchLoading');
        
        // Show loading
        resultsContainer.innerHTML = '';
        loadingIndicator.classList.remove('d-none');

        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Search failed');
            }

            this.displaySearchResults(data.results);
        } catch (error) {
            console.error('Search error:', error);
            this.showAlert(error.message, 'danger');
        } finally {
            loadingIndicator.classList.add('d-none');
        }
    }

    displaySearchResults(results) {
        const container = document.getElementById('searchResults');
        
        if (!results || results.length === 0) {
            container.innerHTML = '<div class="col-12 text-center text-muted">No videos found</div>';
            return;
        }

        container.innerHTML = results.map(video => `
            <div class="col-md-6 col-lg-4">
                <div class="card video-card h-100 fade-in-up" data-url="${video.url}">
                    <img src="${video.thumbnail || 'https://via.placeholder.com/320x180?text=No+Image'}" 
                         class="card-img-top" alt="${video.title}">
                    <div class="card-body p-2">
                        <h6 class="card-title" title="${video.title}">${video.title}</h6>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                <i class="fas fa-user"></i> ${video.uploader || 'Unknown'}
                            </small>
                            <small class="text-muted">
                                <i class="fas fa-clock"></i> ${video.duration || 'Unknown'}
                            </small>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mt-2">
                            <small class="text-muted">
                                <i class="fas fa-eye"></i> ${this.formatNumber(video.view_count)} views
                            </small>
                            <button class="btn btn-primary btn-sm" onclick="app.selectVideo('${video.url}')">
                                <i class="fas fa-download"></i> Select
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async selectVideo(url) {
        document.getElementById('urlInput').value = url;
        await this.getVideoInfo();
        
        // Scroll to video info section
        document.getElementById('videoInfo').scrollIntoView({ behavior: 'smooth' });
    }

    async getVideoInfo() {
        const url = document.getElementById('urlInput').value.trim();
        if (!url) {
            this.showAlert('Please enter a YouTube URL', 'warning');
            return;
        }

        const getInfoBtn = document.getElementById('getInfoBtn');
        const originalText = getInfoBtn.innerHTML;
        
        // Show loading
        getInfoBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        getInfoBtn.disabled = true;

        try {
            const response = await fetch('/video_info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to get video info');
            }

            this.displayVideoInfo(data);
        } catch (error) {
            console.error('Video info error:', error);
            this.showAlert(error.message, 'danger');
        } finally {
            getInfoBtn.innerHTML = originalText;
            getInfoBtn.disabled = false;
        }
    }

    displayVideoInfo(video) {
        // Update video info display
        document.getElementById('videoThumbnail').src = video.thumbnail || 'https://via.placeholder.com/320x180?text=No+Image';
        document.getElementById('videoTitle').textContent = video.title;
        document.getElementById('videoUploader').textContent = video.uploader || 'Unknown';
        document.getElementById('videoDuration').textContent = video.duration || 'Unknown';
        document.getElementById('videoViews').textContent = this.formatNumber(video.view_count);

        // Store video data
        this.currentVideo = video;

        // Update quality options
        this.updateQualityOptions();

        // Show video info
        document.getElementById('videoInfo').classList.remove('d-none');
    }

    updateQualityOptions() {
        const formatSelect = document.getElementById('formatSelect');
        const qualitySelect = document.getElementById('qualitySelect');
        
        if (!this.currentVideo) return;

        const isAudio = formatSelect.value === 'audio';
        const formats = isAudio ? this.currentVideo.audio_formats : this.currentVideo.video_formats;

        qualitySelect.innerHTML = '<option value="best">Best Quality</option>';
        
        if (formats && formats.length > 0) {
            formats.forEach(format => {
                const option = document.createElement('option');
                option.value = format.quality;
                option.textContent = `${format.quality} (${format.ext})`;
                qualitySelect.appendChild(option);
            });
        }
    }

    async startDownload() {
        if (!this.currentVideo) {
            this.showAlert('Please select a video first', 'warning');
            return;
        }

        const url = document.getElementById('urlInput').value.trim();
        const format = document.getElementById('formatSelect').value;
        const quality = document.getElementById('qualitySelect').value;

        const downloadBtn = document.getElementById('downloadBtn');
        const originalText = downloadBtn.innerHTML;
        
        downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
        downloadBtn.disabled = true;

        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, format, quality })
            });

            if (response.ok) {
                // Create download link for the file
                const blob = await response.blob();
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                
                // Set filename based on format
                const extension = format === 'audio' ? 'mp3' : 'mp4';
                a.download = `${this.currentVideo.title.replace(/[^a-zA-Z0-9]/g, '_')}.${extension}`;
                
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                document.body.removeChild(a);
                
                this.showAlert('Download completed successfully!', 'success');
            } else {
                const data = await response.json();
                throw new Error(data.error || 'Download failed');
            }
            
        } catch (error) {
            console.error('Download error:', error);
            this.showAlert(error.message, 'danger');
        } finally {
            downloadBtn.innerHTML = originalText;
            downloadBtn.disabled = false;
        }
    }

    showProgressModal(downloadId) {
        // Set up progress modal
        document.getElementById('progressTitle').textContent = this.currentVideo.title;
        document.getElementById('progressBar').style.width = '0%';
        document.getElementById('progressBar').textContent = '0%';
        document.getElementById('progressStatus').textContent = 'Starting...';
        document.getElementById('progressSpeed').textContent = '-';
        document.getElementById('progressSize').textContent = '-';

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('progressModal'));
        modal.show();

        // Store current download and start polling
        this.currentDownload = downloadId;
        this.startPolling(downloadId);
    }

    startPolling(downloadId) {
        // Clear any existing polling
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }

        // Poll every 2 seconds
        this.pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/poll_progress/${downloadId}`);
                const data = await response.json();
                this.updateDownloadProgress(data);

                // Stop polling if download is completed or failed
                if (data.status === 'completed' || data.status === 'failed') {
                    clearInterval(this.pollInterval);
                    this.pollInterval = null;
                }
            } catch (error) {
                console.error('Polling error:', error);
            }
        }, 2000);
    }

    updateDownloadProgress(data) {
        const { download_id, status, progress, error } = data;
        
        // Update progress modal if it's the current download
        if (this.currentDownload === download_id) {
            const progressBar = document.getElementById('progressBar');
            const progressStatus = document.getElementById('progressStatus');

            progressBar.style.width = `${progress}%`;
            progressBar.textContent = `${progress}%`;
            progressStatus.textContent = status.charAt(0).toUpperCase() + status.slice(1);

            if (status === 'completed') {
                progressBar.classList.remove('progress-bar-animated');
                progressBar.classList.add('bg-success');
                this.showAlert('Download completed successfully!', 'success');
                setTimeout(() => {
                    const modalElement = document.getElementById('progressModal');
                    const modalInstance = bootstrap.Modal.getInstance(modalElement);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }, 2000);
                this.refreshRecentDownloads();
            } else if (status === 'failed') {
                progressBar.classList.remove('progress-bar-animated');
                progressBar.classList.add('bg-danger');
                progressStatus.textContent = `Failed: ${error || 'Unknown error'}`;
                this.showAlert(`Download failed: ${error || 'Unknown error'}`, 'danger');
            }
        }

        // Update active downloads sidebar
        this.updateActiveDownloads(data);
    }

    updateActiveDownloads(data) {
        const container = document.getElementById('activeDownloads');
        
        if (data.status === 'completed' || data.status === 'failed') {
            this.activeDownloads.delete(data.download_id);
        } else {
            this.activeDownloads.set(data.download_id, data);
        }

        if (this.activeDownloads.size === 0) {
            container.innerHTML = '<p class="text-muted text-center">No active downloads</p>';
        } else {
            container.innerHTML = Array.from(this.activeDownloads.values()).map(download => `
                <div class="download-item p-2 mb-2 rounded">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <small class="fw-bold">Download #${download.download_id}</small>
                        <span class="status-indicator status-${download.status}"></span>
                    </div>
                    <div class="progress mb-1" style="height: 4px;">
                        <div class="progress-bar" style="width: ${download.progress}%"></div>
                    </div>
                    <small class="text-muted">${download.status.charAt(0).toUpperCase() + download.status.slice(1)} - ${download.progress}%</small>
                </div>
            `).join('');
        }
    }

    async refreshRecentDownloads() {
        try {
            const response = await fetch('/downloads');
            const downloads = await response.json();
            
            const container = document.getElementById('recentDownloads');
            
            if (downloads.length === 0) {
                container.innerHTML = '<p class="text-muted text-center">No recent downloads</p>';
                return;
            }

            container.innerHTML = downloads.slice(0, 10).map(download => `
                <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-light rounded">
                    <div>
                        <small class="fw-bold">${download.title.substring(0, 50)}${download.title.length > 50 ? '...' : ''}</small>
                        <br>
                        <small class="text-muted">
                            <i class="fas fa-${download.status === 'completed' ? 'check-circle text-success' : 
                                              download.status === 'failed' ? 'times-circle text-danger' : 
                                              'spinner fa-spin text-primary'}"></i>
                            ${download.status.charAt(0).toUpperCase() + download.status.slice(1)}
                        </small>
                    </div>
                    ${download.status === 'completed' ? `
                        <a href="/download_file/${download.id}" class="btn btn-sm btn-outline-primary">
                            <i class="fas fa-download"></i>
                        </a>
                    ` : ''}
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Error refreshing downloads:', error);
        }
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.querySelector('.container');
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show mt-3`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        alertContainer.insertBefore(alert, alertContainer.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatSpeed(bytesPerSecond) {
        if (!bytesPerSecond) return '-';
        return this.formatBytes(bytesPerSecond) + '/s';
    }

    formatNumber(num) {
        if (!num) return '0';
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new YouTubeDownloader();
});
