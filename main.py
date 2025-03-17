from otherPred import pred
from genrePred import genrePred
from moodPred import moodPred
import csv
from videoDownload import videoDownload
import essentia.standard as es

FIELDNAMES = ["Name", "Title", "Artist", "Genre", "BPM", "Danceability", "Key", "Scale", "Mood"]

with open("songReq.txt", "r") as f:
    file = f.readlines()

for url in file:
    try:
        directory, artistName, title = videoDownload(url)
        audio = es.MonoLoader(filename=directory, sampleRate= 44100, resampleQuality=4)()
    except:
        continue

    genre  = genrePred(audio)
    bpm, danceability, key, scale = pred(audio)
    mood = moodPred(audio)

    with open("chart.csv", "a", newline='') as c: 
            chart = csv.DictWriter(c, FIELDNAMES)
            chart.writerow({"Name" : "Anonymous", "Title" : title , "Artist" : artistName, "Genre" :genre,
                            "BPM" :bpm, "Danceability" : danceability, "Key" : key, "Scale": scale, "Mood" : mood})

