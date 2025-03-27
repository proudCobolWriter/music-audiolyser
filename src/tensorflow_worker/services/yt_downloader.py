from typing import Union
from pathlib import Path
import subprocess
import logging
import pprint
import json
import os

from tensorflow_worker.logging.custom import CustomFormatter as cf

# Setting up the custom colored logger

logger = logging.getLogger("YouTube")
logger.setLevel(logging.DEBUG)

colorlog = logging.StreamHandler()
colorlog.setLevel(logging.DEBUG)
colorlog.setFormatter(cf())

logger.addHandler(colorlog)

# Constants

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT_DIR / ".cache" / "songs"
MAX_CACHE_SIZE = "100mb"  # kb, mb or gb
AUDIO_FORMAT = "wav"  # usually either wav or mp3

# Util


def flatten_args(tbl: list[Union[str, dict[str, str]]]) -> list[str]:
    newFlattenedList = []

    for x in tbl:
        if isinstance(x, dict):
            for key, value in zip(x.keys(), x.values()):
                newFlattenedList.append(key)
                newFlattenedList.append(value)
        else:
            newFlattenedList.append(x)

    return newFlattenedList


def ensure_path(path: Union[Path, str]) -> bool:  # returns true if a path gets created for logging
    try:
        if type(path) == str:
            path = Path(str)
        elif not isinstance(path, Path):
            raise ValueError("A path or a string must be given")

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            return True
    except PermissionError:
        logger.error(f"Not enough permissions to create the appropriate directories at file path: {path}")
    except OSError:
        logger.error(f"OS Error at: {path}", exc_info=True)

    return False


# Youtube videos downloader export


class YTDownloader:
    def __init__(self) -> None:
        self.Queue = []

    @staticmethod
    def download(urls: Union[str, list[str]]) -> bool:
        if isinstance(urls, str):  # ensuring list of strings for the for loop
            urls = [urls]

        for url in urls:
            try:
                if ensure_path(OUTPUT_PATH):
                    logger.info(f"A directory has been created at: {OUTPUT_PATH}")

                getfilename_args = [
                    "--no-download",
                    "-j",
                    url,
                ]
                flatted_getfilename_args = flatten_args(getfilename_args)

                result = subprocess.run(
                    ["yt-dlp", *flatted_getfilename_args], capture_output=True, text=True, check=True
                ).stdout
                jsondict = json.loads(result)

                metadata = {
                    "title": jsondict["title"],
                    "duration": jsondict["duration"],
                    "description": jsondict["description"],
                    "author": jsondict["uploader"],
                    "date": jsondict["upload_date"],
                    "epoch": jsondict["timestamp"],
                    "view_count": jsondict["view_count"],
                    "tags": jsondict["tags"],
                    "categories": jsondict["categories"],
                    "thumbnail": jsondict["thumbnail"],
                }

                logger.debug(pprint.pformat(metadata))
                raise ValueError("nigga")

                download_args = [
                    "-x",  # ffmpeg and ffprobe are required for audio only file conversion
                    {"-f": "bestaudio"},
                    {"--audio-format": "wav"},
                    {"--output": os.path.join(OUTPUT_PATH, "%(title)s.%(ext)s")},
                    "--verbose",
                    "--progress",
                    url,
                ]
                flattened_args = flatten_args(download_args)

                subprocess.run(["yt-dlp", *flattened_args], check=True)
            except subprocess.CalledProcessError:
                logger.error("Failed to download the YouTube content:", exc_info=True)
            except Exception:
                logger.error("Unexpected error occurred during the YouTube download:", exc_info=True)
            else:
                return True
            return False

    def __repr__(self) -> None:
        fields = ", ".join(f"{i!r}={v!r}" for (i, v) in zip(self.__dict__.keys(), self.__dict__.values()))
        return f"{self.__class__.__name__}({fields})"
