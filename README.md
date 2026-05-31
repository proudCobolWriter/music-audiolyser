# Music Audiolyser

![Python Version](https://img.shields.io/badge/python-3.9.18-blue)
![License](https://img.shields.io/badge/license-GPL--3.0-green)

> [!WARNING]
> This project is only supported on **Linux**. The Windows build is not functional due to `essentia-tensorflow` having no Windows support.

A school project that analyses song features and predicts their hypothetical uploader using machine learning models (KNN, Random Forest, Neural Network).

---

## Features

- **Song analysis** — extracts tempo, key, scale (major/minor), danceability and mood
- **ML prediction** — predicts the hypothetical uploader using KNN, Random Forest or Neural Network
- **Simple GUI** — built with CustomTkinter for uploading and browsing songs
- **YouTube download** — fetches audio directly from a YouTube URL via yt-dlp
- **SQLite database** — stores songs, students and listening history locally

---

## Requirements

- Python 3.9.18
- [Poetry](https://python-poetry.org/) (recommended) or pip

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/proudCobolWriter/music-audiolyser.git
cd music-audiolyser
git checkout python-program
```

2. Install dependencies:

**With Poetry (recommended):**
```bash
poetry install
```

**With pip:**
```bash
pip install -r requirements.txt
```

---

## Usage

**With Poetry:**
```bash
poetry run audiolyser
```

**Without Poetry:**
```bash
python src/music_audiolyser/main.py
```

---

## Compiled executable

Pre-built binaries for Linux and Windows are available in the [Actions](../../actions) tab under the latest workflow run (see the **Artifacts** section at the bottom of the page).

The `data/` folder must be placed **next to the executable** for it to work:
```
dist/
├── main          # or main.exe on Windows
└── data/
    ├── config/
    ├── db/
    ├── models/
    └── ...
```

To build it yourself:
```bash
poetry run pyinstaller main.spec
```

---

## Configuration

All config files live in `data/config/` and are created automatically on first launch with sensible defaults. You can edit them freely without recompiling.

- ui.json | Theme, window size, font |
- model.json | Active model type and hyperparameters |
- paths.json | Paths to the database, downloads folder, models |

---

## Powered by

[![ESSENTIA](https://essentia.upf.edu/_static/essentia_logo.svg)](https://essentia.upf.edu)

[Essentia](https://essentia.upf.edu) — open-source audio analysis library by MTG · [TensorFlow](https://www.tensorflow.org) · [scikit-learn](https://scikit-learn.org) · [yt-dlp](https://github.com/yt-dlp/yt-dlp) · [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)