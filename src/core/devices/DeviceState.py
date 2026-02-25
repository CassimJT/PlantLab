# This Python file uses the following encoding: utf-8
from enum import IntEnum

class DeviceState(IntEnum):
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    ERROR = 3

