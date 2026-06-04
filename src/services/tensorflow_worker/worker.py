from services.tensorflow_worker.tensorflow import process
from services.shared.tfsocket import TFWorkerSocket
from pyee import EventEmitter

import asyncio as aio
import logging

# Setting up the custom colored logger

from services.logging.custom import CustomFormatter as cf

logger = logging.getLogger("Tensorflow")
logger.setLevel(logging.DEBUG)

colorlog = logging.StreamHandler()
colorlog.setLevel(logging.DEBUG)
colorlog.setFormatter(cf())

logger.addHandler(colorlog)

# Variables

ee = EventEmitter()
socket = TFWorkerSocket(eventEmitter=ee)
loop: aio.AbstractEventLoop = None


@ee.on("packet-received")
def handle_packet(data: str):
    if data.startswith(""):
        args = data.split(" ")
        args.pop(0)

        if len(args) == 0:
            return logger.error("No argument detected", exc_info=True)

        arg = args.pop(0)


async def main():
    aio.create_task(aio.to_thread(socket.createServerConnection))
    logger.info("Initialized socket")

    await aio.Event().wait()


if __name__ == "__main__":
    aio.run(main())
