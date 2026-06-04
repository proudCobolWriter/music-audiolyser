# Music Audiolyser

![Python Version](https://img.shields.io/badge/python-3.9.18-blue)

## Description

Music Audiolyser is a school project that analyses the features of various songs allowing the computation of predictions using KNN (and maybe more in the future).
It serves as an example to demonstrate when machine learning can be useful.
This project also includes a basic UI to upload songs (currently only "Upload songs" works).

## Features

- Extracts song features (tempo, key, duration, scale (minor and major), etc)
- Uses KNN models to predict the hypothetical uploader
- Simple GUI for uploading songs

## How can I start it?

### Clone the repository

...

### Download FFmpeg

### Download sqlite3 (and libsqlite3-dev)

#### Windows

$ winget install -e --id Gyan.FFmpeg

#### Debian

$ sudo apt-get install ffmpeg

### Get the correct Python version (3.13.13)

#### Windows

$ winget install python.python.3.9 --version="3.9.18"

$ py -3.9 --version
-> it should output "Python 3.9.18"

#### Debian

```
$ sudo apt update
$ sudo apt install -y build-essential zlib1g-dev libncurses-dev libgdbm-dev \
libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev \
wget curl llvm libbz2-dev xz-utils tk-dev liblzma-dev libncursesw6

$ cd /usr/src
$ sudo wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
$ sudo tar xzf Python-3.9.18.tgz
$ cd Python-3.9.18

$ sudo ./configure --enable-optimizations --with-ensurepip=install
$ sudo make altinstall

$ python3.9 --version
-> it should output "Python 3.9.18"
```

### Create a virtual environment

#### Windows

$ py -3.9 -m pip install --user virtualenv
$ py -3.9 -m venv .venv

#### Linux

$ python3.9 -m pip install --user virtualenv
$ python3.9 -m venv .venv

### Activate the virtual environment

#### Windows

$ .venv\Scripts\activate

#### macOS and Linux

$ source .venv/bin/activate

## TODO:

[ ] - Deploy it to ASGI standard<br/>
[ ] - Deploy with Docker and Dockerfile<br/>
[ ] - Prettify the code with some python analog<br/>
[ ] - Add 404 page view and pathing<br/>
[ ] - Transition to Celery and Redis/RabbitMQ<br/>
[ ] - Check cache if the song already exists<br/>
[ ] - Upgrade the socket from synchronous to asynchronous design<br />
[ ] - Remove cleanly the .json files when purging cache<br />
[ ] - Split App.tsx in different components<br />
[ ] - Make the log stream colored everywhere included in the Django context<br />
[ ] - Add a progress bar to the YTB/TF downloads

### Powered by ESSENTIA AI and models, along with Tensor Flow.

![ESSENTIA](https://essentia.upf.edu/_static/essentia_logo.svg)
