import socket
import logging

from services.logging.custom import CustomFormatter as cf

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

# CONSTANTS

HOST = "127.0.0.1"  # should be localhost if the tensorflow worker is on the same server as the websites backend
PORT = 65432  # in which case, the socket shouldn't be available to other IPv4 interfaces than localhost
RECEIVE_BUFFER = 1024  # bits

# TODO: make the server connection logic support multiple clients
CLIENT_POOL_MAX_SIZE = 10  # rough estimate of the number of services to be expected

# Socket manager class export


class TFWorkerSocket:
    def __init__(self, *_, **kwargs) -> None:
        self.ADDRESS = HOST
        self.PORT = PORT

        self.eventEmitter = kwargs.pop("eventEmitter", None)
        self.__dict__.update(kwargs)

        if not (self.PORT >= 1024 and self.PORT <= 2**16):
            logger.warning("Port should be within the user registered port range")

        self.Socket = None
        self.Connection = None

        self.running = False
        self.server_socket = False

    def __repr__(self) -> None:
        fields = ", ".join(f"{k!r}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"

    def __str__(self) -> None:
        return self.__repr__()

    def createServerConnection(self) -> None:
        logger.info("Creating the socket (server)")
        if self.Socket is not None:
            return logger.warning("A socket has already been created. Consider closing it first.")

        try:
            self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET -> IPv4, SOCK_STREAM -> TCP
            self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.Socket.bind((self.ADDRESS, self.PORT))
            self.Socket.listen(CLIENT_POOL_MAX_SIZE)
            self.Socket.setblocking(True)  # make socket operations yield
            logger.info(f"The socket is now listening on {self.ADDRESS}:{self.PORT}")
        except socket.error:
            logger.error("Failed to setup the socket:", exc_info=True)
            self.Socket = None
        else:
            self.running = True
            self.server_socket = True
            self.handleServerConnection()
        finally:
            self.closeConnection()

    def handleServerConnection(self) -> None:
        while self.running:
            try:
                if self.__dict__.get("Connection") is None:
                    self.Connection, self.ClientAddress = self.Socket.accept()  # yields for a connection
                    logger.info(
                        f"Established connection with {self.ClientAddress} on {self.ADDRESS}:{self.PORT} as expected"
                    )

                data = self.Connection.recv(RECEIVE_BUFFER)
                decodedBuffer = data.decode().strip()

                logger.debug(f"Received packet: {decodedBuffer = }")

                if not data:
                    logger.info("Socket connection has been severed, awaiting new connection")
                    self.Connection, self.ClientAddress = None, None
                    continue

                if decodedBuffer == "STOP":
                    logger.info('Socket connection is closing gracefully after a "STOP" request')
                    break

                ee = self.__dict__.get("eventEmitter")

                if ee:
                    ee.emit("packet-received", decodedBuffer)

                # The following essentially acts like a request mirrorer/forwarder to all clients on the line
                # self.Connection.sendall(data)
                # logger.debug(f"Sent data: {decodedBuffer}")
            except socket.error:
                logger.error(
                    "Encountered an error while handling client connections (a RST request has likely been sent by the peer to disconnect)",
                    exc_info=True,
                )

    def closeConnection(self) -> None:
        if self.Socket is None:
            return
        else:
            try:
                self.Socket.shutdown(socket.SHUT_RDWR)
                self.Socket.close()
            except OSError:
                pass

            self.Socket = None

        if self.Connection:
            try:
                self.Connection.shutdown(socket.SHUT_RDWR)
                self.Connection.close()
            except OSError:
                pass

            self.Connection, self.ClientAddress = None, None

        self.running = False

        logger.info("The socket is now closed")

    def createClientConnection(self) -> None:
        logger.info("Creating the socket (client)")
        if self.Socket is not None:
            return logger.warning("A socket has already been created. Consider closing it first.")

        try:
            self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET -> IPv4, SOCK_STREAM -> TCP
            self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.Socket.setblocking(True)  # make socket operations yield
            self.Socket.connect((self.ADDRESS, self.PORT))
            logger.info(f"The socket is now connected to server socket {self.ADDRESS}:{self.PORT}")
        except socket.error:
            logger.error("Failed to setup the socket:", exc_info=True)
            self.Socket = None
        else:
            self.running = True
            self.server_socket = False
            self.handleClientConnection()
        finally:
            self.closeConnection()

    def handleClientConnection(self) -> None:
        while self.running:
            try:
                data = self.Socket.recv(RECEIVE_BUFFER)  # yields for an incoming message
                decodedBuffer = data.decode().strip()

                if not decodedBuffer:
                    continue

                logger.info(f"Reading packet from {self.ADDRESS}:{self.PORT}, {decodedBuffer = }")

                if decodedBuffer == "STOP":
                    logger.info('Socket connection is closing gracefully after a "STOP" request')
                    break

                ee = self.__dict__.get("eventEmitter")

                if ee:
                    ee.emit("packet-received", decodedBuffer)
            except socket.error:
                logger.error(
                    "Encountered an error while communicating with the server",
                    exc_info=True,
                )

    def send(self, data: str) -> None:
        if self.Socket is None:
            logger.warning("Attempt to send bytes but the socket hasn't been started yet")
            return

        try:
            if self.server_socket:
                if self.Connection is None:
                    raise ConnectionResetError("Missing socket connection to client(s)")

                self.Connection.sendall(data.encode())
            else:
                self.Socket.sendall(data.encode())
        except (BrokenPipeError, ConnectionResetError, OSError):
            logger.error("Encountered an error while sending packet through socket", exc_info=True)
