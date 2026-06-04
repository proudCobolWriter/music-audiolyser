from django.apps import AppConfig
from logging import getLogger

from .services.tf_connection import socket, ee

from threading import Thread
import os


class MusicAppConfig(AppConfig):
    name = "music_app"
    verbose_name = "Music Audiolyser"

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":  # get rid of the duplicate log
            return

        logger = getLogger(self.name)
        logger.info(f"{self.verbose_name} is ready!")

        self.logger = logger
        self.socket = socket
        self.eventEmitter = ee

        self.sthread = Thread(target=socket.createClientConnection, daemon=True)
        self.sthread.start()

        logger.info(f"Socket is ready at thread {self.sthread.ident}!")
