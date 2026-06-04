from data.labels.genres import genres
from essentia.standard import TensorflowPredictEffnetDiscogs, TensorflowPredict2D

from utils import path_to_str, TF_ROOT_DIR

import numpy as np

def genrePred(audio):
    if not hasattr(genrePred, "embeddingModel"):
        genrePred.embeddingModel = TensorflowPredictEffnetDiscogs(
            graphFilename=path_to_str(TF_ROOT_DIR / "data" / "models" / "pretrained" / "jamendo" / "discogs-effnet-bs64-1.pb", True), output="PartitionedCall:1"
        )
    embeddingModel = genrePred.embeddingModel

    embeddings = embeddingModel(audio)

    if not hasattr(genrePred, "model"):
        genrePred.model = TensorflowPredict2D(graphFilename=path_to_str(TF_ROOT_DIR / "data" / "models" / "pretrained" / "jamendo" / "mtg_jamendo_genre-discogs-effnet-1.pb", True))
    model = genrePred.model

    predictions = model(embeddings)

    averagePred = np.mean(predictions, axis=0).argmax()
    return genres[averagePred]
