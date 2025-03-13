import essentia.standard as es 

def pred(audio_file):  
    loader = es.MonoLoader(filename=audio_file)
    audio = loader()

    rhythm_extractor = es.RhythmExtractor2013()
    danceabilityAlg = es.Danceability()
    keyAlg = es.KeyExtractor()

    danceability, dfa  = danceabilityAlg(audio)

    key, scale, strength = keyAlg(audio)
    bpm, beats, beatsConfidence, _, _ = rhythm_extractor(audio)
    return round(bpm), danceability, key, scale