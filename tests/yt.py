if __name__ != "__main__":
    raise ImportError(f"{__name__} is not a module, aborting")

from services.shared.ytb import YTDownloader

import asyncio

# static downloads test
# YTDownloader.download("https://www.youtube.com/watch?v=IU2wBKoDOzg") # the man who sold the world
# YTDownloader.download("https://www.youtube.com/watch?v=JGwWNGJdvx8") # shape of you
# YTDownloader.download("https://www.youtube.com/watch?v=m4sITdduLRU") # kino
# YTDownloader.download("https://www.youtube.com/watch?v=XEjLoHdbVeE") # abba

# playlist test
# YTDownloader.download("https://www.youtube.com/watch?v=OPf0YbXqDm0&list=PLMC9KNkIncKvYin_USF1qoJQnIyMAfRxl") # pop music playlist (180 items)


async def main():
    downloader = YTDownloader()

    await downloader.start()

    downloader += [
        "https://www.youtube.com/watch?v=XEjLoHdbVeE",
        "https://www.youtube.com/watch?v=XEjLoHdbVeE",
        "https://www.youtube.com/watch?v=IU2wBKoDOzg",
        "https://www.youtube.com/watch?v=JGwWNGJdvx8",
        "https://www.youtube.com/watch?v=m4sITdduLRU",
        "https://www.youtube.com/watch?v=XEjLoHdbVeE",
    ]

    print("Printing queue (start of processing):", len(downloader))  # 4

    await asyncio.sleep(2)
    await downloader.wait()

    print("Printing queue (end of processing):", len(downloader))  # 0


asyncio.run(main())
