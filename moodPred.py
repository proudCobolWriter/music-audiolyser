from data.moods import moods
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs, TensorflowPredict2D
import numpy as np

def moodPred(audio):

    if not hasattr(moodPred, 'embeddingModel'):
        moodPred.embeddingModel = TensorflowPredictEffnetDiscogs(graphFilename="data/discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
    embeddingModel = moodPred.embeddingModel

    embeddings = embeddingModel(audio)

    if not hasattr(moodPred, 'model'):
        moodPred.model = TensorflowPredict2D(graphFilename="data/mtg_jamendo_moodtheme-discogs-effnet-1.pb")
    model = moodPred.model
    
    predictions = model(embeddings)



    averagePred = np.mean(predictions, axis = 0)
    topMoods = averagePred.argsort()[::-1][:1]
    return moods[topMoods.item()]

