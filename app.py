from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, after_this_request
import yt_dlp
import os
import threading
import uuid
from datetime import datetime
import shutil
import tempfile
import zipfile

app = Flask(__name__)

# Create downloads directory if it doesn't exist
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Store download status
download_status = {}


class DownloadProgress:
    def __init__(self, download_id):
        self.download_id = download_id
        self.status = "starting"
        self.progress = 0
        self.filename = ""
        self.error = None
        self.total_files = 0
        self.downloaded_files = 0


def progress_hook(d, download_id):
    """Progress hook for yt-dlp"""
    if download_id in download_status:
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                download_status[download_id].progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
            download_status[download_id].status = "downloading"
            download_status[download_id].filename = os.path.basename(d.get('filename', ''))
        elif d['status'] == 'finished':
            download_status[download_id].downloaded_files += 1
            download_status[download_id].filename = os.path.basename(d.get('filename', ''))
            # Update progress based on files downloaded
            if download_status[download_id].total_files > 0:
                download_status[download_id].progress = (download_status[download_id].downloaded_files /
                                                         download_status[download_id].total_files) * 100


def get_playlist_info(url):
    """Get playlist information to determine total number of videos"""
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force-ipv4': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                return len(list(info['entries']))
            else:
                return 1  # Single video
    except:
        return 1


def download_single_video(url, download_id):
    try:
        download_status[download_id].total_files = 1

        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/{download_id}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'force-ipv4': True,
            'socket_timeout': 30,
            'retries': 10,
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        download_status[download_id].status = "completed"

    except Exception as e:
        download_status[download_id].status = "error"
        download_status[download_id].error = str(e)


def download_single_audio(url, download_id):
    try:
        download_status[download_id].total_files = 1

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{DOWNLOAD_DIR}/{download_id}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'force-ipv4': True,
            'socket_timeout': 30,
            'retries': 10,
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        download_status[download_id].status = "completed"

    except Exception as e:
        download_status[download_id].status = "error"
        download_status[download_id].error = str(e)


def download_playlist_videos(url, download_id):
    try:
        # Get playlist info first
        total_files = get_playlist_info(url)
        download_status[download_id].total_files = total_files

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',  # Ensure output is MP4
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # Convert to MP4 if not already
            }],
            'outtmpl': f'{DOWNLOAD_DIR}/{download_id}/%(playlist_title)s/%(title)s.%(ext)s',
            'force-ipv4': True,
            'socket_timeout': 30,
            'retries': 10,
            'noplaylist': False,  # This is crucial for playlist downloads
            'yes_playlist': True,  # Explicitly enable playlist mode
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            # Add anti-bot detection options similar to AudioPlaylist2.py
            'sleep_interval': 1,
            'max_sleep_interval': 3,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        download_status[download_id].status = "completed"

    except Exception as e:
        download_status[download_id].status = "error"
        download_status[download_id].error = str(e)


def download_playlist_audio(url, download_id):
    try:
        # Get playlist info first
        total_files = get_playlist_info(url)
        download_status[download_id].total_files = total_files

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{DOWNLOAD_DIR}/{download_id}/%(playlist_title)s/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'force-ipv4': True,
            'socket_timeout': 30,
            'retries': 10,
            'noplaylist': False,  # This is crucial for playlist downloads
            'yes_playlist': True,  # Explicitly enable playlist mode
            'ignoreerrors': True,  # Continue on download errors
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            # Add anti-bot detection options similar to AudioPlaylist2.py
            'sleep_interval': 1,
            'max_sleep_interval': 3,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ApgleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }

        # Try with browser cookies first (like in AudioPlaylist2.py)
        try:
            ydl_opts['cookiesfrombrowser'] = ('chrome',)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as cookie_error:
            print(f"Cookie method failed, trying without: {cookie_error}")
            # Fallback without cookies
            del ydl_opts['cookiesfrombrowser']
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        download_status[download_id].status = "completed"

    except Exception as e:
        download_status[download_id].status = "error"
        download_status[download_id].error = str(e)


def create_zip_from_directory(directory_path, zip_filename):
    """Create a zip file from a directory"""
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Create relative path for zip
                arcname = os.path.relpath(file_path, directory_path)
                zipf.write(file_path, arcname)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def start_download():
    data = request.json
    url = data.get('url', '').strip()
    download_type = data.get('type', 'single_video')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Generate unique download ID
    download_id = str(uuid.uuid4())
    download_status[download_id] = DownloadProgress(download_id)

    # Create download directory for this session
    session_dir = os.path.join(DOWNLOAD_DIR, download_id)
    os.makedirs(session_dir, exist_ok=True)

    # Start download in background thread
    if download_type == 'single_video':
        thread = threading.Thread(target=download_single_video, args=(url, download_id))
    elif download_type == 'single_audio':
        thread = threading.Thread(target=download_single_audio, args=(url, download_id))
    elif download_type == 'playlist_videos':
        thread = threading.Thread(target=download_playlist_videos, args=(url, download_id))
    elif download_type == 'playlist_audio':
        thread = threading.Thread(target=download_playlist_audio, args=(url, download_id))
    else:
        return jsonify({'error': 'Invalid download type'}), 400

    thread.daemon = True
    thread.start()

    return jsonify({'download_id': download_id})


@app.route('/status/<download_id>')
def get_status(download_id):
    if download_id not in download_status:
        return jsonify({'error': 'Download not found'}), 404

    progress = download_status[download_id]
    return jsonify({
        'status': progress.status,
        'progress': progress.progress,
        'filename': progress.filename,
        'error': progress.error,
        'total_files': progress.total_files,
        'downloaded_files': progress.downloaded_files
    })


@app.route('/download/<download_id>')
def download_file(download_id):
    if download_id not in download_status:
        return jsonify({'error': 'Download not found'}), 404

    progress = download_status[download_id]
    if progress.status != 'completed':
        return jsonify({'error': 'Download not completed'}), 400

    session_dir = os.path.join(DOWNLOAD_DIR, download_id)

    # Count files in the directory
    total_files = 0
    files_list = []
    for root, dirs, files in os.walk(session_dir):
        for file in files:
            total_files += 1
            files_list.append(os.path.join(root, file))

    if total_files == 0:
        return jsonify({'error': 'No files found'}), 404
    elif total_files == 1:
        # Single file - send directly
        file_path = files_list[0]
        original_filename = os.path.basename(file_path)
        return send_file(
            file_path,
            as_attachment=True,
            download_name=original_filename,
            mimetype='application/octet-stream'
        )
    else:
        # Multiple files - create and send zip
        zip_filename = f"{download_id}_playlist.zip"
        zip_path = os.path.join(DOWNLOAD_DIR, zip_filename)

        try:
            create_zip_from_directory(session_dir, zip_path)

            @after_this_request
            def remove_zip(response):
                try:
                    os.remove(zip_path)
                except Exception:
                    pass
                return response

            return send_file(
                zip_path,
                as_attachment=True,
                download_name=zip_filename,
                mimetype='application/zip'
            )
        except Exception as e:
            return jsonify({'error': f'Error creating zip file: {str(e)}'}), 500


@app.route('/cleanup/<download_id>', methods=['POST'])
def cleanup_download(download_id):
    if download_id in download_status:
        del download_status[download_id]

    session_dir = os.path.join(DOWNLOAD_DIR, download_id)
    if os.path.exists(session_dir):
        shutil.rmtree(session_dir)

    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)