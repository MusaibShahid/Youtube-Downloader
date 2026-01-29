#!/usr/bin/env python3
"""
Configuration file for YouTube Downloader
Ensures local-only operation using device resources
"""

import os
import platform

# Configuration - can be local or server mode
SERVER_MODE = os.environ.get('YT_SERVER_MODE', 'false').lower() == 'true' or os.environ.get('VERCEL') == '1'
LOCAL_ONLY = not SERVER_MODE
IS_VERCEL = os.environ.get('VERCEL') == '1'

# Host configuration based on mode
if SERVER_MODE:
    HOST = '0.0.0.0'  # Accessible from other devices on network
    print("[SERVER MODE] Accessible from other devices")
else:
    HOST = '127.0.0.1'  # Only accessible from local device
    print("[LOCAL MODE] Local device only")

PORT = 5000

# Resource configuration - uses local device resources only
if IS_VERCEL:
    DOWNLOAD_FOLDER = "/tmp/downloads"
    UPLOAD_FOLDER = "/tmp/uploads"
    MERGED_FOLDER = "/tmp/merged"
else:
    DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    MERGED_FOLDER = os.path.join(os.getcwd(), "merged")

# Override with environment variables if set
DOWNLOAD_FOLDER = os.environ.get('YT_DOWNLOAD_FOLDER', DOWNLOAD_FOLDER)
UPLOAD_FOLDER = os.environ.get('YT_UPLOAD_FOLDER', UPLOAD_FOLDER)
MERGED_FOLDER = os.environ.get('YT_MERGED_FOLDER', MERGED_FOLDER)

# Create directories on local device
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MERGED_FOLDER, exist_ok=True)

# System information
SYSTEM_INFO = {
    'platform': platform.system(),
    'machine': platform.machine(),
    'processor': platform.processor(),
    'python_version': platform.python_version(),
    'local_only': LOCAL_ONLY,
    'host': HOST,
    'port': PORT
}

def get_local_paths():
    """Get all local file paths"""
    return {
        'downloads': DOWNLOAD_FOLDER,
        'uploads': UPLOAD_FOLDER,
        'merged': MERGED_FOLDER,
        'app_directory': os.getcwd()
    }

def print_config_info():
    """Print configuration information"""
    mode = "SERVER" if SERVER_MODE else "LOCAL"
    print(f"[{mode} DEVICE CONFIGURATION]")
    print("=" * 40)
    print(f"Host: {HOST} ({'accessible from network' if SERVER_MODE else 'local device only'})")
    print(f"Port: {PORT}")
    print(f"Platform: {SYSTEM_INFO['platform']}")
    print(f"Python: {SYSTEM_INFO['python_version']}")
    print(f"App Directory: {os.getcwd()}")
    print(f"Downloads: {DOWNLOAD_FOLDER}")
    print(f"Uploads: {UPLOAD_FOLDER}")
    print(f"Merged: {MERGED_FOLDER}")
    print("=" * 40)
    if SERVER_MODE:
        print("SERVER MODE: Accessible from other devices")
        print("Using server resources")
        print("Network access enabled")
    else:
        print("Using LOCAL device resources only")
        print("No external network dependencies")
        print("Not accessible from other devices")
