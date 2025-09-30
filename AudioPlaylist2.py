import yt_dlp
import os


def download_playlist_audio(playlist_url, save_path="downloads"):
    """
    Download audio from YouTube playlist with authentication options
    """
    # Create download directory if it doesn't exist
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Configuration options to avoid bot detection
    ydl_opts = {
        'format': 'bestaudio/best',  # Download best audio quality
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),  # Output filename template
        'extractaudio': True,  # Extract audio
        'audioformat': 'mp3',  # Convert to mp3
        'ignoreerrors': True,  # Continue on download errors

        # Anti-bot detection options
        'cookiesfrombrowser': ('chrome',),  # Use cookies from Chrome browser
        # Alternative: 'cookiesfrombrowser': ('firefox',),  # Use Firefox cookies
        # Alternative: 'cookiesfrombrowser': ('safari',),   # Use Safari cookies

        # Additional options to avoid detection
        'sleep_interval': 1,  # Sleep between downloads
        'max_sleep_interval': 5,  # Maximum sleep interval
        'writeinfojson': False,  # Don't write info json
        'writesubtitles': False,  # Don't write subtitles
        'writeautomaticsub': False,  # Don't write auto subtitles

        # User agent to mimic real browser
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading playlist: {playlist_url}")
            ydl.download([playlist_url])
            print("Download completed successfully!")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print("\nTrying alternative method without browser cookies...")

        # Fallback options without cookies
        fallback_opts = ydl_opts.copy()
        del fallback_opts['cookiesfrombrowser']

        try:
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                ydl.download([playlist_url])
                print("Download completed with fallback method!")
        except Exception as e2:
            print(f"Fallback also failed: {str(e2)}")
            print("\nPlease try one of the manual solutions mentioned below.")


def download_with_manual_cookies(playlist_url, cookies_file_path, save_path="downloads"):
    """
    Download using manually exported cookies file
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'extractaudio': True,
        'audioformat': 'mp3',
        'ignoreerrors': True,
        'cookies': cookies_file_path,  # Path to cookies file
        'sleep_interval': 1,
        'max_sleep_interval': 5,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading playlist with manual cookies: {playlist_url}")
            ydl.download([playlist_url])
            print("Download completed successfully!")
    except Exception as e:
        print(f"Error with manual cookies: {str(e)}")


if __name__ == "__main__":
    # Get playlist URL from user
    playlist_url = input("Enter YouTube playlist URL: ").strip()

    print("\nAttempting download with automatic cookie extraction...")
    download_playlist_audio(playlist_url, save_path="downloads")

    print("\n" + "=" * 50)
    print("TROUBLESHOOTING GUIDE:")
    print("=" * 50)
    print("If the download still fails, try these solutions:")
    print("\n1. BROWSER COOKIES METHOD:")
    print("   - Make sure you're logged into YouTube in your browser")
    print("   - The script will try to use cookies from Chrome automatically")
    print("   - For Firefox: Change 'chrome' to 'firefox' in the code")
    print("   - For Safari: Change 'chrome' to 'safari' in the code")

    print("\n2. MANUAL COOKIES FILE:")
    print("   - Install a browser extension like 'Get cookies.txt'")
    print("   - Export YouTube cookies to a .txt file")
    print("   - Use the download_with_manual_cookies() function")

    print("\n3. ALTERNATIVE APPROACHES:")
    print("   - Try using a VPN")
    print("   - Wait a few hours and try again")
    print("   - Update yt-dlp: pip install --upgrade yt-dlp")

    print("\n4. SINGLE VIDEO TEST:")
    print("   - Try downloading a single video first to test")
    print("   - If that works, then try the playlist")