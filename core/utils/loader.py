import json
from pathlib import Path
import multiprocessing
from .constants import ROOT_DIR


DEFAULT_UI = {
    "theme": "dark",
    "window_size": "700x530",
    "font": "Arial",
    "title": "Music Audiolyser",
}

DEFAULT_MODEL = {
    "default_model": "knn",
    "available_models": ["knn", "random_forest", "neural_net"],
    "use_gpu": "False",
    "knn": {
        "n_neighbors": 5,
        "weights": {
            "value": "distance",
            "options": ["distance", "uniform"],
            "description": "Method to calculate the neighbors' contribution : 'uniform' = simple average, 'distance' = weighted average based on proximity",
        },
    },
}

DEFAULT_PATHS = {
    "song_requests": "data/requests/song_req.txt",
    "chart": "data/outputs/chart.csv",
    "downloads": "data/songs/",
    "models": {
        "trained": {"knn": "data/models/trained/knn.pkl"},
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

CONFIG_DIR = ROOT_DIR / "data" / "config"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_json(file_path: Path, default: dict):

    data = default.copy()
    need_save = False

    if file_path.exists() and file_path.stat().st_size > 0:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    for k, v in default.items():
                        if k not in loaded:
                            loaded[k] = v
                            need_save = True
                    data.update(loaded)
                else:
                    need_save = True
        except Exception as e:
            print(f"[WARN] {file_path} is invalid. Using defaults. ({e})")
            need_save = True
    else:
        print(f"[INFO] {file_path} not found or empty. Using defaults.")
        need_save = True

    if need_save:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[INFO] {file_path} updated with defaults or missing keys.")

    else:
        print(f"[INFO] {file_path} loaded successfully.")
    return data


UI_CONFIG = load_json(CONFIG_DIR / "ui.json", DEFAULT_UI)
MODEL_CONFIG = load_json(CONFIG_DIR / "model.json", DEFAULT_MODEL)
PATHS_CONFIG = load_json(CONFIG_DIR / "paths.json", DEFAULT_PATHS)


def get_available_cores(default=1):
    try:
        allocated_cores = max(1, multiprocessing.cpu_count() // 2)
        print(
            f"[INFO] Allocating {allocated_cores} core(s) to run the models efficiently."
        )
        return allocated_cores

    except:
        print(
            "[WARN] Unable to detect multiple cores. Defaulting to 1 core for model execution."
        )
        return default


NUM_CORE = get_available_cores()
