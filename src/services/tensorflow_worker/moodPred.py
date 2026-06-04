from data.labels.moods import moods
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs, TensorflowPredict2D

from pathlib import Path

import numpy as np

TF_ROOT_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT_DIR = TF_ROOT_DIR.parent.parent

def path_to_str(pathlike: Path, absolute: bool = False, relative_from: Path = TF_ROOT_DIR) -> str:
    if absolute:
        return str(pathlike.absolute())
    return str(pathlike.relative_to(relative_from))

def moodPred(audio, dataPath: Path):
    if not hasattr(moodPred, "embeddingModel"):
        moodPred.embeddingModel = TensorflowPredictEffnetDiscogs(
            graphFilename=path_to_str(dataPath / "models" / "pretrained" / "jamendo" / "discogs-effnet-bs64-1.pb", True), output="PartitionedCall:1"
        )
    embeddingModel = moodPred.embeddingModel

    embeddings = embeddingModel(audio)

    if not hasattr(moodPred, "model"):
        moodPred.model = TensorflowPredict2D(graphFilename=path_to_str(dataPath / "models" / "pretrained" / "jamendo" / "mtg_jamendo_moodtheme-discogs-effnet-1.pb", True))
    model = moodPred.model

    predictions = model(embeddings)

    averagePred = np.mean(predictions, axis=0).argmax()
    return moods[averagePred]
