from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, after_this_request
import yt_dlp
import os
import threading
import uuid
from datetime import datetime
import shutil
import tempfile

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


def progress_hook(d, download_id):
    """Progress hook for yt-dlp"""
    if download_id in download_status:
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                download_status[download_id].progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
            download_status[download_id].status = "downloading"
            download_status[download_id].filename = d.get('filename', '')
        elif d['status'] == 'finished':
            download_status[download_id].status = "completed"
            download_status[download_id].progress = 100
            download_status[download_id].filename = d.get('filename', '')


def download_single_video(url, download_id):
    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/{download_id}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'force-ipv4': True,
            'socket_timeout': 30,
            'retries': 10,
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        download_status[download_id].status = "error"
        download_status[download_id].error = str(e)


def download_single_audio(url, download_id):
    try:
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

    except Exception as e:
        download_status[download_id].status = "error"
        download_status[download_id].error = str(e)


def download_playlist_videos(url, download_id):
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{DOWNLOAD_DIR}/{download_id}/%(playlist_title)s/%(title)s.%(ext)s',
            'force-ipv4': True,
            'socket_timeout': 30,
            'retries': 10,
            'noplaylist': False,
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        download_status[download_id].status = "error"
        download_status[download_id].error = str(e)


def download_playlist_audio(url, download_id):
    try:
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
            'noplaylist': False,
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        download_status[download_id].status = "error"
        download_status[download_id].error = str(e)


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
        'error': progress.error
    })


@app.route('/download/<download_id>')
def download_file(download_id):
    if download_id not in download_status:
        return jsonify({'error': 'Download not found'}), 404

    progress = download_status[download_id]
    if progress.status != 'completed':
        return jsonify({'error': 'Download not completed'}), 400

    session_dir = os.path.join(DOWNLOAD_DIR, download_id)

    # Find the first file in the download directory
    for root, dirs, files in os.walk(session_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Get original filename for download
                original_filename = os.path.basename(file_path)

                # Send file as attachment with proper headers for browser download
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=original_filename,
                    mimetype='application/octet-stream'
                )
            except Exception as e:
                return jsonify({'error': f'Error sending file: {str(e)}'}), 500

    return jsonify({'error': 'File not found'}), 404


@app.route('/cleanup/<download_id>', methods=['POST'])
def cleanup_download(download_id):
    if download_id in download_status:
        del download_status[download_id]

    session_dir = os.path.join(DOWNLOAD_DIR, download_id)
    if os.path.exists(session_dir):
        shutil.rmtree(session_dir)

    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)