import os

import yt_dlp

def download_spotify_playlist(playlist_url, save_path="downloads"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'extractaudio': True,
        'audioquality': 1,
        'audioformat': 'mp3',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

playlist_url = input("Enter Spotify playlist URL: ")
download_spotify_playlist(playlist_url)
