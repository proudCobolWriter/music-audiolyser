import pickle
import pandas as pd

from music_audiolyser.core.utils.constants import CAT_FEATURES, NUM_FEATURES
from music_audiolyser.core.utils.loader import PATHS_CONFIG


def run_knn(song_request: dict):

    with open(PATHS_CONFIG["models"]["trained"]["knn"], "rb") as f:
        pipeline = pickle.load(f)

    song_request = pd.DataFrame([song_request])


    song_request = song_request[CAT_FEATURES + NUM_FEATURES]


    predicted_name = pipeline.predict(song_request)

    return predicted_name
