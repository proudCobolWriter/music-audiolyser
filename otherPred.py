import essentia.standard as es 

def pred(audio):  

    rhythm_extractor = es.RhythmExtractor2013()
    danceabilityAlg = es.Danceability()
    keyAlg = es.KeyExtractor()

    danceability = danceabilityAlg(audio)[0]

    key, scale = keyAlg(audio)[:2]
    bpm= rhythm_extractor(audio)[0]
    return round(bpm), danceability, key, scale