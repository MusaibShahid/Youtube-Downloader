#!/usr/bin/env python3
"""
Create Portable Package Script
Creates a portable package of the YouTube Downloader
"""

import os
import shutil
import zipfile
from pathlib import Path
import datetime

def create_portable_package():
    """Create a portable package"""
    print("📦 Creating Portable YouTube Downloader Package")
    print("=" * 50)
    
    # Package name with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"YouTube_Downloader_Portable_{timestamp}"
    
    # Files to include
    essential_files = [
        'app.py',
        'launcher.py',
        'setup_portable.py',
        'requirements.txt',
        'README_PORTABLE.md',
        'templates/',
        'static/',
        'start.bat',
        'start.sh'
    ]
    
    # Create package directory
    package_dir = Path(package_name)
    package_dir.mkdir(exist_ok=True)
    
    print(f"📁 Creating package directory: {package_name}")
    
    # Copy essential files
    for file_path in essential_files:
        src = Path(file_path)
        dst = package_dir / file_path
        
        if src.is_file():
            print(f"📄 Copying file: {file_path}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        elif src.is_dir():
            print(f"📁 Copying directory: {file_path}")
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    
    # Create directories
    directories = ['downloads', 'uploads', 'merged']
    for directory in directories:
        (package_dir / directory).mkdir(exist_ok=True)
        print(f"📁 Creating directory: {directory}")
    
    # Create a simple README for the package
    readme_content = f"""# 🎥 YouTube Downloader - Portable Package

Created: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 🚀 Quick Start

### Option 1: Simple Launcher (Recommended)
1. Run `python launcher.py`
2. The app will install dependencies automatically and start

### Option 2: Manual Setup
1. Run `python setup_portable.py` to set up everything
2. Then run `python app.py` to start the server

### Option 3: Platform Scripts
- Windows: Double-click `start.bat`
- Linux/macOS: Run `./start.sh`

## 📱 Access
Open your browser to: http://localhost:5000

## 📁 File Locations
- Downloads: `./downloads/`
- Merged Files: `./merged/`
- Uploads: `./uploads/`

## ⚡ Features
- Fast downloading and merging
- Real-time progress tracking
- Built-in file merger tool
- No external dependencies (after setup)
- Portable and self-contained

## 🆘 Support
Check README_PORTABLE.md for detailed instructions and troubleshooting.
"""
    
    with open(package_dir / "README.txt", "w", encoding='utf-8') as f:
        f.write(readme_content)
    
    print("📄 Created README.txt")
    
    # Create ZIP package
    zip_name = f"{package_name}.zip"
    print(f"📦 Creating ZIP package: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_name):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_name)
                zipf.write(file_path, arcname)
    
    # Clean up package directory
    shutil.rmtree(package_name)
    
    print("\n" + "=" * 50)
    print("✅ Portable package created successfully!")
    print(f"📦 Package: {zip_name}")
    print(f"📏 Size: {os.path.getsize(zip_name) / 1024 / 1024:.1f} MB")
    print("\n🚀 To distribute:")
    print(f"   1. Share the {zip_name} file")
    print("   2. Recipients extract and run 'python launcher.py'")
    print("   3. No additional setup required!")

if __name__ == "__main__":
    create_portable_package()
