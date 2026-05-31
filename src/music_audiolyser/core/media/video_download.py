import re

import yt_dlp

from music_audiolyser.core.utils.constants import (
    PATHS_CONFIG,
    YT_DL_OUTPUT,
    YT_DLP_AUDIO_FORMAT,
)


def video_download(URL):

    ydl_opts_filename = {
        "extractor_args": {"youtube": {"player_client": ["android"]}},
        "outtmpl": "%(title)s.%(ext)s",
        "quiet": True,
        "simulate": True,
        "nocheckcertificate": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts_filename) as ydl:
            info = ydl.extract_info(URL, download=False)
            video_filename = ydl.prepare_filename(info)
            video_filename = re.sub(
                r"\.[^.]+$", f".{YT_DLP_AUDIO_FORMAT}", video_filename
            )

        print("vidéo " + video_filename)

        file_path = PATHS_CONFIG["downloads"] / video_filename
        is_downloaded = file_path.exists()

        if not is_downloaded:

            ydl_opts_download = {
                "extractor_args": {"youtube": {"player_client": ["android"]}},
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": YT_DLP_AUDIO_FORMAT,
                    }
                ],
                "outtmpl": YT_DL_OUTPUT,
                "verbose": True,
                "nocheckcertificate": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                ydl.download([URL])

            print("Download complete.")

        names = re.match(r"^(.*?)\s*[-|–|—｜⧸]\s*(.*?)(\.\w{2,4})?$", video_filename)
        if names:
            artist_name = names.group(1)
            title = names.group(2)
        else:
            artist_name = "Unknown"
            title = video_filename

        return str(file_path), artist_name, title

    except yt_dlp.utils.DownloadError as e:
        print(f"Error during the process of yt-dlp: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
