import numpy as np

from core.preds.mood_pred import mood_pred
from index import ALL_MOODS


class FakeEmbeddingModel:
    def __call__(self, audio):
        return np.array([[0.1, 0.9]])


class FakeGenreModel:
    def __call__(self, embeddings):
        return np.array([[0.2, 0.8]])


def test_mood_pred(monkeypatch):
    monkeypatch.setattr(
        "core.preds.mood_pred.TensorflowPredictEffnetDiscogs",
        lambda graphFilename, output: FakeEmbeddingModel(),
    )

    monkeypatch.setattr(
        "core.preds.mood_pred.TensorflowPredict2D",
        lambda graphFilename: FakeGenreModel(),
    )

    fake_audio = np.zeros((100, 100))

    genre = mood_pred(fake_audio)

    assert genre in ALL_MOODS
