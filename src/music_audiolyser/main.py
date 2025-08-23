import sys

from .UI.UI import App


def run():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyze":
        from .core import song_pipeline

        song_pipeline.song_pipeline()
    else:
        run()
