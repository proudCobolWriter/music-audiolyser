import essentia.standard as es 

def pred(audio):  

    rhythmExtractor = es.RhythmExtractor2013()
    danceabilityAlg = es.Danceability()
    keyAlg = es.KeyExtractor()

    danceability = danceabilityAlg(audio)[0]

    key, scale = keyAlg(audio)[:2]
    bpm = rhythmExtractor(audio)[0]
    return round(bpm), danceability, key, scale