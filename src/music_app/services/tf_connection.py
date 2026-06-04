from services.shared.tfsocket import TFWorkerSocket
from pyee import EventEmitter

ee = EventEmitter()
socket = TFWorkerSocket(eventEmitter=ee)
