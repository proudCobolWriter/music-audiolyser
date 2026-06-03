from multiprocessing import Process, Queue
from .services.youtube_worker.youtube import YTDownloader

import asyncio

command_queue = Queue()
process = None


def worker_loop(queue):
    downloader = YTDownloader()

    while True:
        url = queue.get()

        if url is None:
            break

        downloader.download(url)


def downloader_main(queue):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    downloader = YTDownloader(workers=3)

    async def bridge():
        while True:
            url = await asyncio.to_thread(queue.get)

            downloader.enqueue(url)

    loop.create_task(downloader.start())
    loop.create_task(bridge())

    loop.run_forever()


def start_downloader():
    global process

    process = Process(
        target=downloader_main,
        args=(command_queue,),
        daemon=True,
    )

    process.start()
