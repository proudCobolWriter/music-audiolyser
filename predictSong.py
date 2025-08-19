from otherPred import pred
from genrePred import genrePred
from moodPred import moodPred
import pandas as pd
from videoDownload import videoDownload
import essentia.standard as es

def predictSong():

    songRequest = None

    url = str(input("URL de la chanson YouTube : \n")).strip()

    try :
        directory, _,_ = videoDownload(url)
        audio = es.MonoLoader(filename=directory, sampleRate= 16000, resampleQuality=4)()


        genre  = genrePred(audio)
        mood = moodPred(audio)
        audio = es.MonoLoader(filename=directory, sampleRate= 44100, resampleQuality=4)()
        bpm, danceability, key, scale = pred(audio)

        songRequest = pd.DataFrame([{
                "Genre" : genre,
                "BPM" : bpm,
                "Danceability" : danceability,
                "Key" : key,
                "Scale": scale,
                "Mood" : mood
            }])
        return songRequest

    except Exception as e:
        print("Erreur lors du traitement :", e)

        



