from typing import Union, Callable, Any
from functools import wraps
from pathlib import Path
from subprocess import run, call, Popen, PIPE, STDOUT, DEVNULL, CalledProcessError
from io import BytesIO

import re as regex
import asyncio
import logging
import pprint
import json
import time
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
MAX_YT_VIDEO_DURATION = 10  # in minutes
AUDIO_FORMAT = "mp3"  # usually either wav or mp3, wav is preferred for the highest quality
AUDIO_QUALITY = "bestaudio"  # see docs: https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#extractor-options

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


def log_subprocess_output(pipe: BytesIO, decode: bool = True, level: int = 10) -> list[Union[str, None]]:
    lines = []

    for line in iter(pipe.readline, b""):  # b'\n'-separated lines
        decoded = line.decode("utf-8")
        logger.log(level, "Extracted line from subprocess STDOUT: %r", decoded if decode else line)
        lines.append(decoded)

    return lines


def check_tool_cli(args: list[str]) -> None:
    try:
        result = call(
            args, text=True, stdout=DEVNULL, stderr=DEVNULL
        )  # run but no need for capture output or check kwargs
    except Exception as e:
        logger.critical(f"{type(e).__name__}:", exc_info=True)
        result = 1

    if result != 0:
        logger.critical(
            f"{args[0]} has returned error code {result}, check that {args[0]} is installed AND available in your .bashrc environment, included in the PATH variable"
        )
        raise ProcessLookupError()


def update_jobs_decorator(foo: Callable[[Any, Any], Any]) -> Callable[[Any, Any], Any]:
    @wraps(foo)
    def wrapper(self, *args, **kwargs):
        foo(self, *args, **kwargs)
        asyncio.run(self.updateCoroutine())

    return wrapper


# Youtube videos downloader export


class YTDownloader:
    def __init__(self) -> None:
        # Check for ffmpeg and ffprobe (required dependencies)
        check_tool_cli(["ffmpeg", "-version"])
        check_tool_cli(["ffprobe", "-version"])

        self.Queue: set[str] = set()
        self.__coqueue: set[asyncio.Task] = set()

    async def __downloadJobAsync(self, url) -> Any:
        print("start")
        await asyncio.sleep(3)
        print("end")
        # self.download(url)

    async def updateCoroutine(self) -> None:
        for url in self.Queue:
            if any([co.get_name() == url for co in self.__coqueue]):
                logger.warning(f"Already processing {url = }, ignoring")
                continue

            def discard(future: asyncio.Task):
                for item in self.__coqueue:
                    if item is future:
                        self.__coqueue.discard(item)
                        print(future.result())
                        break

            task = asyncio.create_task(self.__downloadJobAsync(url), name=url)
            task.add_done_callback(discard)
            self.__coqueue.add(task)
            await task

    @staticmethod
    def fetchPlaylistItems(url: str) -> list[Union[str, None]]:
        playlist_items = []

        try:
            getplaylist_args = ["--no-download", "--flat-playlist", "--print", "url", url]
            flattened_getplaylist_args = flatten_args(getplaylist_args)

            result = run(["yt-dlp", *flattened_getplaylist_args], text=True, check=True, capture_output=True).stdout
            playlist_items = [x for x in result.splitlines(False) if x != "NA"]

            logger.info(f"Found {len(playlist_items)} song(s) in the playlist")
        except (OSError, CalledProcessError):
            logger.error("Failed to retrieve the different videos in the provided playlist:", exc_info=True)
        except Exception:
            logger.error("Unexpected error occurred during the YouTube download:", exc_info=True)
        finally:
            return playlist_items

    def __repr__(self) -> None:
        fields = ", ".join(f"{i!r}={v!r}" for (i, v) in zip(self.__dict__.keys(), self.__dict__.values()))
        return f"{self.__class__.__name__}({fields})"

    def __str__(self) -> None:
        return self.__repr__()

    @update_jobs_decorator
    def __add__(self, other_value: Union[str, list[str]]) -> None:
        if isinstance(other_value, str):
            if other_value in self.Queue:
                logger.warning(f"Tried to add duplicate url ({other_value}), aborting")
            self.Queue.add(other_value)
        else:
            if not (isinstance(other_value, list) and all([type(x) == str for x in other_value])):
                raise ArithmeticError(
                    f"Can only add strings or an array of strings to the queue, got {type(other_value).__name__}"
                )
            else:
                for url in other_value:
                    if url in self.Queue:
                        logger.warning(f"Tried to add duplicate url ({url}), ignoring")
                self.Queue = self.Queue.union(other_value)

    @staticmethod
    def download(urls: Union[str, list[str]]) -> None:
        if isinstance(urls, str):  # ensuring list of strings for the for loop
            if urls.find("list") != -1:  # is a YouTube playlist?
                logger.info("Detected a playlist input, fetching its content now:")
                urls = YTDownloader.fetchPlaylistItems(urls)  # -> fetch its content
            else:
                urls = [urls]

        for url in urls:
            try:
                logger.info(f"Now trying to process {url = }:")
                start_time = time.perf_counter()

                if ensure_path(OUTPUT_PATH):
                    logger.info(f"A directory has been created at: {OUTPUT_PATH}")

                getfilename_args = [
                    "--no-download",
                    "-j",
                    url,
                ]
                flattened_getfilename_args = flatten_args(getfilename_args)

                result = run(["yt-dlp", *flattened_getfilename_args], text=True, check=True, capture_output=True).stdout
                jsondict = json.loads(result)

                assumed_names = regex.match(r"^(.*?)\s*[-|–|—｜]\s*(.*?)(\.\w{2,4})?$", jsondict["title"])
                assumed_author_name, assumed_song_name = assumed_names.group(1), assumed_names.group(2)

                metadata = {
                    "path": f"{jsondict['title']}.{AUDIO_FORMAT}",
                    "id": jsondict["id"],
                    "title": jsondict["title"],
                    "description": jsondict["description"],
                    "duration": jsondict["duration"],
                    "lang": jsondict["language"]  # should not be relied upon, usually the first subtitles' language
                    or "Unknown",
                    "uploader": jsondict["uploader"],
                    "author_name": assumed_author_name,  # extracted with RegEx and only works with common song naming patterns (it can fail!)
                    "song_name": assumed_song_name,  # extracted with RegEx and only works with common song naming patterns (it can fail!)
                    "date": jsondict["upload_date"],
                    "epoch": jsondict["timestamp"],  # unix timestamp
                    "view_count": jsondict["view_count"],
                    "tags": jsondict["tags"],
                    "categories": jsondict["categories"],  # usually just ["Music"]
                    "thumbnail_maxres": jsondict["thumbnail"],
                    "thumbnails": jsondict["thumbnails"],
                }

                logger.debug("Data gathered about the video:" + "\n" * 2 + pprint.pformat(metadata))

                if metadata["duration"] > MAX_YT_VIDEO_DURATION * 60:
                    logger.warning("A video longer than 10 minutes was provided, aborting")
                    continue

                download_args = [
                    "-x",  # ffmpeg and ffprobe are required for audio only file conversion
                    {"-f": AUDIO_QUALITY},
                    {"--audio-format": AUDIO_FORMAT},
                    {"--output": os.path.join(OUTPUT_PATH, "%(title)s.%(ext)s")},
                    "--verbose",
                    "--progress",
                    "--no-playlist",
                    url,
                ]
                flattened_args = flatten_args(download_args)

                process = Popen(["yt-dlp", *flattened_args], stdout=PIPE, stderr=STDOUT)
                lines = []

                with process.stdout as s:
                    lines = log_subprocess_output(s)

                status_code = process.wait()
                if status_code == 1:
                    lines = "".join(lines)
                    if (
                        error_occurrence := lines.find("ERROR")
                    ) != -1:  # only display the error part of the stream if possible (STDERR is empty for some reasons)
                        lines = lines[error_occurrence:]
                    raise ChildProcessError(f"yt-dlp returned status code 1:\nSTDOUT:\n\n{lines}")

                with open(os.path.join(OUTPUT_PATH, metadata["id"] + ".manifest.json"), "wt", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=4, ensure_ascii=False)

                end_time = time.perf_counter()
            except (OSError, CalledProcessError):
                logger.error("Failed to download the YouTube content:", exc_info=True)
            except Exception:
                logger.error("Unexpected error occurred during the YouTube download:", exc_info=True)
            else:
                logger.info(
                    f"Song \"{metadata['title']}\" has been successfully saved at path: {OUTPUT_PATH}/{metadata['title']}.{AUDIO_FORMAT} \
                    Process has taken {end_time - start_time:.2f} seconds (using perf_counter)"
                )
