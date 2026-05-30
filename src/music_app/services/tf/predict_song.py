import essentia.standard as es
import pandas as pd

from genre_pred import genre_pred
from mood_pred import mood_pred
from other_pred import pred


def predict_song(directory):
    song_request = None

    try:
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


print(
    predict_song(
        "/mnt/z/Programming Heaven/GitHub/music-audiolyser/src/tensorflow_worker/.cache/songs/ABBA - Gimme! Gimme! Gimme! (A Man After Midnight).mp3"
    )
)
