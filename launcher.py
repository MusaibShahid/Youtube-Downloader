#!/usr/bin/env python3
"""
YouTube Downloader - Portable Launcher
Simple launcher that checks dependencies and starts the app
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['flask', 'pytubefix', 'moviepy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_missing_packages(packages):
    """Install missing packages"""
    print(f"📦 Installing missing packages: {', '.join(packages)}")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
        return True
    except subprocess.CalledProcessError:
        return False

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    """Main launcher function"""
    print("🎥 YouTube Downloader - Portable Launcher")
    print("=" * 45)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Ask user for mode
    print("\nChoose mode:")
    print("1. Local mode (local device only)")
    print("2. Server mode (accessible from other devices)")
    
    while True:
        choice = input("\nEnter choice (1 or 2): ").strip()
        if choice == "1":
            os.environ['YT_SERVER_MODE'] = 'false'
            print("🏠 Starting in LOCAL mode...")
            break
        elif choice == "2":
            os.environ['YT_SERVER_MODE'] = 'true'
            print("🌐 Starting in SERVER mode...")
            break
        else:
            print("❌ Please enter 1 or 2")
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print("📦 Installing missing packages...")
        
        if not install_missing_packages(missing):
            print("❌ Failed to install packages. Please run: pip install -r requirements.txt")
            input("Press Enter to exit...")
            sys.exit(1)
        
        print("✅ Dependencies installed successfully")
    else:
        print("✅ All dependencies found")
    
    # Create directories
    directories = ['downloads', 'uploads', 'merged']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("📁 Directories ready")
    
    # Start the app
    print("🚀 Starting YouTube Downloader...")
    print("🌐 The app will open in your browser automatically")
    print("📱 Access at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 45)
    
    # Open browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the Flask app
    try:
        from app import app
        from config import HOST, PORT
        app.run(debug=False, host=HOST, port=PORT)
    except KeyboardInterrupt:
        print("\n👋 YouTube Downloader stopped")
    except Exception as e:
        print(f"\n❌ Error starting the app: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
