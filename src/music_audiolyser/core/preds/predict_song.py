import essentia.standard as es

from ...core.media.video_download import video_download
from ...core.preds.genre_pred import genre_pred
from ...core.preds.mood_pred import mood_pred
from ...core.preds.other_pred import pred
from ..model.run_model import run_model


def predict_song(url, progress_callback=None):
    try:
        if progress_callback:
            progress_callback(song_name="Downloading", advance=False)

        result = video_download(url)

        if result is None:
            raise ValueError(f"video_download failed for url: {url}")

        directory, _, _ = result

        if progress_callback:
            progress_callback(song_name="Loading audio", advance=False)

        audio = es.MonoLoader(filename=directory, sampleRate=16000, resampleQuality=4)()

        if progress_callback:
            progress_callback(song_name="Predicting genre", advance=False)

        genre = genre_pred(audio)

        if progress_callback:
            progress_callback(song_name="Predicting mood", advance=False)

        mood = mood_pred(audio)

        if progress_callback:
            progress_callback(song_name="Reloading audio", advance=False)

        audio = es.MonoLoader(filename=directory, sampleRate=44100, resampleQuality=4)()

        if progress_callback:
            progress_callback(song_name="Extracting features", advance=False)

        bpm, danceability, key, scale = pred(audio)

        result = {
            "genre": genre,
            "bpm": bpm,
            "danceability": danceability,
            "key": key,
            "scale": scale,
            "mood": mood,
        }

        if progress_callback:
            progress_callback(song_name="Running KNN", advance=True)

        result = run_model(result)

        if progress_callback:
            progress_callback(song_name="Done", advance=True)

        return result[0]

    except Exception as e:
        if progress_callback:
            progress_callback(song_name=1, advance=False)
        print("Error while processing :", e)
