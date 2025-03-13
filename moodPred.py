from header.moods import moods
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs, TensorflowPredict2D
import numpy as np

def moodPred(file):
    
    audio = MonoLoader(filename=file, sampleRate=16000, resampleQuality=4)()
    embedding_model = TensorflowPredictEffnetDiscogs(graphFilename="header/discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
    embeddings = embedding_model(audio)
    model = TensorflowPredict2D(graphFilename="header/mtg_jamendo_moodtheme-discogs-effnet-1.pb")
    predictions = model(embeddings)

    averagePred = np.mean(predictions, axis = 0)
    topMoods = averagePred.argsort()[::-1][:1]
    return moods[topMoods.item()]

