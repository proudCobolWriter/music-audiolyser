# Music Audiolyser

![Python Version](https://img.shields.io/badge/python-3.9.18-blue)
![Coverage](https://img.shields.io/endpoint?url=https://gist.github.com/proudCobolWriter/<GIST_ID>/raw/badge.json)


## Description

Music Audiolyser is a school project that analyses songs' features and allows computing predictions using KNN (and maybe more in the future).
It serves as an exemple to demonstrate when machine learning can be useful.
This project also includes a basic UI to upload songs (currently only "Upload songs" works).


## Features

-Extract song features (tempo, key, duration, scale (minor and major))
-Use KNN models on to predict the hypothetical uploader
-Simple GUI for uploading songs


## Installation

1. Clone the repository:

```bash
git clone https://github.com/proudCobolWriter/music-audiolyser.git
```

2. Install dependecies wih Poetry:

```bash
poetry install
```

Or if you don't want to use Poetry, install with pip:

```bash
pip install -r requirements.txt
```

## Usage

Run the main application:
```bash
poetry run python main.py
```

Or without Poetry:

```bash
python main.py
```





### Powered by ESSENTIA AI and models, along with Tensor Flow.

![ESSENTIA](https://essentia.upf.edu/_static/essentia_logo.svg)


