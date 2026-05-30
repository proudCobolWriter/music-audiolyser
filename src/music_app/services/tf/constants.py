from pathlib import Path

from genres import genres
from moods import moods

from loader import PATHS_CONFIG

YT_DL_OUTPUT = str(Path(PATHS_CONFIG["downloads"]) / "%(title)s.%(ext)s")
YT_DLP_AUDIO_FORMAT = "mp3"


FEATURES = ["Genre", "BPM", "Danceability", "Key", "Scale", "Mood"]
FIELDNAMES = [
    "Name",
    "Title",
    "Artist",
    "Genre",
    "BPM",
    "Danceability",
    "Key",
    "Scale",
    "Mood",
]

ALL_KEYS = [
    "C",
    "D",
    "E",
    "F",
    "G",
    "A",
    "B",
    "C#",
    "D#",
    "F#",
    "G#",
    "A#",
    "Db",
    "Eb",
    "Gb",
    "Ab",
    "Bb",
]
ALL_SCALES = ["major", "minor"]
ALL_MOODS = moods
ALL_GENRES = genres

CAT_FEATURES = ["Genre", "Key", "Scale", "Mood"]
NUM_FEATURES = ["BPM", "Danceability"]
