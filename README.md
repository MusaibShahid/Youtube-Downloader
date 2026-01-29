# 🎥 YouTube 4K/8K Downloader

A modern web-based YouTube video downloader that supports high-quality downloads up to 8K resolution with a beautiful, responsive interface.

## ✨ Features

- **High Quality Downloads**: Support for 8K, 4K, 1440p, 1080p, 720p, 480p, and 360p
- **Modern Web Interface**: Beautiful, responsive design with dark theme
- **Real-time Progress**: Live download progress tracking with status updates
- **Smart Quality Selection**: Automatic fallback to best available quality
- **Safe File Handling**: Automatic filename sanitization and cleanup
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Mobile Friendly**: Responsive design that works on all devices

## 🚀 Quick Start

### Prerequisites

1. **Python 3.7+** installed on your system
2. **FFmpeg** installed and added to your system PATH
   - Windows: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo yum install ffmpeg` (CentOS/RHEL)

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd youtube_downloader
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser and go to**
   ```
   http://localhost:5000
   ```

## 📱 How to Use

1. **Copy a YouTube video URL**
   - Go to YouTube and copy the URL of the video you want to download
   - Example: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

2. **Paste the URL**
   - Open the web interface at `http://localhost:5000`
   - Paste the YouTube URL in the input field

3. **Select Quality**
   - Choose your preferred video quality from the dropdown
   - Higher quality = larger file size
   - Not all videos have all quality options

4. **Start Download**
   - Click "Start Download" button
   - Watch the real-time progress
   - Download the file when complete

## 🛠️ Technical Details

### Project Structure
```
youtube_downloader/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── templates/         # HTML templates
│   ├── index.html     # Home page
│   └── result.html    # Download progress page
├── static/            # Static files
│   └── style.css      # Custom CSS styles
├── downloads/         # Downloaded files (created automatically)
└── output/           # Temporary files (legacy, can be deleted)
```

### API Endpoints

- `GET /` - Home page with download form
- `POST /download` - Start video download
- `GET /progress/<download_id>` - Get download progress (JSON)
- `GET /download_file/<download_id>` - Download completed file
- `GET /cleanup` - Clean up old files (admin endpoint)

### Dependencies

- **Flask**: Web framework
- **pytubefix**: YouTube video downloading
- **FFmpeg**: Video/audio merging (external dependency)

## 🔧 Configuration

### Environment Variables
You can set these environment variables to customize the application:

- `FLASK_ENV=development` - Enable debug mode
- `FLASK_PORT=5000` - Change the port (default: 5000)
- `FLASK_HOST=0.0.0.0` - Change the host (default: 0.0.0.0)

### File Cleanup
The application automatically cleans up temporary files after merging. Old downloaded files (>1 hour) can be cleaned using the `/cleanup` endpoint.

## 🐛 Troubleshooting

### Common Issues

1. **"FFmpeg not found" error**
   - Make sure FFmpeg is installed and in your system PATH
   - Test by running `ffmpeg -version` in terminal

2. **"No video streams available" error**
   - The video might be private, deleted, or region-restricted
   - Try a different video URL

3. **Download fails or stops**
   - Check your internet connection
   - Some videos might have download restrictions
   - Try a lower quality setting

4. **Port already in use**
   - Change the port in `app.py` or kill the process using port 5000
   - On Windows: `netstat -ano | findstr :5000` then `taskkill /PID <PID> /F`

### Performance Tips

- Higher quality videos take longer to download and more disk space
- The application downloads video and audio separately, then merges them
- Temporary files are automatically cleaned up after successful merging

## 🚀 Production Deployment

For production deployment, consider:

1. **Use a production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Set up reverse proxy** (nginx/Apache)

3. **Configure environment variables**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-secret-key-here
   ```

4. **Set up file cleanup cron job**
   ```bash
   # Add to crontab to clean files every hour
   0 * * * * curl -s http://localhost:5000/cleanup
   ```

## 📄 License

This project is for educational purposes. Please respect YouTube's Terms of Service and copyright laws when downloading videos.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this project.

## ⚠️ Disclaimer

This tool is for personal use only. Please respect copyright laws and YouTube's Terms of Service. The developers are not responsible for any misuse of this software.
