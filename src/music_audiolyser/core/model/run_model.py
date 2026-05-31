import pandas as pd

from music_audiolyser.core.utils.constants import CAT_FEATURES, NUM_FEATURES, USED_MODEL


def run_model(song_request: dict):
    song_request = pd.DataFrame([song_request])

    song_request = song_request[CAT_FEATURES + NUM_FEATURES]

    print("[INFO] predicting listener...")

    predicted_name = USED_MODEL.predict(song_request)

    print("[INFO] prediction successfully executed!")

    return predicted_name
