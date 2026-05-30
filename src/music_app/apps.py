from django.apps import AppConfig
from logging import getLogger

from .services.downloader_process import start_downloader

import os


class MusicAppConfig(AppConfig):
    name = "music_app"
    verbose_name = "Music Audiolyser"

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":  # get rid of the duplicate log
            return

        logger = getLogger(self.name)
        logger.info(f"{self.verbose_name} is ready!")

        start_downloader()
