from data.labels.moods import moods
from essentia.standard import TensorflowPredictEffnetDiscogs, TensorflowPredict2D

from utils import path_to_str, TF_ROOT_DIR

import numpy as np

def moodPred(audio):
    if not hasattr(moodPred, "embeddingModel"):
        moodPred.embeddingModel = TensorflowPredictEffnetDiscogs(
            graphFilename=path_to_str(TF_ROOT_DIR / "data" / "models" / "pretrained" / "jamendo" / "discogs-effnet-bs64-1.pb", True), output="PartitionedCall:1"
        )
    embeddingModel = moodPred.embeddingModel

    embeddings = embeddingModel(audio)

    if not hasattr(moodPred, "model"):
        moodPred.model = TensorflowPredict2D(graphFilename=path_to_str(TF_ROOT_DIR / "data" / "models" / "pretrained" / "jamendo" / "mtg_jamendo_moodtheme-discogs-effnet-1.pb", True))
    model = moodPred.model

    predictions = model(embeddings)

    averagePred = np.mean(predictions, axis=0).argmax()
    return moods[averagePred]
