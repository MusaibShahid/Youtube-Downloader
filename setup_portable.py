#!/usr/bin/env python3
"""
YouTube Downloader - Portable Setup Script
This script sets up the YouTube downloader for portable use.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = ['downloads', 'uploads', 'merged', 'static']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_startup_scripts():
    """Create platform-specific startup scripts"""
    system = platform.system().lower()
    
    if system == "windows":
        # Windows batch file
        with open("start_portable.bat", "w") as f:
            f.write("""@echo off
echo 🎥 YouTube Downloader - Portable Edition
echo 📱 Starting server...
echo.
python app.py
pause
""")
        print("✅ Created start_portable.bat")
        
        # Windows PowerShell script
        with open("start_portable.ps1", "w") as f:
            f.write("""# YouTube Downloader - Portable Edition
Write-Host "🎥 YouTube Downloader - Portable Edition" -ForegroundColor Cyan
Write-Host "📱 Starting server..." -ForegroundColor Green
Write-Host ""
python app.py
Read-Host "Press Enter to exit"
""")
        print("✅ Created start_portable.ps1")
        
    else:
        # Unix/Linux/macOS shell script
        with open("start_portable.sh", "w") as f:
            f.write("""#!/bin/bash
echo "🎥 YouTube Downloader - Portable Edition"
echo "📱 Starting server..."
echo ""
python3 app.py
read -p "Press Enter to exit..."
""")
        os.chmod("start_portable.sh", 0o755)
        print("✅ Created start_portable.sh")

def create_readme():
    """Create a comprehensive README for portable use"""
    readme_content = """# 🎥 YouTube Downloader - Portable Edition

A fast, portable YouTube video downloader with built-in file merging capabilities.

## 🚀 Quick Start

### Windows:
1. Double-click `start_portable.bat` or run `start_portable.ps1` in PowerShell
2. Open your browser to `http://localhost:5000`

### Linux/macOS:
1. Run `./start_portable.sh` in terminal
2. Open your browser to `http://localhost:5000`

## 📁 File Locations

- **Downloads:** `./downloads/` - All downloaded YouTube videos
- **Merged Files:** `./merged/` - Files created by the merger tool
- **Uploads:** `./uploads/` - Temporary files for merging

## ⚡ Features

- **Fast Processing:** Optimized for speed with chunked downloads
- **Real-time Progress:** Live download tracking
- **Auto-Merge:** Automatic video+audio merging with MoviePy
- **File Merger:** Upload and merge separate audio/video files
- **Portable:** No external dependencies, works offline after setup
- **High Quality:** Up to 4K/8K resolution support

## 🔧 Technical Details

- **Framework:** Flask (Python web framework)
- **YouTube Library:** pytubefix (YouTube video extraction)
- **Video Processing:** MoviePy (Python-based, no FFmpeg required)
- **Port:** 5000 (configurable in app.py)

## 📦 Dependencies

All dependencies are automatically installed via `requirements.txt`:
- Flask 3.0.0
- pytubefix 6.10.2
- moviepy 2.2.1
- Werkzeug 3.0.1

## 🌐 Network Access

The app runs locally by default. To allow network access:
1. Edit `app.py`
2. Change `app.run(debug=True, host='0.0.0.0', port=5000)`
3. Access from other devices using your IP address

## 🛠️ Troubleshooting

### If downloads are slow:
- Check your internet connection
- Try different video qualities
- Close other bandwidth-intensive applications

### If merging fails:
- The app will provide separate video and audio files
- Use the built-in File Merger tool to combine them manually

### If the app won't start:
- Make sure Python 3.7+ is installed
- Run `python -m pip install -r requirements.txt` manually
- Check that port 5000 is not in use

## 📝 License

This is a free, open-source application for personal use.

## 🆘 Support

For issues or questions, check the console output for detailed error messages.
"""
    
    with open("README_PORTABLE.md", "w") as f:
        f.write(readme_content)
    print("✅ Created README_PORTABLE.md")

def main():
    """Main setup function"""
    print("🎥 YouTube Downloader - Portable Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Install requirements
    print("\n📦 Installing dependencies...")
    if not install_requirements():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Create startup scripts
    print("\n🚀 Creating startup scripts...")
    create_startup_scripts()
    
    # Create README
    print("\n📝 Creating documentation...")
    create_readme()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n🚀 To start the application:")
    
    system = platform.system().lower()
    if system == "windows":
        print("   Windows: Double-click start_portable.bat")
        print("   PowerShell: .\\start_portable.ps1")
    else:
        print("   Terminal: ./start_portable.sh")
    
    print("\n🌐 Then open: http://localhost:5000")
    print("\n📖 Read README_PORTABLE.md for detailed instructions")

if __name__ == "__main__":
    main()
