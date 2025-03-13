from otherPred import pred
from genrePred import genrePred
from moodPred import moodPred
import csv
from videoDownload import videoDownload


with open("songReq.txt", "r") as f:
    file = f.readlines()

for url in file:
    directory, artistName, title = videoDownload(url)
    genre  = genrePred(directory)
    bpm, danceability, key, scale = pred(directory)
    mood = moodPred(directory)
    fieldnames = ["Name", "Title", "Artist", "Genre", "BPM", "Danceability", "Key", "Scale", "Mood"]
    with open("chart.csv", "a", newline='') as c: 
            chart = csv.DictWriter(c, fieldnames)
            chart.writerow({"Name" : "Anonymous", "Title" : title , "Artist" : artistName, "Genre" :genre,
                            "BPM" :bpm, "Danceability" : danceability, "Key" : key, "Scale": scale, "Mood" : mood})

