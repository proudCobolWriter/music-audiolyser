import logging


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    blue_underline = "\x1b[4;34m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    fmt = "<c>[%(asctime)s] [%(levelname)s] <u>[%(name)s->%(filename)s:%(lineno)d]:</u> %(message)s</c>"
    encoding = "utf-8"
    datefmt = "%H:%M:%S"

    def __init__(self, nonDefaultFormat=fmt):
        super().__init__()
        self.fmt = nonDefaultFormat
        
        replace_map = [
            "<c>"
        ]
        
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, self.datefmt, "%")
        return formatter.format(record)
