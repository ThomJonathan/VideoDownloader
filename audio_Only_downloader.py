import yt_dlp

def download_audio(url, save_path="."):
    ydl_opts = {
        'format': 'bestaudio/best',  # Best quality audio
        'outtmpl': f'{save_path}/%(title)s.%(ext)s',  # Save as audio title
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # Convert audio to MP3 format
            'preferredquality': '192',  # Set bitrate quality
        }],
        'force-ipv4': True,
        'socket_timeout': 30,  # Increase timeout to 30 seconds
        'retries': 10,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

video_url = input("Enter YouTube video URL: ")
download_audio(video_url, save_path="downloads")
