from services.shared.tfsocket import TFWorkerSocket
from services.youtube_worker.youtube import YTDownloader
from pyee import EventEmitter

import asyncio as aio
import logging

# Setting up the custom colored logger

from services.logging.custom import CustomFormatter as cf

logger = logging.getLogger("YTWorker")
logger.setLevel(logging.DEBUG)

colorlog = logging.StreamHandler()
colorlog.setLevel(logging.DEBUG)
colorlog.setFormatter(cf())

logger.addHandler(colorlog)

# Variables

ee = EventEmitter()
socket = TFWorkerSocket(eventEmitter=ee)
downloader = YTDownloader(eventEmitter=ee)
loop: aio.AbstractEventLoop = None


@ee.on("packet-received")
def handle_packet(data: str):
    if data.startswith("ADD-VIDEO"):
        args = data.split(" ")
        args.pop(0)

        if len(args) == 0:
            return logger.error("No URL argument detected", exc_info=True)

        url = args.pop(0)

        if url == "" or not YTDownloader.extract_id(url):
            return logger.warning("The provided URL was either empty or invalid")

        downloader.enqueue(url)


@ee.on("dl-response")
def handle_download(data: str):
    socket.send("CHECK-SONG " + data)


async def stop():
    await downloader.stop()


async def main():
    await downloader.start()
    logger.info("Initialized downloader")

    aio.create_task(aio.to_thread(socket.createServerConnection))
    logger.info("Initialized socket")

    await aio.Event().wait()


if __name__ == "__main__":
    aio.run(main())
