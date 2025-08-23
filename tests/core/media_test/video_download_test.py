import subprocess

from music_audiolyser.core.media.video_download import video_download


def fake_subprocess_run(command, capture_output=False, text=False, check=False):
    class Result:
        stdout = "Artist - Title.mp4\n"

    return Result()


def test_video_download(monkeypatch):
    monkeypatch.setattr(subprocess, "run", fake_subprocess_run)

    # Appel de la fonction
    file_path, artist, title = video_download("https://youtube.com/johndoe")

    assert artist == "Artist"
    assert title == "Title"
    assert file_path.endswith(".mp3")
