import logging
from colorist import Color, BgColor, BrightColor, BgBrightColor, Effect


class CustomFormatter(logging.Formatter):
    fmt = f"{Effect.UNDERLINE_OFF}[%(asctime)s] {Effect.REVERSE}[%(levelname)s]{Effect.REVERSE_OFF} {Effect.UNDERLINE}[%(name)s -> %(filename)s:%(lineno)d]{Effect.UNDERLINE_OFF}: %(message)s"
    encoding = "utf-8"
    datefmt = "%H:%M:%S"

    def __init__(self, nonDefaultFormat=fmt):
        super().__init__()
        self.fmt = nonDefaultFormat

        self.FORMATS = {
            logging.DEBUG: "".join([str(Color.BLUE), self.fmt, str(Color.OFF)]),
            logging.INFO: "".join([str(Color.GREEN), self.fmt, str(Color.OFF)]),
            logging.WARNING: "".join([str(Color.YELLOW), self.fmt, str(Color.OFF)]),
            logging.ERROR: "".join([str(Color.RED), self.fmt, str(Color.OFF)]),
            logging.CRITICAL: "".join(
                [str(Effect.BOLD), str(Color.RED), self.fmt, str(Color.OFF), str(Effect.BOLD_OFF)]
            ),
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, self.datefmt, "%")
        return formatter.format(record)
