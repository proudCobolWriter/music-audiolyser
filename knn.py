import pandas as pd
import pickle
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from predictSong import predictSong
from sklearn.model_selection import cross_val_score

df = pd.read_csv("chart.csv")
features = ["Genre", "BPM", "Danceability", "Key", "Scale", "Mood"]
X = df[features]
Y = df["Name"]


with open("data/KNNpipeline.pkl", "rb") as f:
    pipeline = pickle.load(f)



Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=0.2, random_state=42)
pipeline.fit(Xtrain, Ytrain)



songRequest = predictSong()

predictedName = pipeline.predict(songRequest)


print("Score du KNN :", pipeline.score(Xtest, Ytest))
print(f"Cette chanson correspond le plus aux gouts de : {predictedName[0]}")