import yt_dlp
import os

def download_playlist_videos(playlist_url, save_path="."):
    # Create the directory if it doesn't exist
    os.makedirs(save_path, exist_ok=True)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Best video & audio quality
        'merge_output_format': 'mp4',  # Ensure output is MP4 format
        'outtmpl': f'{save_path}/%(playlist_title)s/%(title)s.%(ext)s',  # Save inside playlist folder
        'force-ipv4': True,
        'socket_timeout': 30,  # Timeout setting
        'retries': 10,
        'noplaylist': False,  # Ensure the entire playlist is downloaded
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Prompt the user for a playlist URL
    playlist_url = input("Enter YouTube playlist URL: ")
    download_playlist_videos(playlist_url, save_path="downloads")
