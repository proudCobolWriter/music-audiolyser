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

# uncomment to check if logger works properly in console stream
# for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
#     logger.__getattribute__(level.lower())(f"Printing test string with {level = }")

# Constants

HOST = "127.0.0.1"  # should be localhost if the tensorflow worker is on the same server as the websites backend
PORT = 65432  # in which case, the socket shouldn't be available to other IPv4 interfaces than localhost
RECEIVE_BUFFER = 1024  # bits

# Socket manager class export


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
            self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                logger.debug(f"Received packet: {data = }")

                if not data:  # or equals to ''
                    logger.info("Socket connection has been severed, awaiting new connection")
                    # break
                    self.Connection, self.ClientAddress = None, None
                    continue

                decodedBuffer = data.decode()

                if decodedBuffer == "STOP":
                    logger.info('Socket connection is closing gracefully after a "STOP" request')
                    break

                self.Connection.sendall(data)
                logger.debug(f"Sent data: {data}")
            except socket.error:
                logger.error(
                    "Encountered an error while handling client connections (a RST request has likely been sent by the peer to disconnect)",
                    exc_info=True,
                )

    def closeSocket(self) -> None:
        if self.Socket is None:
            return

        self.Connection.shutdown(socket.SHUT_RDWR)
        self.Socket.shutdown(socket.SHUT_RDWR)
        self.Connection.close()
        self.Socket.close()

        self.Socket = None
        self.Connection, self.ClientAddress = None, None

        self.Running = False

        logger.info("The socket is now closed")
