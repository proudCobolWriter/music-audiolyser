from otherPred import pred
from genrePred import genrePred
from moodPred import moodPred

from utils import Path, path_to_str, TF_ROOT_DIR, PROJECT_ROOT_DIR

import essentia.standard as es

# CONSTANTS

FIELDNAMES = ["Name", "Title", "Artist", "Genre", "BPM", "Danceability", "Key", "Scale", "Mood"]

# Helper function

def process(path: Path) -> tuple[str, int, float, str, str, str]:
    directory: str = path_to_str(path, True)
    audio = es.MonoLoader(filename=directory, sampleRate=16000, resampleQuality=4)()

    genre = genrePred(audio)
    mood = moodPred(audio)

    audio = es.MonoLoader(filename=directory, sampleRate=44100, resampleQuality=4)()
    bpm, danceability, key, scale = pred(audio)

    return (genre, bpm, danceability, key, scale, mood)


# test call:
# process(PROJECT_ROOT_DIR / ".cache" / "songs" / "Rihanna - Love On The Brain (Billboard Music Awards 2016).mp3")
