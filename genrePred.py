from header.genres import genres
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs, TensorflowPredict2D
import numpy as np

def genrePred(file):
    audio = MonoLoader(filename=file, sampleRate=16000, resampleQuality=4)()
    embedding_model = TensorflowPredictEffnetDiscogs(graphFilename="header/discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
    embeddings = embedding_model(audio)

    model = TensorflowPredict2D(graphFilename="header/genre_discogs400-discogs-effnet-1.pb", input="serving_default_model_Placeholder", output="PartitionedCall:0")
    predictions = model(embeddings)

    averagePred = np.mean(predictions, axis = 0)
    topGenres = averagePred.argsort()[::-1][:1]
    return genres[topGenres.item()]



