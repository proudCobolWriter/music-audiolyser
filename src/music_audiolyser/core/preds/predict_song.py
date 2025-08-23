import essentia.standard as es
import pandas as pd

from ...core.media.video_download import video_download
from ...core.preds.genre_pred import genre_pred
from ...core.preds.mood_pred import mood_pred
from ...core.preds.other_pred import pred


def predict_song():
    song_request = None

    url = str(input("URL de la chanson YouTube : \n")).strip()

    try:
        directory, _, _ = video_download(url)
        audio = es.MonoLoader(filename=directory, sampleRate=16000, resampleQuality=4)()

        genre = genre_pred(audio)
        mood = mood_pred(audio)
        audio = es.MonoLoader(filename=directory, sampleRate=44100, resampleQuality=4)()
        bpm, danceability, key, scale = pred(audio)

        song_request = pd.DataFrame(
            [
                {
                    "Genre": genre,
                    "BPM": bpm,
                    "Danceability": danceability,
                    "Key": key,
                    "Scale": scale,
                    "Mood": mood,
                }
            ]
        )
        return song_request

    except Exception as e:
        print("Erreur lors du traitement :", e)
