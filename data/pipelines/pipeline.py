import pickle

from sklearn.compose import ColumnTransformer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from core.utils.loader import MODEL_CONFIG, NUM_CORE, PATHS_CONFIG
from index import (
    ALL_GENRES,
    ALL_KEYS,
    ALL_MOODS,
    ALL_SCALES,
    CAT_FEATURES,
    NUM_FEATURES,
)


def safe_knn(n_neighbors, weights, num_core):
    try:
        knn = KNeighborsClassifier(
            n_neighbors=n_neighbors, weights=weights, n_jobs=num_core
        )
        _ = knn.fit([[0], [1]], [0, 1])
        print(f"[INFO] KNN created successfully with n_jobs={NUM_CORE}")
        return knn
    except Exception as e:
        print(f"[WARN] Multithreading not supported: {e}")
        print("[INFO] Falling back to single-thread mode")
        return KNeighborsClassifier(
            n_neighbors=n_neighbors, weights=weights, n_jobs=None
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
            safe_knn(
                n_neighbors=MODEL_CONFIG["knn"]["n_neighbors"],
                weights=MODEL_CONFIG["knn"]["weights"]["value"],
                num_core=NUM_CORE,
            ),
        ),
    ]
)


with open(PATHS_CONFIG["models"]["trained"]["knn"], "wb") as f:
    pickle.dump(pipeline, f)

print("[INFO] KNN pipeline created and saved successfully.")
