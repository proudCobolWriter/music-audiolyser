import essentia.standard as es


def pred(audio):
    rhythm_extractor = es.RhythmExtractor2013()
    danceability_alg = es.Danceability()
    key_alg = es.KeyExtractor()

    danceability = danceability_alg(audio)[0]
    key, scale = key_alg(audio)[:2]
    bpm = rhythm_extractor(audio)[0]

    return round(bpm), danceability, key, scale
