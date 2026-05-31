import numpy as np
from essentia.standard import TensorflowPredict2D, TensorflowPredictEffnetDiscogs

from music_audiolyser.core.utils.constants import ALL_GENRES, PATHS_CONFIG


def genre_pred(audio):
    if not hasattr(genre_pred, "embedding_model"):
        genre_pred.embedding_model = TensorflowPredictEffnetDiscogs(
            graphFilename=PATHS_CONFIG["models"]["pretrained"]["embedding_model"],
            output="PartitionedCall:1",
        )
    embedding_model = genre_pred.embedding_model

    embeddings = embedding_model(audio)

    if not hasattr(genre_pred, "model"):
        genre_pred.model = TensorflowPredict2D(
            graphFilename=PATHS_CONFIG["models"]["pretrained"]["mtg_jamendo_genre"]
        )
    model = genre_pred.model

    predictions = model(embeddings)

    average_pred = np.mean(predictions, axis=0).argmax()
    return ALL_GENRES[average_pred]
