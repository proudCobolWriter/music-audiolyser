import importlib.util
import sqlite3
import sys
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .loader import get_available_cores, load_json


def _get_root_dir() -> Path:
    """
    Resolves the root directory of the project in both dev and compiled modes.

    - In compiled mode (PyInstaller): returns the folder containing the executable,
      so that the 'data/' folder placed next to it can be found.
    - In dev mode: walks up the directory tree from this file until it finds
      the project root folder (named 'music-audiolyser' or 'music-audiolyser-python-program').

    Returns:
        Path: Absolute path to the project root directory.

    Raises:
        RuntimeError: If the root folder cannot be found (dev mode only).
    """
    if getattr(sys, "frozen", False):
        # Compiled mode (PyInstaller): the executable sits next to the 'data/' folder
        return Path(sys.executable).parent
    else:
        # Dev mode: walk up until we find the project root by name
        p = Path(__file__).resolve()
        while p.name not in ("music-audiolyser", "music-audiolyser-python-program"):
            if p.parent == p:
                raise RuntimeError(
                    "[WARN] The root of this project is impossible to find"
                )
            p = p.parent
        return p


ROOT_DIR = _get_root_dir()


# ──────────────────────────────────────────────
# Default config values
# Used as fallback if a config file is missing,
# empty, or contains unrecognised keys.
# ──────────────────────────────────────────────

DEFAULT_UI = {
    "theme": "dark",
    "color_theme": "blue",
    "window_size": "700x530",
    "font": "Arial",
    "title": "Music Audiolyser",
}

DEFAULT_MODEL = {
    "default_model": "KNN",
    "available_models": ["KNN", "Random Forest", "Neural N."],
    "use_gpu": False,
    "KNN": {"n_neighbors": 5, "weights": "distance"},
    "Random Forest": {
        "n_estimators": 200,
        "max_depth": None,
        "min_samples_split": 2,
        "min_samples_leaf": 1,
        "n_jobs": -1,
        "criterion": "gini",
        "bootstrap": True,
    },
    "Neural N.": {
        "hidden_layer_sizes": [128, 64],
        "activation": "relu",
        "solver": "adam",
        "alpha": 0.0001,
        "batch_size": "auto",
        "learning_rate": "adaptive",
        "max_iter": 500,
        "early_stopping": True,
        "n_iter_no_change": 10,
        "verbose": False,
    },
}

# All paths are relative to ROOT_DIR.
# load_json() will convert them to absolute Path objects when ROOT_DIR is passed.
DEFAULT_PATHS = {
    "song_requests": "data/requests/song_req.txt",
    "db": "data/db/chart.sqlite3",
    "downloads": "data/songs/",
    "models": {
        "pretrained": {
            "embedding_model": "data/models/pretrained/jamendo/discogs-effnet-bs64-1.pb",
            "mtg_jamendo_genre": "data/models/pretrained/jamendo/mtg_jamendo_genre-discogs-effnet-1.pb",
            "mtg_jamendo_moodtheme": "data/models/pretrained/jamendo/mtg_jamendo_moodtheme-discogs-effnet-1.pb",
        },
    },
    "ui_images": {
        "main_menu_img": "data/images/main_menu_alt.jpg",
        "loading_gear": "data/images/gear.png",
    },
}

CONFIG_FILES = {
    "ui.json": DEFAULT_UI,
    "model.json": DEFAULT_MODEL,
    "paths.json": DEFAULT_PATHS,
}


# ──────────────────────────────────────────────
# Config loading
# ──────────────────────────────────────────────

CONFIG_DIR = ROOT_DIR / "data" / "config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

UI_CONFIG = load_json(CONFIG_DIR / "ui.json", DEFAULT_UI)
MODEL_CONFIG = load_json(CONFIG_DIR / "model.json", DEFAULT_MODEL)
# ROOT_DIR is passed so that relative string paths in paths.json
# are automatically converted to absolute Path objects.
PATHS_CONFIG = load_json(CONFIG_DIR / "paths.json", DEFAULT_PATHS, ROOT_DIR)

NUM_CORE = get_available_cores()

# yt-dlp output template: saves files as 'data/songs/<title>.<ext>'
YT_DL_OUTPUT = str(Path(PATHS_CONFIG["downloads"]) / "%(title)s.%(ext)s")
YT_DLP_AUDIO_FORMAT = "mp3"


def _load_label(filename: str):
    """
    Dynamically loads a Python file from 'data/labels/' at runtime.

    This avoids a direct 'from data.labels.x import x' which would make
    'data' a Python package embedded inside the compiled executable.
    By loading the file dynamically, 'data/' can remain external and editable.

    Args:
        filename (Path): Filename of the label module (e.g. Path("genres.py")).

    Returns:
        module: The loaded Python module, whose attributes can be accessed normally.
    """
    path = ROOT_DIR / "data" / "labels" / filename
    spec = importlib.util.spec_from_file_location(filename.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ──────────────────────────────────────────────
# Analysis constants
# ──────────────────────────────────────────────

# Features used to train and run the classifier
FEATURES = ["genre", "bpm", "danceability", "key", "scale", "mood"]


ALL_KEYS = [
    "C",
    "D",
    "E",
    "F",
    "G",
    "A",
    "B",
    "C#",
    "D#",
    "F#",
    "G#",
    "A#",
    "Db",
    "Eb",
    "Gb",
    "Ab",
    "Bb",
]

ALL_SCALES = ["major", "minor"]

# Loaded dynamically so that 'data/' stays outside the compiled executable
ALL_MOODS = _load_label(Path("moods.py")).moods
ALL_GENRES = _load_label(Path("genres.py")).genres

# Feature categories for the sklearn ColumnTransformer
CAT_FEATURES = ["genre", "key", "scale", "mood"]
NUM_FEATURES = ["bpm", "danceability"]

# Default seed data loaded from 'data/labels/'
DEFAULT_SONGS = _load_label(Path("default_songs.py")).default_songs
DEFAULT_STUDENTS = _load_label(Path("default_students.py")).default_students
DEFAULT_SONG_LISTENERS = _load_label(
    Path("default_song_listeners.py")
).default_song_listeners


# ──────────────────────────────────────────────
# Database helpers
# ──────────────────────────────────────────────


def get_connection():
    """Opens and returns a connection to the SQLite database."""
    conn = sqlite3.connect(PATHS_CONFIG["db"])
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


def init_db():
    """
    Initialises the database schema by executing scheme.sql.
    Uses IF NOT EXISTS statements, so it is safe to call on every startup.
    """
    conn = get_connection()
    cursor = conn.cursor()

    with open(ROOT_DIR / "data" / "db" / "scheme.sql", "r") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()


def is_db_empty(conn) -> bool:
    """Returns True if the songs table contains no rows."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM music_app_song")
    return cursor.fetchone()[0] == 0


def seed_db():
    """
    Populates the database with default songs, students and listeners
    defined in 'data/labels/'. Skips seeding if data is already present.
    """
    conn = get_connection()
    cur = conn.cursor()

    if not is_db_empty(conn):
        print("[INFO] DB already populated → skipping seed")
        conn.close()
        return

    print("[INFO] Seeding database...")

    # Clear any partially inserted data before seeding
    cur.execute("DELETE FROM music_app_song_listeners")
    cur.execute("DELETE FROM music_app_song")
    cur.execute("DELETE FROM music_app_student")

    cur.executemany(
        "INSERT INTO music_app_student (name) VALUES (?)",
        DEFAULT_STUDENTS,
    )

    cur.executemany(
        """
        INSERT INTO music_app_song (
            youtube_id, title, artist, genre,
            bpm, danceability, key, scale, mood
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        DEFAULT_SONGS,
    )

    cur.executemany(
        "INSERT INTO music_app_song_listeners (student_id, song_id) VALUES (?, ?)",
        DEFAULT_SONG_LISTENERS,
    )

    conn.commit()
    conn.close()
    print("[INFO] DB seeded successfully")


# ──────────────────────────────────────────────
# Model helpers
# ──────────────────────────────────────────────


def load_training_data():
    """
    Queries the database and returns a DataFrame with one row per
    (song, listener) pair, including all features used for training.
    """
    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT
            s.genre, s.bpm, s.danceability,
            s.key, s.scale, s.mood,
            st.name AS listener
        FROM music_app_song s
        JOIN music_app_song_listeners sl ON sl.song_id = s.id
        JOIN music_app_student st        ON st.id = sl.student_id
        """,
        conn,
    )

    conn.close()
    return df


def get_model(model_type: str, params: dict, num_core: int):
    """
    Instantiates the sklearn estimator matching model_type.

    Args:
        model_type (str): One of 'KNN', 'Random Forest', 'Neural N.'.
        params (dict): Hyperparameters from MODEL_CONFIG.
        num_core (int): Number of CPU cores to use (where supported).

    Returns:
        sklearn estimator: An unfitted classifier instance.

    Raises:
        ValueError: If model_type is not recognised.
    """
    if model_type == "KNN":
        return KNeighborsClassifier(
            n_neighbors=params.get("n_neighbors", 5),
            weights=params.get("weights", "distance"),
            n_jobs=num_core,
        )
    elif model_type == "Random Forest":
        return RandomForestClassifier(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", None),
            n_jobs=num_core,
            random_state=42,
        )
    elif model_type == "Neural N.":
        return MLPClassifier(
            hidden_layer_sizes=params.get("hidden_layer_sizes", (100,)),
            activation=params.get("activation", "relu"),
            learning_rate_init=params.get("learning_rate_init", 0.001),
            max_iter=params.get("max_iter", 300),
            random_state=42,
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def build_pipeline(model_type: str, model_params: dict, num_core: int) -> Pipeline:
    """
    Builds a full sklearn Pipeline combining preprocessing and classification.

    The preprocessor applies:
    - OneHotEncoding on categorical features (genre, key, scale, mood)
    - StandardScaling on numerical features (bpm, danceability)

    Args:
        model_type (str): Classifier type ('KNN', 'Random Forest', 'Neural N.').
        model_params (dict): Hyperparameters for the chosen classifier.
        num_core (int): Number of CPU cores to allocate.

    Returns:
        Pipeline: An unfitted sklearn Pipeline ready to call .fit() on.
    """
    print("[INFO] Building model using database...")

    pre_processor = ColumnTransformer(
        [
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

    model = get_model(model_type, model_params, num_core)

    return Pipeline(
        [
            ("pre_processor", pre_processor),
            ("classifier", model),
        ]
    )


def get_model_from_config() -> Pipeline:
    """
    Builds and fits the classifier pipeline using the current database
    and the model type / hyperparameters defined in model.json.

    Returns:
        Pipeline: A fitted sklearn Pipeline ready for prediction.
    """
    df = TRAINING_DATA

    # X = features to learn from, y = listener to predict
    X = df[CAT_FEATURES + NUM_FEATURES]
    y = df["listener"]

    model_type = MODEL_CONFIG["default_model"]
    model_params = MODEL_CONFIG[model_type]

    model = build_pipeline(
        model_type=model_type,
        model_params=model_params,
        num_core=NUM_CORE,
    )

    model.fit(X, y)
    print(f"[INFO] {model_type.upper()} model loaded successfully")

    return model


def add_song_to_data(song: dict, student_name: str):
    """
    Inserts a new song and its listener into the database.
    Creates the student record if it does not already exist.

    Args:
        song (dict): Song metadata with keys matching the music_app_song columns.
        student_name (str): Name of the student who listens to this song.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch or create the student
    cursor.execute("SELECT id FROM music_app_student WHERE name = ?", (student_name,))
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            "INSERT INTO music_app_student (name) VALUES (?)", (student_name,)
        )
        student_id = cursor.lastrowid
    else:
        student_id = row["id"]

    cursor.execute(
        """
        INSERT INTO music_app_song (
            youtube_id, title, artist, genre,
            bpm, danceability, key, scale, mood
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            song["youtube_id"],
            song["title"],
            song["artist"],
            song["genre"],
            song["bpm"],
            song["danceability"],
            song["key"],
            song["scale"],
            song["mood"],
        ),
    )

    song_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO music_app_song_listeners (student_id, song_id) VALUES (?, ?)",
        (student_id, song_id),
    )

    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# Startup sequence
# ──────────────────────────────────────────────

init_db()
print("[INFO] Database initialised successfully")

seed_db()

TRAINING_DATA = load_training_data()

# Fit the model once at import time so it is ready for the entire session
USED_MODEL = get_model_from_config()
