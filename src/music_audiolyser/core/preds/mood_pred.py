import numpy as np
from essentia.standard import TensorflowPredict2D, TensorflowPredictEffnetDiscogs

from music_audiolyser.core.utils.constants import ALL_MOODS, PATHS_CONFIG


def mood_pred(audio):
    if not hasattr(mood_pred, "embedding_model"):
        mood_pred.embedding_model = TensorflowPredictEffnetDiscogs(
            graphFilename=PATHS_CONFIG["models"]["pretrained"]["embedding_model"],
            output="PartitionedCall:1",
        )
    embedding_model = mood_pred.embedding_model

    embeddings = embedding_model(audio)

    if not hasattr(mood_pred, "model"):
        mood_pred.model = TensorflowPredict2D(
            graphFilename=PATHS_CONFIG["models"]["pretrained"]["mtg_jamendo_moodtheme"]
        )
    model = mood_pred.model

    predictions = model(embeddings)

    average_pred = np.mean(predictions, axis=0).argmax()
    return ALL_MOODS[average_pred]
