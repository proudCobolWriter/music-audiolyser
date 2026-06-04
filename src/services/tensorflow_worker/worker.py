from services.tensorflow_worker.tensorflow import process
from services.shared.tfsocket import TFWorkerSocket
from pyee import EventEmitter

from utils import Path, path_to_str, TF_ROOT_DIR, PROJECT_ROOT_DIR

from multiprocessing import Process

import asyncio as aio
import logging
import json

# Setting up the custom colored logger

from services.logging.custom import CustomFormatter as cf

logger = logging.getLogger("Tensorflow")
logger.setLevel(logging.DEBUG)

colorlog = logging.StreamHandler()
colorlog.setLevel(logging.DEBUG)
colorlog.setFormatter(cf())

logger.addHandler(colorlog)

# CONSTANTS

SONGS_DIR = PROJECT_ROOT_DIR / ".cache" / "songs"

# Variables

ee = EventEmitter()
socket = TFWorkerSocket(eventEmitter=ee)
loop: aio.AbstractEventLoop = None

def process_wrapper(id: str, path: Path):
    try:
        result = process(path)
        socket.send(f"GOT-RESULT-SONG {id} {result!r}")
    except Exception:
        logger.error("Error encountered during TensorFlow process", exc_info=True)

# TODO: make it so a new process isn't spawned for each job, implement a queue system like for YouTube

@ee.on("packet-received")
def handle_packet(data: str):
    if data.startswith("PROCESS-AUDIO"):
        args = data.split(" ")
        args.pop(0)

        if len(args) == 0:
            return logger.error("No song id argument detected", exc_info=True)

        id = args.pop(0)

        if len(id) != 11:
            return logger.error(f"Provided song id is too long! {len(id)} chars", exc_info=True)

        manifest_dir = SONGS_DIR / f"{id}.manifest.json"
        if not Path.exists(manifest_dir):
            return logger.error(f"File hasn't been processed yet by the YouTube service", exc_info=True)

        object, filename = None, ""

        with open(manifest_dir, "rt+") as f:
            content = f.read()
            object = json.loads(content)
            filename = object["path"]

        path = SONGS_DIR / filename

        if filename == "" or not Path.exists(path):
            return logger.error("Path not found", exc_info=True)

        #p = Process(target=process_wrapper, args=(id, path,),daemon=True)
        #p.start()
        socket.send("dsqjidsqjkdsqj")
        #process_wrapper(id, path)


async def main():
    aio.create_task(aio.to_thread(socket.createServerConnection))
    logger.info("Initialized socket")

    await aio.Event().wait()


if __name__ == "__main__":
    aio.run(main())
