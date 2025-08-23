import numpy as np

from music_audiolyser.core.preds.other_pred import pred


class FakeRhythm:
    def __call__(self, audio):
        return [120.0]


class FakeDanceability:
    def __call__(self, audio):
        return [0.8]


class FakeKey:
    def __call__(self, audio):
        return [3, "minor"]


def test_pred(monkeypatch):
    monkeypatch.setattr(
        "music_audiolyser.core.preds.other_pred.es.RhythmExtractor2013",
        lambda: FakeRhythm(),
    )
    monkeypatch.setattr(
        "music_audiolyser.core.preds.other_pred.es.Danceability",
        lambda: FakeDanceability(),
    )
    monkeypatch.setattr(
        "music_audiolyser.core.preds.other_pred.es.KeyExtractor", lambda: FakeKey()
    )

    fake_audio = np.zeros(100)

    bpm, danceability, key, scale = pred(fake_audio)

    assert bpm == 120
    assert danceability == 0.8
    assert key == 3
    assert scale == "minor"
