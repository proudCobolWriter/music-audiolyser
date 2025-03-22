from logging.handlers import TimedRotatingFileHandler


def custom_namer(default_name):
    # custom logging function to reverse the date before the .log extension (to have vscode highlighting as usual)
    # Example: Rename 'app.log.1' to 'app.1.log'
    base, ext = default_name.rsplit(".", 1)
    return f"{base}.{ext}.log"


class CustomRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namer = custom_namer
