import yt_dlp

def download_video(url, save_path="."):
    ydl_opts = {
        'outtmpl': f'{save_path}/%(title)s.%(ext)s',  # Save as video title
        'format': 'bestvideo+bestaudio/best',  # Best quality
        'force-ipv4': True,
        'socket_timeout': 30,  # Increase timeout to 30 seconds
        'retries': 10,

    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

video_url = input("Enter YouTube video URL: ")
download_video(video_url, save_path="downloads")
