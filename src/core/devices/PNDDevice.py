from PySide6.QtCore import QObject, Signal, Property
from DeviceState import DeviceState


class PNDDevice(QObject):

    deviceIdChanged = Signal()
    stateChanged = Signal()
    temperatureChanged = Signal()
    humidityChanged = Signal()

    def __init__(self, device_id: str = "", parent=None):
        super().__init__(parent)

        self._device_id = device_id
        self._state = DeviceState.DISCONNECTED
        self._temperature = 0.0
        self._humidity = 0.0

    # ======================================
    # Properties
    # ======================================

    @Property(str, notify=deviceIdChanged)
    def deviceId(self):
        return self._device_id

    # ----------------------------------

    @Property(int, notify=stateChanged)
    def state(self):
        return int(self._state)

    def setState(self, state: DeviceState):
        if self._state != state:
            self._state = state
            self.stateChanged.emit()

    # ----------------------------------

    @Property(float, notify=temperatureChanged)
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        if self._temperature != value:
            self._temperature = value
            self.temperatureChanged.emit()

    # ----------------------------------

    @Property(float, notify=humidityChanged)
    def humidity(self):
        return self._humidity

    @humidity.setter
    def humidity(self, value):
        if self._humidity != value:
            self._humidity = value
            self.humidityChanged.emit()
