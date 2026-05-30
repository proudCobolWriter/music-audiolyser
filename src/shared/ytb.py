from urllib.parse import urlparse, parse_qs
from typing import IO, Union, Callable, Any
from functools import wraps
from pathlib import Path
from subprocess import run, call, Popen, PIPE, STDOUT, DEVNULL, CalledProcessError

import re as regex
import asyncio
import logging
import pprint
import random
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

# CONSTANTS

ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT_DIR / ".cache" / "songs"
MAX_CACHE_SIZE = 100  # in MB
MAX_YT_VIDEO_DURATION = 10  # in minutes
YOUTUBE_CLIENT = "android"
AUDIO_QUALITY = "best"  # see docs: https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#extractor-options
AUDIO_FORMAT = (
    "mp3"  # usually either wav or mp3, wav is preferred for the highest quality, mp3 is preferred for file size
)

YOUTUBE_DOMAINS = ["youtu.be", "youtube.com"]
MAX_DOWNLOAD_RETRIES = 3

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
            path = Path(path)
        elif not isinstance(path, Path):
            raise ValueError("A path or a string must be given")

        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            return True
    except PermissionError:
        logger.error(
            f"Not enough permissions to create the appropriate directories at file path: {path}", exc_info=True
        )
    except OSError:
        logger.error(f"OS Error at: {path}", exc_info=True)

    return False


def log_subprocess_output(pipe: IO[bytes], decode: bool = True, level: int = 10) -> list[Union[str, None]]:
    lines = []

    for line in iter(pipe.readline, b""):  # b'\n'-separated lines
        decoded = line.decode("utf-8")
        logger.log(level, "Extracted line from subprocess STDOUT: %s", decoded if decode else line)
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


# Youtube videos downloader export


class YTDownloader:
    def __init__(self, workers: int = 3) -> None:
        # Check for ffmpeg and ffprobe (required dependencies)
        check_tool_cli(["ffmpeg", "-version"])
        check_tool_cli(["ffprobe", "-version"])

        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self.queued_ids: set[str] = set()
        self.active_downloads: set[str] = set()
        self.workers = workers
        self.worker_tasks = []

    async def worker(self):
        while True:
            url = await self.queue.get()

            try:
                if url in self.active_downloads:
                    logger.warning(f"Already downloading {url = }, ignoring...")
                    continue

                self.active_downloads.add(url)

                def run_thread(url: str):
                    YTDownloader.download(url)
                    YTDownloader.clear_cache()

                await asyncio.sleep(random.uniform(1, 3))
                await asyncio.to_thread(run_thread, url)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.error(f"Failure to download {url = }...", exc_info=True)
            finally:
                self.active_downloads.discard(url)
                self.queued_ids.discard(YTDownloader.extract_id(url))
                self.queue.task_done()

    async def wait(self):
        # waits till all tasks are processed
        await self.queue.join()

    async def start(self):
        for _ in range(self.workers):
            task = asyncio.create_task(self.worker())
            self.worker_tasks.append(task)

    async def stop(self):
        for task in self.worker_tasks:
            task.cancel()

        await asyncio.gather(*self.worker_tasks, return_exceptions=True)

    def __repr__(self) -> None:
        fields = ", ".join(f"{i!r}={v!r}" for (i, v) in zip(self.__dict__.keys(), self.__dict__.values()))
        return f"{self.__class__.__name__}({fields})"

    def __str__(self) -> None:
        return self.__repr__()

    # overload the + operator to add new URLs
    def __add__(self, x: Union[str, list[str]]):
        if isinstance(x, str):
            self.enqueue(x)
        elif isinstance(x, list) and all([type(u) == str for u in x]):
            for u in x:
                self.enqueue(u)
        else:
            logger.error("Unknown type of string or collection of strings given", exc_info=True)

        return self  # allows chaining if desired

    def __len__(self) -> int:
        return self.queue.qsize()

    def enqueue(self, url: str):
        if not isinstance(url, str):
            logger.error("A string representative of an URL must be given", exc_info=True)
            return

        ytbid = YTDownloader.extract_id(url)

        if ytbid is None:
            logger.warning(f"Invalid youTube URL: {url}")
            return

        if ytbid in self.queued_ids:
            logger.warning(f"Tried to add a duplicate {url = }, ignoring...")
            return

        self.queued_ids.add(ytbid)
        self.queue.put_nowait(url)

    @staticmethod
    def fetch_playlist_items(url: str) -> list[Union[str, None]]:
        playlist_items = []

        try:
            sabr_bypass = {"--extractor-args": f"youtube:player_client={YOUTUBE_CLIENT}"}

            getplaylist_args = [sabr_bypass, "--no-download", "--flat-playlist", "--print", "url", url]
            flattened_getplaylist_args = flatten_args(getplaylist_args)

            result = run(["yt-dlp", *flattened_getplaylist_args], text=True, check=True, capture_output=True).stdout
            playlist_items = [x for x in result.splitlines(False) if x != "NA"]

            logger.info(f"Found {len(playlist_items)} song(s) in the playlist")
        except (OSError, CalledProcessError):
            logger.error("Failed to retrieve the different videos in the provided playlist:", exc_info=True)
        except Exception:
            logger.error("Unexpected error occurred during the YouTube download:", exc_info=True)

        return playlist_items

    @staticmethod
    def extract_id(url_string: str) -> str:
        # Make sure all URLs start with a valid scheme
        if not url_string.lower().startswith("http"):
            url_string = "http://%s" % url_string

        url = urlparse(url_string)

        # Check host against whitelist of domains
        if not url.hostname or (url.hostname.replace("www.", "") not in YOUTUBE_DOMAINS):
            return None

        # Video ID is usually to be found in 'v' query string
        qs = parse_qs(url.query)
        if "v" in qs:
            return qs["v"][0]

        # Otherwise fall back to path component
        return url.path.lstrip("/")

    @staticmethod
    def download(urls: Union[str, list[str]], path: Union[str, Path] = OUTPUT_PATH):
        if isinstance(urls, str):  # ensuring list of strings for the for loop
            if urls.find("list") != -1:  # is a YouTube playlist?
                logger.info("Detected a playlist input, fetching its content now:")
                urls = YTDownloader.fetch_playlist_items(urls)  # -> fetch its content
            else:
                urls = [urls]

        for url in urls:
            try:
                logger.info(f"Now trying to process {url = }:")
                start_time = time.perf_counter()

                if ensure_path(path):
                    logger.info(f"A directory has been created at: {path}")

                sabr_bypass = {"--extractor-args": f"youtube:player_client={YOUTUBE_CLIENT}"}

                getfilename_args = [
                    sabr_bypass,
                    "--no-download",
                    "-j",
                    url,
                ]
                flattened_getfilename_args = flatten_args(getfilename_args)

                result = None

                for attempt in range(MAX_DOWNLOAD_RETRIES):
                    try:
                        result = run(
                            ["yt-dlp", *flattened_getfilename_args], text=True, check=True, capture_output=True
                        ).stdout

                        break
                    except Exception as e:
                        logger.error(
                            f"Caught error while trying to download {url = }, retrying... ({attempt + 1}/{MAX_DOWNLOAD_RETRIES})",
                            exc_info=True,
                        )
                        time.sleep(attempt + 1)
                else:
                    raise CalledProcessError(
                        f"YT-DLP has failed {MAX_DOWNLOAD_RETRIES} times, aborting."
                    )  # avoid a json.loads(result) call with result=None

                jsondict = json.loads(result)

                assumed_names = regex.match(r"^(.*?)\s*[-|–|—｜]\s*(.*?)(\.\w{2,4})?$", jsondict["title"])
                assumed_author_name, assumed_song_name = "Unknown", jsondict["title"]

                if assumed_names:
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
                    sabr_bypass,
                    "-x",  # ffmpeg and ffprobe are required for audio only file conversion
                    {"-f": AUDIO_QUALITY},
                    {"--audio-format": AUDIO_FORMAT},
                    {"--output": os.path.join(path, "%(title)s.%(ext)s")},
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

                with open(os.path.join(path, metadata["id"] + ".manifest.json"), "wt", encoding="utf-8") as f:
                    json.dump(metadata, f, indent=4, ensure_ascii=False)

                end_time = time.perf_counter()
            except (OSError, CalledProcessError):
                logger.error("Failed to download the YouTube content:", exc_info=True)
            except Exception:
                logger.error("Unexpected error occurred during the YouTube download:", exc_info=True)
            else:
                logger.info(
                    f"Song \"{metadata['title']}\" has been successfully saved at path: {path}/{metadata['title']}.{AUDIO_FORMAT} \
                    Process has taken {end_time - start_time:.2f} seconds (using perf_counter)"
                )

    @staticmethod
    def get_cache_size(path: Union[str, Path]) -> int:
        dir = os.listdir(path)
        files = [os.path.getsize(path / f) for f in dir if os.path.isfile(path / f)]

        total_size = 0
        for size in files:
            total_size += size

        return total_size

    @staticmethod
    def clear_cache(path: Union[str, Path]) -> tuple[int, int]:
        cache_size = YTDownloader.get_cache_size()

        if cache_size <= MAX_CACHE_SIZE * (1024**2):
            return

        dir = os.listdir(path)
        files = [(os.stat(path / f), f) for f in dir if os.path.isfile(path / f)]

        files.sort(key=lambda f: f[0].st_mtime)

        files_removed = 0
        space_cleared = 0

        for file in files:
            if cache_size <= MAX_CACHE_SIZE * (1024**2):
                break

            fdir = path / file[1]
            size = os.path.getsize(fdir)

            files_removed += 1
            cache_size -= size
            space_cleared += size

            os.remove(fdir)

        logger.info(f"{files_removed} files have been removed clearing {space_cleared / (1024**2):.2f}MB")

        return (files_removed, space_cleared)
