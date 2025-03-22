from django.apps import AppConfig
from logging import getLogger


class MusicAppConfig(AppConfig):
    name = "music_app"
    verbose_name = "Music Audiolyser"

    def ready(self):
        logger = getLogger(self.name)
        logger.info(f"{self.verbose_name} is ready!")
