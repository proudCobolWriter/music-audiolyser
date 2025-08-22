import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from core.preds.predict_song import predict_song
from core.utils.loader import PATHS_CONFIG
from index import FEATURES

df = pd.read_csv(PATHS_CONFIG["chart"])
X = df[FEATURES]
Y = df["Name"]


with open(PATHS_CONFIG["models"]["trained"]["knn"], "rb") as f:
    pipeline = pickle.load(f)


X_train, x_test, Y_train, y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42
)
pipeline.fit(X_train, Y_train)


song_request = predict_song()

predicted_name = pipeline.predict(song_request)


print("Score du KNN :", pipeline.score(x_test, y_test))
print(f"Cette chanson correspond le plus aux gouts de : {predicted_name[0]}")
