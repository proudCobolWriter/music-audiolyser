import socket
import logging

from tensorflow_worker.logging.custom import CustomFormatter as cf

# Setting up the custom colored logger

logger = logging.getLogger("Socket")
logger.setLevel(logging.DEBUG)

colorlog = logging.StreamHandler()
colorlog.setLevel(logging.DEBUG)
colorlog.setFormatter(cf())

logger.addHandler(colorlog)

# Constants

HOST = "127.0.0.1"  # should be localhost if the tensorflow worker is on the same server as the websites backend
PORT = 65432  # in which case, the socket shouldn't be available to other IPv4 interfaces than localhost
RECEIVE_BUFFER = 1024  # bits

# Static library exports


class TFWorkerSocket:
    def __init__(self, *_, **kwargs) -> None:
        self.PORT = PORT
        self.HOST = HOST
        self.__dict__.update(kwargs)

        if not (self.PORT >= 1024 and self.PORT <= 2**16):
            logger.warning("Port should be within the user registered port range")

        self.Running = False
        self.Socket = None

    def __repr__(self) -> None:
        fields = ", ".join(f"{i!r}={v!r}" for (i, v) in zip(self.__dict__.keys(), self.__dict__.values()))
        return f"{self.__class__.__name__}({fields})"

    def createSocket(self) -> None:
        logger.info("Creating the socket")
        if self.Socket is not None:
            return logger.warning("A socket has already been created. Consider closing it first.")

        try:
            self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET -> IPv4, SOCK_STREAM -> ICP
            self.Socket.bind((self.HOST, self.PORT))
            self.Socket.listen()
            logger.info(f"The socket is now listening on {self.HOST}:{self.PORT}")
        except socket.error:
            logger.error("Failed to setup the socket:", exc_info=True)
            self.Socket = None
        else:
            self.Running = True
            self.handleSocket()
        finally:
            self.closeSocket()

    def handleSocket(self) -> None:
        while self.Running:
            try:
                if self.__dict__.get("Connection") is None:
                    self.Connection, self.ClientAddress = self.Socket.accept()  # yields for a connection
                    logger.info(
                        f"Established connection with {self.ClientAddress} on {self.HOST}:{self.PORT} as expected"
                    )

                data = self.Connection.recv(1024)

                logger.info(f"Received {data} {self.ClientAddress}")
                if not data:  # or equals to ''
                    logger.info("Socket connection has been broken")
                    break
                self.Connection.sendall(data)

                logger.info(f"Sent all {data} {self.ClientAddress}")
            except socket.error:
                logger.error(
                    "Encountered an error while handling client connections (a RST request has likely been sent by the peer to disconnect)",
                    exc_info=True,
                )

    def closeSocket(self) -> None:
        if self.Socket is None:
            return

        self.Connection.close()
        self.Socket.close()
        self.Socket = None
        self.Connection, self.ClientAddress = None, None
        self.Running = False

        logger.info("The socket is now closed")
