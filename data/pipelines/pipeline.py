import pickle
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from music_audiolyser.core.utils.constants import (
    ALL_GENRES,
    ALL_KEYS,
    ALL_MOODS,
    ALL_SCALES,
    CAT_FEATURES,
    NUM_FEATURES,
)
from music_audiolyser.core.utils.loader import MODEL_CONFIG, NUM_CORE, PATHS_CONFIG



def create_knn(n_neighbors, weights, num_core):
    try:
        return KNeighborsClassifier(
            n_neighbors=n_neighbors,
            weights=weights,
            n_jobs=num_core,
        )
    except Exception:
        print("[WARN] Multithreading not supported, fallback to single thread")
        return KNeighborsClassifier(
            n_neighbors=n_neighbors,
            weights=weights,
        )


pre_processor = ColumnTransformer(
    transformers=[
        (
            "cat",
            OneHotEncoder(
                categories=[ALL_GENRES, ALL_KEYS, ALL_SCALES, ALL_MOODS],
                handle_unknown="ignore",
            ),
            CAT_FEATURES,
        ),
        ("num", StandardScaler(), NUM_FEATURES),
    ]
)

pipeline = Pipeline(
    steps=[
        ("pre_processor", pre_processor),
        (
            "classifier",
            create_knn(
                n_neighbors=MODEL_CONFIG["knn"]["n_neighbors"],
                weights=MODEL_CONFIG["knn"]["weights"]["value"],
                num_core=NUM_CORE,
            ),
        ),
    ]
)


df = pd.read_csv(PATHS_CONFIG["chart"])

X = df[CAT_FEATURES + NUM_FEATURES]
Y = df["Name"]

pipeline.fit(X, Y)

with open(PATHS_CONFIG["models"]["trained"]["knn"], "wb") as f:
    pickle.dump(pipeline, f)

print("[INFO] KNN trained and saved successfully.")


