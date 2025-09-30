import yt_dlp
import os

def download_playlist_audio(playlist_url, save_path="."):
    # Create the directory if it doesn't exist
    os.makedirs(save_path, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',  # Best quality audio
        'outtmpl': f'{save_path}/%(playlist_title)s/%(title)s.%(ext)s',  # Save inside playlist folder
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # Convert to MP3
            'preferredquality': '192',  # 192 kbps quality
        }],
        'force-ipv4': True,
        'socket_timeout': 30,  # Timeout setting
        'retries': 10,
        'noplaylist': False,  # Ensure playlists are downloaded
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    playlist_url = input("Enter YouTube playlist URL: ")
    download_playlist_audio(playlist_url, save_path="downloads")
