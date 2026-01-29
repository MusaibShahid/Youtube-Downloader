from flask import Flask, render_template, request, send_file, redirect, url_for, flash, jsonify
from pytubefix import YouTube
import os, subprocess, datetime, threading, re, uuid
from werkzeug.utils import secure_filename
from config import DOWNLOAD_FOLDER, UPLOAD_FOLDER, MERGED_FOLDER, HOST, PORT, print_config_info, SERVER_MODE

app = Flask(__name__)
app.secret_key = 'youtube-downloader-secret-key'

# Global variables for tracking downloads
download_status = {}
download_progress = {}

# Global variables for tracking merges
merge_status = {}
merge_progress = {}
merge_files = {}

def sanitize_filename(filename):
    """Clean filename for safe saving"""
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\s+', ' ', filename).strip()
    return filename[:200] if len(filename) > 200 else filename

def process_merge(video_path, audio_path, output_path, merge_id):
    """Process file merging using MoviePy"""
    try:
        merge_status[merge_id] = "starting"
        merge_progress[merge_id] = 0
        
        # Import moviepy here to avoid import errors if not installed
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            merge_status[merge_id] = "loading_files"
            merge_progress[merge_id] = 20
            
            # Load video and audio
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            
            merge_status[merge_id] = "merging"
            merge_progress[merge_id] = 50
            
            # Set audio to video
            final_clip = video_clip.set_audio(audio_clip)
            
            merge_status[merge_id] = "writing_output"
            merge_progress[merge_id] = 75
            
            # Write the result with optimized settings
            final_clip.write_videofile(
                output_path, 
                codec='libx264', 
                audio_codec='aac',
                verbose=False,
                logger=None,
                preset='fast',  # Faster encoding
                ffmpeg_params=['-movflags', '+faststart'],  # Web optimization
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up
            video_clip.close()
            audio_clip.close()
            final_clip.close()
            
            merge_status[merge_id] = "completed"
            merge_progress[merge_id] = 100
            
            # Clean up input files
            try:
                os.remove(video_path)
                os.remove(audio_path)
            except:
                pass  # Don't fail if cleanup fails
                
        except ImportError:
            raise Exception("MoviePy is not installed. Please install it with: pip install moviepy")
            
    except Exception as e:
        merge_status[merge_id] = "error"
        merge_progress[merge_id] = 0
        print(f"Merge error: {str(e)}")
        # Store error for retrieval
        merge_files[merge_id] = {"error": str(e)}

def update_progress(download_id, stream, chunk, bytes_remaining):
    """Update download progress"""
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress = (bytes_downloaded / total_size) * 100
    download_progress[download_id] = round(progress, 1)

def process_download(url, itag, mode, download_id):
    """Background download processing"""
    try:
        download_status[download_id] = "starting"
        download_progress[download_id] = 0
        
        # Try to create YouTube object with retries
        max_retries = 3
        yt = None
        
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1} to access YouTube URL: {url}")
                download_status[download_id] = f"connecting_attempt_{attempt + 1}"
                
                yt = YouTube(url, 
                           on_progress_callback=lambda stream, chunk, bytes_remaining: 
                           update_progress(download_id, stream, chunk, bytes_remaining),
                           use_oauth=False,
                           allow_oauth_cache=False)
                
                # Test if we can access video info
                _ = yt.title  # This will trigger the actual connection
                print(f"Successfully connected on attempt {attempt + 1}")
                break
                
            except Exception as e:
                error_msg = str(e).lower()
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                
                # Check for specific error types
                if "private" in error_msg or "unavailable" in error_msg:
                    raise Exception("This video is private or unavailable. Please check the URL and try a different video.")
                elif "age" in error_msg and "restricted" in error_msg:
                    raise Exception("This video is age-restricted and cannot be downloaded.")
                elif "live" in error_msg:
                    raise Exception("Live streams cannot be downloaded. Please wait until the stream ends.")
                elif "premium" in error_msg or "members" in error_msg:
                    raise Exception("This video requires YouTube Premium or channel membership.")
                
                if attempt < max_retries - 1:
                    import time
                    wait_time = (attempt + 1) * 2  # 2, 4, 6 seconds
                    print(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    # Provide helpful error message based on common issues
                    if "retries" in error_msg or "timeout" in error_msg or "connection" in error_msg:
                        raise Exception(f"Network connection issue. Please check your internet connection and try again. If the problem persists, the video might be temporarily unavailable.")
                    else:
                        raise Exception(f"Failed to connect after {max_retries} attempts. This might be due to network issues, video restrictions, or temporary YouTube problems. Error: {str(e)}")
        
        if not yt:
            raise Exception("Could not create YouTube object")
            
        safe_title = sanitize_filename(yt.title)
        timestamp = str(int(datetime.datetime.now().timestamp()))
        print(f"Video title: {yt.title}")
        print(f"Safe title: {safe_title}")
        
        # Audio-only download
        if mode == "audio":
            download_status[download_id] = "downloading_audio"
            stream = yt.streams.get_by_itag(itag)
            if not stream:
                stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            
            if not stream:
                raise Exception("No audio stream available")
            
            # Create filename with quality info
            quality_info = f"_{stream.abr}" if hasattr(stream, 'abr') and stream.abr else ""
            filename = f"{safe_title}{quality_info}.mp3"
            output_path = os.path.join(DOWNLOAD_FOLDER, filename)
            stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
            
            download_status[download_id] = "completed"
            download_progress[download_id] = 100
            download_status[f"{download_id}_file"] = output_path
            download_status[f"{download_id}_filename"] = filename
            print(f"Audio download completed: {filename}")
            return

        # Progressive download (already has video+audio)
        elif mode == "progressive":
            download_status[download_id] = "downloading_video"
            stream = yt.streams.get_by_itag(itag)
            if not stream:
                raise Exception("Selected video stream not available")
            
            # Create filename with quality info
            quality_info = f"_{stream.resolution}" if hasattr(stream, 'resolution') and stream.resolution else ""
            filename = f"{safe_title}{quality_info}.mp4"
            output_path = os.path.join(DOWNLOAD_FOLDER, filename)
            stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)
            
            download_status[download_id] = "completed"
            download_progress[download_id] = 100
            download_status[f"{download_id}_file"] = output_path
            download_status[f"{download_id}_filename"] = filename
            print(f"Progressive download completed: {filename}")
            return

        # Merge download (high quality video + audio) - ALWAYS TRY MOVIEPY FIRST
        elif mode == "merge":
            video_path = os.path.join(DOWNLOAD_FOLDER, f"temp_video_{timestamp}.mp4")
            output_path = os.path.join(DOWNLOAD_FOLDER, f"{safe_title}.mp4")

            # Download audio first (usually faster) - prefer MP4 audio for better compatibility
            download_status[download_id] = "downloading_audio"
            
            # Try to get MP4 audio first (better compatibility), then fallback to any audio
            audio_stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4").order_by('abr').desc().first()
            if not audio_stream:
                audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            
            if not audio_stream:
                raise Exception("No audio stream available")
            
            # Use appropriate extension based on audio type
            audio_ext = "m4a" if "mp4" in audio_stream.mime_type else "webm"
            audio_filename = f"temp_audio_{timestamp}.{audio_ext}"
            audio_path = os.path.join(DOWNLOAD_FOLDER, audio_filename)
            
            print(f"Downloading audio: {audio_stream.mime_type}, {audio_stream.abr}")
            audio_stream.download(output_path=DOWNLOAD_FOLDER, filename=audio_filename)

            # Download video
            download_status[download_id] = "downloading_video"
            video_stream = yt.streams.get_by_itag(itag)
            if not video_stream:
                raise Exception("Selected video stream not available")
            
            video_stream.download(output_path=DOWNLOAD_FOLDER, filename=f"temp_video_{timestamp}.mp4")

            # Try MoviePy FIRST (no FFmpeg dependency)
            download_status[download_id] = "merging_files_python"
            print("Using MoviePy for merging (better compatibility)...")
            
            try:
                # Try to use moviepy for merging
                from moviepy.editor import VideoFileClip, AudioFileClip
                
                print("Loading video and audio files...")
                video_clip = VideoFileClip(video_path)
                audio_clip = AudioFileClip(audio_path)
                
                print("Merging video and audio...")
                final_video = video_clip.set_audio(audio_clip)
                
                # Get video quality for filename
                quality_info = f"_{video_stream.resolution}" if video_stream and hasattr(video_stream, 'resolution') and video_stream.resolution else "_HQ"
                final_filename = f"{safe_title}{quality_info}_merged.mp4"
                final_path = os.path.join(DOWNLOAD_FOLDER, final_filename)
                
                print("Writing final video file...")
                # Optimized settings for faster processing
                final_video.write_videofile(
                    final_path, 
                    codec='libx264', 
                    audio_codec='aac', 
                    verbose=False, 
                    logger=None,
                    preset='fast',  # Faster encoding
                    ffmpeg_params=['-movflags', '+faststart'],  # Web optimization
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True
                )
                
                # Clean up
                video_clip.close()
                audio_clip.close()
                final_video.close()
                
                print("MoviePy merge completed successfully")
                
                # Clean up temporary files
                try:
                    if os.path.exists(audio_path): os.remove(audio_path)
                    if os.path.exists(video_path): os.remove(video_path)
                except Exception as e:
                    print(f"Cleanup error: {e}")
                
                download_status[download_id] = "completed"
                download_progress[download_id] = 100
                download_status[f"{download_id}_file"] = final_path
                download_status[f"{download_id}_filename"] = final_filename
                print(f"Merge download completed: {final_filename}")
                return
                
            except ImportError:
                print("MoviePy not available, trying FFmpeg...")
                # Fall back to FFmpeg if MoviePy is not available
                pass
            except Exception as e:
                print(f"MoviePy merge failed: {e}, trying FFmpeg...")
                # Fall back to FFmpeg if MoviePy fails
                pass

            # FFmpeg fallback (only if MoviePy fails)
            download_status[download_id] = "checking_ffmpeg"
            ffmpeg_check = subprocess.run("ffmpeg -version", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if ffmpeg_check.returncode != 0:
                # Neither MoviePy nor FFmpeg available - provide separate files
                download_status[download_id] = "providing_separate_files"
                print("Neither MoviePy nor FFmpeg available. Providing video and audio files separately...")
                
                # Copy video file to final location with descriptive name
                video_final_name = f"{safe_title}_{video_stream.resolution}_VIDEO_ONLY.mp4"
                video_final_path = os.path.join(DOWNLOAD_FOLDER, video_final_name)
                
                audio_final_name = f"{safe_title}_{audio_stream.abr}_AUDIO_ONLY.{audio_ext}"
                audio_final_path = os.path.join(DOWNLOAD_FOLDER, audio_final_name)
                
                import shutil
                shutil.copy2(video_path, video_final_path)
                shutil.copy2(audio_path, audio_final_path)
                
                # Store both files info
                download_status[f"{download_id}_video_file"] = video_final_path
                download_status[f"{download_id}_video_filename"] = video_final_name
                download_status[f"{download_id}_audio_file"] = audio_final_path
                download_status[f"{download_id}_audio_filename"] = audio_final_name
                
                # Use video file as primary download
                output_path = video_final_path
                final_filename = video_final_name
                
                download_status[download_id] = "completed"
                download_progress[download_id] = 100
                download_status[f"{download_id}_file"] = output_path
                download_status[f"{download_id}_filename"] = final_filename
                print(f"Separate files provided: {video_final_name} and {audio_final_name}")
                return
                    
            else:
                # FFmpeg is available - use it for merging
                download_status[download_id] = "merging_files"
                
                # Get video quality for filename
                quality_info = f"_{video_stream.resolution}" if video_stream and hasattr(video_stream, 'resolution') and video_stream.resolution else "_HQ"
                final_filename = f"{safe_title}{quality_info}_merged.mp4"
                final_path = os.path.join(DOWNLOAD_FOLDER, final_filename)
                
                # Try multiple FFmpeg commands for better compatibility
                merge_commands = [
                    # Command 1: Standard merge with audio re-encoding
                    f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -b:a 128k -shortest "{final_path}" -y',
                    # Command 2: Force audio mapping
                    f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest "{final_path}" -y',
                    # Command 3: Re-encode both if needed
                    f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v libx264 -c:a aac -b:a 128k -shortest "{final_path}" -y'
                ]
                
                merge_success = False
                last_error = ""
                
                for i, cmd in enumerate(merge_commands):
                    print(f"Trying FFmpeg merge command {i+1}: {cmd}")
                    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    if result.returncode == 0:
                        print(f"FFmpeg merge successful with command {i+1}")
                        merge_success = True
                        break
                    else:
                        last_error = result.stderr.decode()
                        print(f"FFmpeg command {i+1} failed: {last_error}")
                
                if not merge_success:
                    raise Exception(f"All FFmpeg merge attempts failed. Last error: {last_error}")

                # Verify the merged file has audio
                download_status[download_id] = "verifying_audio"
                verify_cmd = f'ffprobe -v quiet -show_streams -select_streams a "{final_path}"'
                verify_result = subprocess.run(verify_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if verify_result.returncode != 0 or not verify_result.stdout.strip():
                    print("Warning: Merged file may not have audio, trying alternative merge...")
                    # Try one more time with different settings
                    alt_cmd = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a libmp3lame -b:a 128k -ac 2 -ar 44100 "{final_path}" -y'
                    alt_result = subprocess.run(alt_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if alt_result.returncode != 0:
                        print(f"Alternative FFmpeg merge also failed: {alt_result.stderr.decode()}")

                # Clean up temporary files
                try:
                    if os.path.exists(audio_path): os.remove(audio_path)
                    if os.path.exists(video_path): os.remove(video_path)
                except Exception as e:
                    print(f"Cleanup error: {e}")
                
                download_status[download_id] = "completed"
                download_progress[download_id] = 100
                download_status[f"{download_id}_file"] = final_path
                download_status[f"{download_id}_filename"] = final_filename
                print(f"FFmpeg merge download completed: {final_filename}")
                return

        else:
            raise Exception(f"Unknown download mode: {mode}")
        
    except Exception as e:
        download_status[download_id] = f"error: {str(e)}"
        download_progress[download_id] = 0

@app.route("/")
def index():
    return render_template("simple.html")

@app.route('/api/drives')
def get_drives():
    """Get available drives and directories"""
    import platform
    drives = []
    
    if platform.system() == "Windows":
        import string
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                try:
                    # Get free space
                    import shutil
                    free_gb = shutil.disk_usage(drive).free / (1024**3)
                    
                    drives.append({
                        'path': drive,
                        'free_gb': round(free_gb, 2),
                        'display': f"{letter}: Drive ({round(free_gb, 1)} GB free)"
                    })
                except:
                    drives.append({
                        'path': drive,
                        'free_gb': 0,
                        'display': f"{letter}: Drive"
                    })
    else:
        # Linux/macOS
        drives.append({
            'path': os.path.expanduser('~'),
            'free_gb': 0,
            'display': 'Home Directory'
        })
        drives.append({
            'path': '/tmp',
            'free_gb': 0,
            'display': 'Temporary Directory'
        })
    
    return jsonify(drives)

@app.route('/api/set-directory', methods=['POST'])
def set_directory():
    """Set custom directory for downloads"""
    data = request.get_json()
    directory_type = data.get('type')  # 'downloads', 'uploads', 'merged'
    new_path = data.get('path')
    
    if not new_path or not os.path.exists(new_path):
        return jsonify({'success': False, 'message': 'Invalid directory path'})
    
    # Update the global variable
    global DOWNLOAD_FOLDER, UPLOAD_FOLDER, MERGED_FOLDER
    
    if directory_type == 'downloads':
        DOWNLOAD_FOLDER = new_path
    elif directory_type == 'uploads':
        UPLOAD_FOLDER = new_path
    elif directory_type == 'merged':
        MERGED_FOLDER = new_path
    else:
        return jsonify({'success': False, 'message': 'Invalid directory type'})
    
    # Create directory if it doesn't exist
    os.makedirs(new_path, exist_ok=True)
    
    return jsonify({'success': True, 'message': f'{directory_type.title()} directory updated'})

@app.route('/api/cleanup', methods=['POST'])
def cleanup_storage():
    """Clean up old files to free space"""
    data = request.get_json()
    directory_type = data.get('type', 'all')  # 'downloads', 'uploads', 'merged', 'all'
    max_age_hours = data.get('max_age_hours', 24)  # Default: 24 hours
    
    import time
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    cleaned_files = 0
    freed_space = 0
    
    directories_to_clean = []
    if directory_type == 'all':
        directories_to_clean = [DOWNLOAD_FOLDER, UPLOAD_FOLDER, MERGED_FOLDER]
    elif directory_type == 'downloads':
        directories_to_clean = [DOWNLOAD_FOLDER]
    elif directory_type == 'uploads':
        directories_to_clean = [UPLOAD_FOLDER]
    elif directory_type == 'merged':
        directories_to_clean = [MERGED_FOLDER]
    
    for directory in directories_to_clean:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > max_age_seconds:
                        try:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            cleaned_files += 1
                            freed_space += file_size
                        except:
                            pass
    
    freed_space_mb = round(freed_space / (1024 * 1024), 2)
    
    return jsonify({
        'success': True,
        'message': f'Cleaned {cleaned_files} files, freed {freed_space_mb} MB',
        'cleaned_files': cleaned_files,
        'freed_space_mb': freed_space_mb
    })

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        url = request.form["url"]
        if not url:
            flash("Please enter a YouTube URL", "error")
            return redirect(url_for('index'))
        
        # Try to connect with retries
        max_retries = 3
        yt = None
        
        for attempt in range(max_retries):
            try:
                print(f"Analyze attempt {attempt + 1} for URL: {url}")
                yt = YouTube(url, use_oauth=False, allow_oauth_cache=False)
                
                # Test connection by accessing title
                _ = yt.title
                print(f"Analysis successful on attempt {attempt + 1}")
                break
                
            except Exception as e:
                error_msg = str(e).lower()
                print(f"Analysis attempt {attempt + 1} failed: {str(e)}")
                
                # Check for specific error types
                if "private" in error_msg or "unavailable" in error_msg:
                    raise Exception("This video is private or unavailable. Please check the URL and try a different video.")
                elif "age" in error_msg and "restricted" in error_msg:
                    raise Exception("This video is age-restricted and cannot be downloaded.")
                elif "live" in error_msg:
                    raise Exception("Live streams cannot be downloaded. Please wait until the stream ends.")
                elif "premium" in error_msg or "members" in error_msg:
                    raise Exception("This video requires YouTube Premium or channel membership.")
                
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)  # Wait 2 seconds between retries
                else:
                    if "retries" in error_msg or "timeout" in error_msg or "connection" in error_msg:
                        raise Exception("Network connection issue. Please check your internet connection and try again. If the problem persists, the video might be temporarily unavailable.")
                    else:
                        raise Exception(f"Could not access video after {max_retries} attempts. This might be due to network issues, video restrictions, or temporary YouTube problems. Error: {str(e)}")
        
        if not yt:
            raise Exception("Could not create YouTube object")
        
        # Get all available streams - prioritize merged video+audio
        video_streams = []
        audio_streams = []
        
        # Get best audio stream for merging calculations
        best_audio = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        audio_size = round(best_audio.filesize / 1024 / 1024, 2) if best_audio and best_audio.filesize else 50
        
        # Progressive streams (video + audio already merged)
        for stream in yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc():
            if stream.resolution:
                size_mb = round(stream.filesize / 1024 / 1024, 2) if stream.filesize else 0
                video_streams.append({
                    "resolution": stream.resolution,
                    "size_mb": size_mb,
                    "itag": stream.itag,
                    "type": "Ready to Download (Video+Audio)",
                    "fps": getattr(stream, 'fps', 30),
                    "download_type": "progressive"
                })
        
        # Adaptive video streams (higher quality, will be merged with audio)
        for stream in yt.streams.filter(adaptive=True, mime_type="video/mp4").order_by('resolution').desc():
            if stream.resolution:
                video_size = round(stream.filesize / 1024 / 1024, 2) if stream.filesize else 0
                total_size = video_size + audio_size
                video_streams.append({
                    "resolution": stream.resolution,
                    "size_mb": total_size,
                    "itag": stream.itag,
                    "type": "High Quality (Auto-Merged with MoviePy)",
                    "fps": getattr(stream, 'fps', 30),
                    "download_type": "merge"
                })
        
        # Audio-only streams
        for stream in yt.streams.filter(only_audio=True).order_by('abr').desc():
            if stream.abr:
                size_mb = round(stream.filesize / 1024 / 1024, 2) if stream.filesize else 0
                audio_streams.append({
                    "quality": f"{stream.abr} - {stream.audio_codec}",
                    "size_mb": size_mb,
                    "itag": stream.itag,
                    "type": "Audio Only (MP3)",
                    "download_type": "audio"
                })
        
        return render_template("streams.html", 
                             yt=yt, 
                             video_streams=video_streams, 
                             audio_streams=audio_streams,
                             url=url)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route("/download", methods=["POST"])
def download():
    try:
        url = request.form["url"]
        itag = request.form["itag"]
        download_type = request.form.get("download_type", "progressive")
        
        if not url or not itag:
            flash("Missing required parameters", "error")
            return redirect(url_for('index'))

        # Generate download ID
        download_id = str(int(datetime.datetime.now().timestamp() * 1000))

        # Start download in background
        thread = threading.Thread(target=process_download, args=(url, itag, download_type, download_id))
        thread.daemon = True
        thread.start()

        return render_template("progress.html", download_id=download_id)
        
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route("/progress_api/<download_id>")
def get_progress(download_id):
    """Get download progress as JSON"""
    from flask import jsonify
    status = download_status.get(download_id, "not_found")
    progress = download_progress.get(download_id, 0)
    
    response = {
        "status": status,
        "progress": progress
    }
    
    if status == "completed":
        file_path = download_status.get(f"{download_id}_file")
        filename = download_status.get(f"{download_id}_filename")
        if file_path and os.path.exists(file_path):
            response["download_ready"] = True
            response["filename"] = filename
    
    return jsonify(response)

@app.route("/download_file/<download_id>")
def download_file(download_id):
    """Download the completed file"""
    try:
        file_path = download_status.get(f"{download_id}_file")
        filename = download_status.get(f"{download_id}_filename")
        
        if not file_path or not os.path.exists(file_path):
            flash("File not found or download not completed", "error")
            return redirect(url_for('index'))
        
        # Use the actual video title as filename
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f"Error downloading file: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route("/merge-files", methods=["POST"])
def merge_files():
    """Handle file upload and start merge process"""
    try:
        if 'video_file' not in request.files or 'audio_file' not in request.files:
            return jsonify({"success": False, "error": "Both video and audio files are required"})
        
        video_file = request.files['video_file']
        audio_file = request.files['audio_file']
        output_name = request.form.get('output_name', '').strip()
        
        if video_file.filename == '' or audio_file.filename == '':
            return jsonify({"success": False, "error": "Both files must be selected"})
        
        # Generate unique merge ID
        merge_id = str(uuid.uuid4())
        
        # Secure filenames
        video_filename = secure_filename(video_file.filename)
        audio_filename = secure_filename(audio_file.filename)
        
        # Save uploaded files
        video_path = os.path.join(UPLOAD_FOLDER, f"{merge_id}_video_{video_filename}")
        audio_path = os.path.join(UPLOAD_FOLDER, f"{merge_id}_audio_{audio_filename}")
        
        video_file.save(video_path)
        audio_file.save(audio_path)
        
        # Generate output filename
        if output_name:
            output_filename = sanitize_filename(output_name)
            if not output_filename.endswith('.mp4'):
                output_filename += '.mp4'
        else:
            base_name = os.path.splitext(video_filename)[0]
            output_filename = f"{base_name}_merged.mp4"
        
        output_path = os.path.join(MERGED_FOLDER, f"{merge_id}_{output_filename}")
        
        # Store merge info
        merge_files[merge_id] = {
            "output_path": output_path,
            "output_filename": output_filename
        }
        
        # Start merge process in background
        merge_thread = threading.Thread(target=process_merge, args=(video_path, audio_path, output_path, merge_id))
        merge_thread.daemon = True
        merge_thread.start()
        
        return jsonify({"success": True, "merge_id": merge_id})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/merge-progress/<merge_id>")
def get_merge_progress(merge_id):
    """Get merge progress"""
    try:
        status = merge_status.get(merge_id, "unknown")
        progress = merge_progress.get(merge_id, 0)
        
        response = {
            "status": status,
            "progress": progress
        }
        
        if status == "completed":
            merge_info = merge_files.get(merge_id, {})
            response["download_url"] = f"/download-merged/{merge_id}"
            response["filename"] = merge_info.get("output_filename", "merged_video.mp4")
        elif status == "error":
            merge_info = merge_files.get(merge_id, {})
            response["error"] = merge_info.get("error", "Unknown error occurred")
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"status": "error", "progress": 0, "error": str(e)})

@app.route("/download-merged/<merge_id>")
def download_merged(merge_id):
    """Download merged file"""
    try:
        merge_info = merge_files.get(merge_id)
        if not merge_info:
            flash("Merge not found", "error")
            return redirect(url_for('index'))
        
        output_path = merge_info["output_path"]
        output_filename = merge_info["output_filename"]
        
        if not os.path.exists(output_path):
            flash("Merged file not found", "error")
            return redirect(url_for('index'))
        
        return send_file(output_path, as_attachment=True, download_name=output_filename)
        
    except Exception as e:
        flash(f"Download error: {str(e)}", "error")
        return redirect(url_for('index'))

if __name__ == "__main__":
    print_config_info()
    mode = "SERVER" if SERVER_MODE else "LOCAL"
    print(f"\nYouTube Downloader - {mode} EDITION")
    print("Access at: http://localhost:5000")
    if SERVER_MODE:
        print("Network access: http://[server-ip]:5000")
    print("MoviePy integration for seamless merging")
    print("Built-in file merger tool")
    print("Network retry logic")
    if SERVER_MODE:
        print("\nRunning in SERVER mode - accessible from other devices")
    else:
        print("\nRunning in LOCAL mode - local device only")
    app.run(debug=True, host=HOST, port=PORT)