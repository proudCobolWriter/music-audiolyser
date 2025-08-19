
import pickle
from genres import genres
from moods import moods
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.neighbors import KNeighborsClassifier

allGenres = genres
allMoods = moods
allKeys = ["C", "D", "E", "F", "G", "A", "B","C#", "D#","F#", "G#", "A#","Db", "Eb","Gb", "Ab", "Bb"]
allScales = ["major", "minor"]


catFeatures = ["Genre", "Key", "Scale", "Mood"]
numFeatures = ["BPM", "Danceability"]
encoderDict = {}

preProcessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(categories=[allGenres, allKeys, allScales, allMoods], handle_unknown="ignore"), catFeatures),
        ("num", StandardScaler(), numFeatures)
    ]
)

pipeline = Pipeline(steps=[
    ("preProcessor", preProcessor),
    ("classifier", KNeighborsClassifier(n_neighbors=6))
])


with open("KNNpipeline.pkl", "wb") as f:
    pickle.dump(pipeline, f)

print("Pipeline KNN créé et sauvegardé")
