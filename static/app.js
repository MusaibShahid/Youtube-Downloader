// YouTube Downloader JavaScript
console.log('🎥 YouTube Downloader JS loaded successfully!');

// Test if all required elements exist
window.addEventListener('load', function() {
    console.log('🔍 Testing page elements...');
    
    const requiredElements = [
        'fetchInfoBtn',
        'downloadBtn', 
        'videoUrl',
        'progressiveStreams',
        'adaptiveStreams',
        'videoOnlyStreams',
        'audioStreams'
    ];
    
    const missing = [];
    requiredElements.forEach(id => {
        const element = document.getElementById(id);
        if (!element) {
            missing.push(id);
        }
    });
    
    if (missing.length > 0) {
        console.error('❌ Missing elements:', missing);
    } else {
        console.log('✅ All required elements found!');
    }
});

// Global variables
let currentVideoInfo = null;
let selectedStream = null;
let currentDownloadId = null;
let pollInterval = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    initializeApp();
});

function initializeApp() {
    // Get elements
    const fetchBtn = document.getElementById('fetchInfoBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const videoUrl = document.getElementById('videoUrl');
    
    if (!fetchBtn || !downloadBtn || !videoUrl) {
        console.error('Required elements not found!');
        return;
    }
    
    console.log('Elements found, setting up event listeners...');
    
    // Fetch video info button
    fetchBtn.addEventListener('click', handleFetchVideoInfo);
    
    // Download button
    downloadBtn.addEventListener('click', handleDownload);
    
    // Enter key support
    videoUrl.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleFetchVideoInfo();
        }
    });
    
    // Auto-focus URL input
    videoUrl.focus();
    
    console.log('App initialized successfully');
}

async function handleFetchVideoInfo() {
    console.log('=== FETCH VIDEO INFO STARTED ===');
    
    const url = document.getElementById('videoUrl').value.trim();
    const loadingIndicator = document.getElementById('loadingIndicator');
    const fetchBtn = document.getElementById('fetchInfoBtn');
    
    if (!url) {
        alert('Please enter a YouTube URL');
        return;
    }

    // Basic YouTube URL validation
    if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
        alert('Please enter a valid YouTube URL');
        return;
    }

    // Show loading
    loadingIndicator.style.display = 'block';
    fetchBtn.disabled = true;
    fetchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Fetching...';

    try {
        console.log('Sending request to fetch video info...');
        
        const response = await fetch('/fetch_video_info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();
        console.log('Response received:', data);

        if (data.success) {
            currentVideoInfo = data;
            displayVideoInfo(data);
            displayDownloadOptions(data);
        } else {
            console.error('Error fetching video info:', data.error);
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Network error:', error);
        alert('Error fetching video info: ' + error.message);
    } finally {
        loadingIndicator.style.display = 'none';
        fetchBtn.disabled = false;
        fetchBtn.innerHTML = '<i class="fas fa-search"></i> Fetch Video Info';
    }
}

function displayVideoInfo(data) {
    console.log('Displaying video info:', data.title);
    
    // Update video info elements
    document.getElementById('videoThumbnail').src = data.thumbnail;
    document.getElementById('videoTitle').textContent = data.title;
    document.getElementById('videoAuthor').textContent = data.author;
    document.getElementById('videoViews').textContent = data.views.toLocaleString();
    document.getElementById('videoDuration').textContent = formatDuration(data.length);
    document.getElementById('videoDescription').textContent = data.description;
    
    // Show video info card
    document.getElementById('videoInfoCard').style.display = 'block';
    
    console.log('Video info displayed successfully');
}

function displayDownloadOptions(data) {
    console.log('=== DISPLAYING DOWNLOAD OPTIONS ===');
    console.log('Video streams:', data.video_streams?.length || 0);
    console.log('Video only streams:', data.video_only_streams?.length || 0);
    console.log('Audio streams:', data.audio_streams?.length || 0);
    
    // Get all containers
    const containers = {
        progressive: document.getElementById('progressiveStreams'),
        adaptive: document.getElementById('adaptiveStreams'),
        videoOnly: document.getElementById('videoOnlyStreams'),
        audio: document.getElementById('audioStreams')
    };
    
    // Check if containers exist
    console.log('Container check:', {
        progressive: !!containers.progressive,
        adaptive: !!containers.adaptive,
        videoOnly: !!containers.videoOnly,
        audio: !!containers.audio
    });
    
    // Clear all containers
    Object.values(containers).forEach(container => {
        if (container) container.innerHTML = '';
    });
    
    // Add progressive streams (Video + Audio)
    if (containers.progressive && data.video_streams && data.video_streams.length > 0) {
        console.log('Adding progressive streams...');
        data.video_streams.forEach(stream => {
            const html = createStreamHTML(stream, 'progressive');
            containers.progressive.innerHTML += html;
        });
        console.log('Progressive streams added');
    } else if (containers.progressive) {
        containers.progressive.innerHTML = '<p class="text-muted">No progressive streams available</p>';
    }
    
    // Add adaptive streams (High Quality)
    if (containers.adaptive && data.video_only_streams && data.video_only_streams.length > 0) {
        console.log('Adding adaptive streams...');
        data.video_only_streams.forEach(stream => {
            const html = createStreamHTML(stream, 'adaptive');
            containers.adaptive.innerHTML += html;
        });
        console.log('Adaptive streams added');
    } else if (containers.adaptive) {
        containers.adaptive.innerHTML = '<p class="text-muted">No high-quality streams available</p>';
    }
    
    // Add video only streams
    if (containers.videoOnly && data.video_only_streams && data.video_only_streams.length > 0) {
        console.log('Adding video only streams...');
        data.video_only_streams.forEach(stream => {
            const html = createStreamHTML(stream, 'video_only', 'vo_');
            containers.videoOnly.innerHTML += html;
        });
        console.log('Video only streams added');
    } else if (containers.videoOnly) {
        containers.videoOnly.innerHTML = '<p class="text-muted">No video-only streams available</p>';
    }
    
    // Add audio streams
    if (containers.audio && data.audio_streams && data.audio_streams.length > 0) {
        console.log('Adding audio streams...');
        data.audio_streams.forEach(stream => {
            const html = createStreamHTML(stream, 'audio_only', 'audio_');
            containers.audio.innerHTML += html;
        });
        console.log('Audio streams added');
    } else if (containers.audio) {
        containers.audio.innerHTML = '<p class="text-muted">No audio streams available</p>';
    }
    
    // Add event listeners to all radio buttons
    setupStreamEventListeners();
    
    // Show download options card
    document.getElementById('downloadOptionsCard').style.display = 'block';
    
    console.log('=== DOWNLOAD OPTIONS SETUP COMPLETE ===');
}

function createStreamHTML(stream, type, prefix = '') {
    const quality = stream.resolution || stream.quality;
    const size = stream.size_mb;
    const fps = stream.fps ? ` (${stream.fps}fps)` : '';
    const id = `stream_${prefix}${stream.itag}`;
    
    return `
        <div class="form-check mb-2">
            <input class="form-check-input" type="radio" name="streamOption" 
                   value="${stream.itag}" data-type="${type}" id="${id}">
            <label class="form-check-label d-flex justify-content-between" for="${id}">
                <span>${quality}${fps}</span>
                <span class="text-muted">${size} MB</span>
            </label>
        </div>
    `;
}

function setupStreamEventListeners() {
    console.log('Setting up stream event listeners...');
    
    const radios = document.querySelectorAll('input[name="streamOption"]');
    console.log(`Found ${radios.length} radio buttons`);
    
    radios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                selectedStream = {
                    itag: this.value,
                    type: this.dataset.type
                };
                document.getElementById('downloadBtn').disabled = false;
                console.log('Stream selected:', selectedStream);
            }
        });
    });
    
    console.log('Event listeners setup complete');
}

async function handleDownload() {
    console.log('=== DOWNLOAD STARTED ===');
    
    if (!selectedStream) {
        alert('Please select a quality option');
        return;
    }

    const url = document.getElementById('videoUrl').value.trim();
    const location = document.getElementById('downloadLocation').value;

    console.log('Download parameters:', {
        url: url,
        itag: selectedStream.itag,
        type: selectedStream.type,
        location: location
    });

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                itag: selectedStream.itag,
                download_type: selectedStream.type,
                download_location: location
            })
        });

        const data = await response.json();
        console.log('Download response:', data);

        if (data.success) {
            currentDownloadId = data.download_id;
            showProgressCard();
            startProgressPolling();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Download error:', error);
        alert('Error starting download: ' + error.message);
    }
}

function showProgressCard() {
    document.getElementById('downloadOptionsCard').style.display = 'none';
    document.getElementById('progressCard').style.display = 'block';
}

function startProgressPolling() {
    console.log('Starting progress polling...');
    pollInterval = setInterval(updateProgress, 1000);
    updateProgress(); // Initial update
}

async function updateProgress() {
    try {
        const response = await fetch(`/progress/${currentDownloadId}`);
        const data = await response.json();

        const progressBar = document.getElementById('progressBar');
        const statusText = document.getElementById('statusText');
        const downloadSection = document.getElementById('downloadSection');
        const errorSection = document.getElementById('errorSection');

        // Update progress bar
        progressBar.style.width = data.progress + '%';
        progressBar.setAttribute('aria-valuenow', data.progress);
        progressBar.textContent = Math.round(data.progress) + '%';

        // Update status text and styling
        let statusMessage = '';
        let statusIcon = '';

        switch(data.status) {
            case 'starting':
                statusMessage = 'Starting download...';
                statusIcon = 'fas fa-spinner fa-spin';
                break;
            case 'downloading_audio':
                statusMessage = 'Downloading audio...';
                statusIcon = 'fas fa-music';
                progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-info';
                break;
            case 'downloading_video':
                statusMessage = 'Downloading video...';
                statusIcon = 'fas fa-video';
                progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-warning';
                break;
            case 'merging':
                statusMessage = 'Merging audio and video...';
                statusIcon = 'fas fa-cogs';
                progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated bg-primary';
                break;
            case 'completed':
                statusMessage = 'Download completed!';
                statusIcon = 'fas fa-check-circle text-success';
                progressBar.className = 'progress-bar bg-success';
                document.getElementById('downloadFileBtn').href = `/download_file/${currentDownloadId}`;
                downloadSection.style.display = 'block';
                clearInterval(pollInterval);
                break;
            default:
                if (data.status.startsWith('error:')) {
                    statusMessage = 'Download failed';
                    statusIcon = 'fas fa-exclamation-triangle text-danger';
                    progressBar.className = 'progress-bar bg-danger';
                    errorSection.style.display = 'block';
                    document.getElementById('errorMessage').textContent = data.status.substring(7);
                    clearInterval(pollInterval);
                } else {
                    statusMessage = 'Processing...';
                    statusIcon = 'fas fa-spinner fa-spin';
                }
        }

        statusText.innerHTML = `<i class="${statusIcon}"></i> ${statusMessage}`;
    } catch (error) {
        console.error('Error fetching progress:', error);
        document.getElementById('statusText').innerHTML = 
            '<i class="fas fa-exclamation-triangle text-danger"></i> Error checking progress';
        document.getElementById('errorSection').style.display = 'block';
        clearInterval(pollInterval);
    }
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

// Clean up interval when page is unloaded
window.addEventListener('beforeunload', function() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
});

console.log('YouTube Downloader JS file loaded completely');
