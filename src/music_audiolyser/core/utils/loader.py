import json
import multiprocessing
from pathlib import Path


def get_available_cores(default=1):
    try:
        allocated_cores = max(1, multiprocessing.cpu_count() // 2)
        print(
            f"[INFO] Allocating {allocated_cores} core(s) to run the models efficiently."
        )
        return allocated_cores

    except Exception:
        print(
            "[WARN] Unable to detect multiple cores. Defaulting to 1 core for model execution."
        )
        return default


NUM_CORE = get_available_cores()


def load_json(file_path: Path, default: dict, root_dir: Path = None):
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

    if root_dir:
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = Path(root_dir / v) if not Path(v).is_absolute() else Path(v)
        print(
            f"[INFO] Paths in {file_path} converted to Path objects using ROOT_DIR={root_dir}"
        )

    return data
