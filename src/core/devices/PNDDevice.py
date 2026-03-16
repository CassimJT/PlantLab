from PySide6.QtCore import QObject, Signal, Property, Slot
from .DeviceState import DeviceState
import json


class PNDDevice(QObject):

    deviceIdChanged = Signal()
    stateChanged = Signal()
    temperatureChanged = Signal(float)
    humidityChanged = Signal(float)
    lastSeenChanged = Signal()
    dataUpdated = Signal()

    def __init__(self, device_id: str = "", parent=None):
        super().__init__(parent)

        self._device_id = device_id
        self._state = DeviceState.DISCONNECTED
        self._temperature = 0.0
        self._humidity = 0.0
        self._last_seen = ""

        from datetime import datetime
        self._last_seen = datetime.now().isoformat()

    # ======================================
    # Properties
    # ======================================

    @Property(str, notify=deviceIdChanged)
    def deviceId(self):
        return self._device_id

    @deviceId.setter
    def deviceId(self, value):
        if self._device_id != value:
            self._device_id = value
            self.deviceIdChanged.emit()

    # ----------------------------------

    @Property(int, notify=stateChanged)
    def state(self):
        return int(self._state)

    def setState(self, state: DeviceState):
        if self._state != state:
            self._state = state
            self.stateChanged.emit()
            self.dataUpdated.emit()

    # ----------------------------------

    @Property(float, notify=temperatureChanged)
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        if abs(self._temperature - value) > 0.01:  # Fuzzy compare for floats
            self._temperature = value
            self.temperatureChanged.emit(value)
            self.dataUpdated.emit()

    # ----------------------------------

    @Property(float, notify=humidityChanged)
    def humidity(self):
        return self._humidity

    @humidity.setter
    def humidity(self, value):
        if abs(self._humidity - value) > 0.01:
            self._humidity = value
            self.humidityChanged.emit(value)
            self.dataUpdated.emit()

    # ----------------------------------

    @Property(str, notify=lastSeenChanged)
    def lastSeen(self):
        return self._last_seen

    @lastSeen.setter
    def lastSeen(self, value):
        if self._last_seen != value:
            self._last_seen = value
            self.lastSeenChanged.emit()

    # ======================================
    # Public Methods
    # ======================================

    @Slot(bytes)
    def updateFromJson(self, json_data: bytes):
        """Update device state from JSON payload."""
        try:
            data = json.loads(json_data)

            if "temperature" in data:
                self.temperature = float(data["temperature"])

            if "humidity" in data:
                self.humidity = float(data["humidity"])

            if "state" in data:
                state_val = int(data["state"])
                if 0 <= state_val <= 3:
                    self.setState(DeviceState(state_val))

            from datetime import datetime
            self.lastSeen = datetime.now().isoformat()

        except Exception as e:
            print(f"Error updating device from JSON: {e}")

    @Slot(result=bytes)
    def toJson(self):
        """Convert device state to JSON."""
        data = {
            "deviceId": self._device_id,
            "state": int(self._state),
            "temperature": self._temperature,
            "humidity": self._humidity,
            "lastSeen": self._last_seen
        }
        return json.dumps(data).encode('utf-8')
