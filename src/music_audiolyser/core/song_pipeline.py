import essentia.standard as es

from ..core.media.video_download import video_download
from ..core.preds.genre_pred import genre_pred
from ..core.preds.mood_pred import mood_pred
from ..core.preds.other_pred import pred
from ..core.utils.constants import PATHS_CONFIG, add_song_to_data


def song_pipeline(name="Unknown", progress_callback=None):
    with open(PATHS_CONFIG["song_requests"], "r") as f:
        file = f.readlines()

    for url in file:
        try:
            directory, artist_name, title = video_download(url)
            audio = es.MonoLoader(
                filename=directory, sampleRate=16000, resampleQuality=4
            )()
        except Exception:
            if progress_callback:
                progress_callback(song_name=1, advance=True)
            continue

        if progress_callback:
            progress_callback(song_name=title, advance=False)

        genre = genre_pred(audio)
        mood = mood_pred(audio)
        audio = es.MonoLoader(filename=directory, sampleRate=44100, resampleQuality=4)()
        bpm, danceability, key, scale = pred(audio)

        add_song_to_data(
            song={
                "youtube_id": url,
                "title": title,
                "artist": artist_name,
                "genre": genre,
                "bpm": bpm,
                "danceability": danceability,
                "key": key,
                "scale": scale,
                "mood": mood,
            },
            student_name=name,
        )
        if progress_callback:
            progress_callback(song_name=None, advance=True)
