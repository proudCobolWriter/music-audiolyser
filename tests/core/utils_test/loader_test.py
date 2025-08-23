import json
from pathlib import Path

from music_audiolyser.core.utils.loader import get_available_cores, load_json


def test_load_json_create_file_if_missing(tmp_path):
    file_path = tmp_path / "ui.json"
    default = {"theme": "dark"}

    data = load_json(file_path, default)

    assert data == default
    assert file_path.exists()
    with open(file_path, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert saved == default


def test_load_json_update_missing_keys(tmp_path):
    file_path = tmp_path / "model.json"
    default = {"a": 1, "b": 2}

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"a": 99}, f)

    data = load_json(file_path, default)

    assert data["a"] == 99
    assert data["b"] == 2


def test_load_json_convert_to_paths(tmp_path):
    file_path = tmp_path / "paths.json"
    default = {"downloads": "data/songs/"}

    data = load_json(file_path, default, root_dir=tmp_path)

    assert isinstance(data["downloads"], Path)
    assert str(data["downloads"]).endswith("data/songs")


def test_load_json_invalid_json(tmp_path):
    file_path = tmp_path / "bad.json"
    default = {"x": 1}

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("{invalid json")

    data = load_json(file_path, default)

    assert data == default
    assert file_path.exists()


def test_get_available_cores(monkeypatch):
    monkeypatch.setattr("multiprocessing.cpu_count", lambda: 8)
    cores = get_available_cores()
    assert cores == 4

    monkeypatch.setattr("multiprocessing.cpu_count", lambda: 1 / 0)
    cores = get_available_cores(default=2)
    assert cores == 2
