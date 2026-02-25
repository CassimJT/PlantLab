# This Python file uses the following encoding: utf-8

from PySide6.QtCore import (
    QObject,
    Slot,
    Signal,
    Property
)


class MQTTClient(QObject):

    # ======================================
    # Signals
    # ======================================

    messageReceived = Signal(str, bytes)   # topic, payload
    connected = Signal()
    disconnected = Signal()
    connectionStateChanged = Signal()
    errorOccurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # ---- Internal State ----
        self._host = ""
        self._port = 1883
        self._client_id = ""
        self._username = ""
        self._password = ""

        self._is_connected = False

        # Underlying transport (e.g., paho client)
        self._client = None

    # ======================================
    # Properties
    # ======================================

    @Property(str)
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        if self._host != value:
            self._host = value

    # --------------------------------------

    @Property(int)
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if self._port != value:
            self._port = value

    # --------------------------------------

    @Property(str)
    def clientId(self):
        return self._client_id

    @clientId.setter
    def clientId(self, value):
        if self._client_id != value:
            self._client_id = value

    # --------------------------------------

    @Property(bool, notify=connectionStateChanged)
    def isConnected(self):
        return self._is_connected

    # ======================================
    # Internal State Handling
    # ======================================

    def _setConnected(self, state: bool):
        if self._is_connected != state:
            self._is_connected = state
            self.connectionStateChanged.emit()

            if state:
                self.connected.emit()
            else:
                self.disconnected.emit()

    # ======================================
    # Public API (Slots)
    # ======================================

    @Slot()
    def connectToBroker(self):
        """Establish connection to MQTT broker."""
        pass

    @Slot()
    def disconnectFromBroker(self):
        """Disconnect from MQTT broker."""
        pass

    @Slot(str, bytes)
    def publish(self, topic, payload):
        """Publish message to topic."""
        pass

    @Slot(str)
    def subscribe(self, topic):
        """Subscribe to topic."""
        pass
