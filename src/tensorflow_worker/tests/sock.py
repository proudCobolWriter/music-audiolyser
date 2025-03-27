import tensorflow_worker.tfsocket as tfsocket
import socket, time
import multiprocessing


def createS():
    s = tfsocket.TFWorkerSocket()
    s.createSocket()


p1 = multiprocessing.Process(target=createS)
p1.start()

time.sleep(1)
ls = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET -> IPv4, SOCK_STREAM -> ICP
ls.connect(("127.0.0.1", 65432))
ls.sendall("STOP".encode())
time.sleep(5)
ls.shutdown(socket.SHUT_RDWR)
ls.close()
