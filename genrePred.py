from data.genres import genres
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs, TensorflowPredict2D
import numpy as np



def genrePred(audio):

    if not hasattr(genrePred, 'embedding_model'):
        genrePred.embedding_model = TensorflowPredictEffnetDiscogs(graphFilename="data/discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
    embedding_model = genrePred.embedding_model

    embeddings = embedding_model(audio)

    if not hasattr(genrePred, 'model'):
        genrePred.model = TensorflowPredict2D(graphFilename="data/genre_discogs400-discogs-effnet-1.pb", input="serving_default_model_Placeholder", output="PartitionedCall:0")
    model = genrePred.model

    predictions = model(embeddings)
    

    averagePred = np.mean(predictions, axis = 0)
    topGenres = averagePred.argsort()[::-1][:1]
    return genres[topGenres.item()]



