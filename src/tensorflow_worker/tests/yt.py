if __name__ != "__main__":
    raise ImportError(f"{__name__} is not a module, aborting")

from tensorflow_worker.services.yt_downloader import YTDownloader
import asyncio

# check ffmpeg and ffprobe
instance = YTDownloader()

# static downloads test
# YTDownloader.download("https://www.youtube.com/watch?v=IU2wBKoDOzg") # the man who sold the world
# YTDownloader.download("https://www.youtube.com/watch?v=JGwWNGJdvx8") # shape of you
# YTDownloader.download("https://www.youtube.com/watch?v=m4sITdduLRU") # kino
# YTDownloader.download("https://www.youtube.com/watch?v=XEjLoHdbVeE")  # abba

# playlist test
# YTDownloader.download("https://www.youtube.com/watch?v=OPf0YbXqDm0&list=PLMC9KNkIncKvYin_USF1qoJQnIyMAfRxl") # pop music playlist (180 items)

# queueing test
instance + [
    "https://www.youtube.com/watch?v=XEjLoHdbVeE",
    "https://www.youtube.com/watch?v=XEjLoHdbVeE",
    "https://www.youtube.com/watch?v=XEjLoHdbVeE",
]

print("Printing queue:", instance.Queue)  # one item


async def main():
    await asyncio.sleep(5)
    print("afdjqdsjq")
    # print(instance.__coqueue)


asyncio.run(main())
