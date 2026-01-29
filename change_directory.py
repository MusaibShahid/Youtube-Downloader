#!/usr/bin/env python3
"""
Quick script to change default directories to a drive with more space
"""

import os
import shutil

def get_drive_with_most_space():
    """Find the drive with the most free space"""
    max_free_space = 0
    best_drive = None
    
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            try:
                free_space = shutil.disk_usage(drive).free
                if free_space > max_free_space:
                    max_free_space = free_space
                    best_drive = drive
            except:
                pass
    
    return best_drive

def main():
    print("🔍 Finding drive with most free space...")
    
    best_drive = get_drive_with_most_space()
    if not best_drive:
        print("❌ No suitable drive found")
        return
    
    free_gb = shutil.disk_usage(best_drive).free / (1024**3)
    print(f"✅ Best drive: {best_drive} ({free_gb:.1f} GB free)")
    
    # Create new directories
    new_downloads = os.path.join(best_drive, "YouTube_Downloads")
    new_uploads = os.path.join(best_drive, "YouTube_Uploads")
    new_merged = os.path.join(best_drive, "YouTube_Merged")
    
    os.makedirs(new_downloads, exist_ok=True)
    os.makedirs(new_uploads, exist_ok=True)
    os.makedirs(new_merged, exist_ok=True)
    
    print(f"📁 Created directories:")
    print(f"   Downloads: {new_downloads}")
    print(f"   Uploads: {new_uploads}")
    print(f"   Merged: {new_merged}")
    
    # Set environment variables for this session
    os.environ['YT_DOWNLOAD_FOLDER'] = new_downloads
    os.environ['YT_UPLOAD_FOLDER'] = new_uploads
    os.environ['YT_MERGED_FOLDER'] = new_merged
    
    print("\n✅ Environment variables set for this session")
    print("🚀 Now run: python app.py")
    print("\n💡 To make this permanent, set these environment variables:")
    print(f"   set YT_DOWNLOAD_FOLDER={new_downloads}")
    print(f"   set YT_UPLOAD_FOLDER={new_uploads}")
    print(f"   set YT_MERGED_FOLDER={new_merged}")

if __name__ == "__main__":
    main()
