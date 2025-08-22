import subprocess
import re
from index import YT_DL_OUTPUT, YT_DLP_AUDIO_FORMAT, SONGS_DIR


def video_download(URL):

    is_downloaded = False

    command_get_filename = ["yt-dlp", "--get-filename", "-o", "%(title)s.%(ext)s", URL]

    try:
        result = subprocess.run(
            command_get_filename, capture_output=True, text=True, check=True
        )

        video_filename = result.stdout.strip()
        print("vidéo " + video_filename)
        video_filename = re.sub(r"\.[^.]+$", f".{YT_DLP_AUDIO_FORMAT}", video_filename)
        if (SONGS_DIR / video_filename).exists():
            is_downloaded = True

        command_download = [
            "yt-dlp",
            "-f",
            "bestaudio",
            "--extract-audio",
            "--audio-format",
            YT_DLP_AUDIO_FORMAT,
            "--verbose",
            "-o",
            YT_DL_OUTPUT,
            URL,
        ]

        if not is_downloaded:
            subprocess.run(command_download, check=True)
            print("Download complete.")

        file_path = SONGS_DIR / video_filename
        names = re.match(r"^(.*?)\s*[-|–|—｜⧸]\s*(.*?)(\.\w{2,4})?$", video_filename)
        if names:
            artist_name = names.group(1)
            title = names.group(2)
        else:
            artist_name = "Unknown"
            title = video_filename

        return str(file_path), artist_name, title

    except subprocess.CalledProcessError as e:
        print(f"Error during the process of yt-dlp: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
