from core.preds.other_pred import pred
from core.preds.genre_pred import genre_pred
from core.preds.mood_pred import mood_pred
from core.media.video_download import video_download
from index import FIELDNAMES
from core.utils.loader import PATHS_CONFIG
import csv
import essentia.standard as es


def main(name, progress_callback=None):
    with open(PATHS_CONFIG["song_requests"], "r") as f:
        file = f.readlines()

    for url in file:
        try:
            directory, artist_name, title = video_download(url)
            audio = es.MonoLoader(
                filename=directory, sampleRate=16000, resampleQuality=4
            )()
        except:
            if progress_callback:
                progress_callback(song_name=1, advance=True)
            continue

        if progress_callback:
            progress_callback(song_name=title, advance=False)

        genre = genre_pred(audio)
        mood = mood_pred(audio)
        audio = es.MonoLoader(filename=directory, sampleRate=44100, resampleQuality=4)()
        bpm, danceability, key, scale = pred(audio)

        with open(PATHS_CONFIG["chart"], "a", newline="") as c:
            chart = csv.DictWriter(c, FIELDNAMES)
            chart.writerow(
                {
                    "Name": name,
                    "Title": title,
                    "Artist": artist_name,
                    "Genre": genre,
                    "BPM": bpm,
                    "Danceability": danceability,
                    "Key": key,
                    "Scale": scale,
                    "Mood": mood,
                }
            )
        if progress_callback:
            progress_callback(song_name=None, advance=True)
