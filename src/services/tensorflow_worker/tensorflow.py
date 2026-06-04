from otherPred import pred
from genrePred import genrePred
from moodPred import moodPred

from pathlib import Path

import essentia.standard as es

FIELDNAMES = ["Name", "Title", "Artist", "Genre", "BPM", "Danceability", "Key", "Scale", "Mood"]

TF_ROOT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT_DIR = TF_ROOT_DIR.parent.parent.parent

def path_to_str(pathlike: Path, absolute: bool = False, relative_from: Path = TF_ROOT_DIR) -> str:
    if absolute:
        return str(pathlike.absolute())
    return str(pathlike.relative_to(relative_from))

def process(path: Path) -> tuple[str, int, float, str, str, str]:
    directory: str = path_to_str(path, True)
    audio = es.MonoLoader(filename=directory, sampleRate=16000, resampleQuality=4)()

    genre = genrePred(audio, TF_ROOT_DIR / "data")
    mood = moodPred(audio, TF_ROOT_DIR / "data")

    audio = es.MonoLoader(filename=directory, sampleRate=44100, resampleQuality=4)()
    bpm, danceability, key, scale = pred(audio)

    return (genre, bpm, danceability, key, scale, mood)


# test call:
# process(PROJECT_ROOT_DIR / ".cache" / "songs" / "Rihanna - Love On The Brain (Billboard Music Awards 2016).mp3")
