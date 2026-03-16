# This Python file uses the following encoding: utf-8

from PySide6.QtCore import (
    QObject, Slot, Signal, Property, QTimer
)
import paho.mqtt.client as mqtt
import json
import uuid
from typing import Optional, Dict, Callable


class MQTTClient(QObject):

    # ======================================
    # Signals
    # ======================================

    messageReceived = Signal(str, bytes)   # topic, payload
    connected = Signal()
    disconnected = Signal()
    connectionStateChanged = Signal()
    errorOccurred = Signal(str)

    # Property change signals
    hostChanged = Signal()
    portChanged = Signal()
    clientIdChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # ---- Internal State ----
        self._host = "localhost"
        self._port = 1883
        self._client_id = f"PlantDoctor_{uuid.uuid4().hex[:8]}"
        self._username = ""
        self._password = ""

        self._is_connected = False

        # Underlying transport (paho client)
        self._client: Optional[mqtt.Client] = None
        self._ping_timer: Optional[QTimer] = None
        self._subscriptions: Dict[str, bool] = {}  # topic -> subscribed

        self._setup_client()

    # ======================================
    # Private Setup
    # ======================================

    def _setup_client(self):
        """Initialize the paho MQTT client."""
        if self._client is None:
            self._client = mqtt.Client(
                client_id=self._client_id,
                protocol=mqtt.MQTTv311
            )

            # Set callbacks
            self._client.on_connect = self._on_mqtt_connect
            self._client.on_disconnect = self._on_mqtt_disconnect
            self._client.on_message = self._on_mqtt_message
            self._client.on_subscribe = self._on_mqtt_subscribe

            # Setup ping timer
            self._ping_timer = QTimer(self)
            self._ping_timer.setInterval(30000)  # 30 seconds
            self._ping_timer.timeout.connect(self._on_ping_timeout)

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """Called when MQTT connection is established."""
        if rc == 0:
            self._set_connected(True)

            # Resubscribe to all topics
            for topic in list(self._subscriptions.keys()):
                self._client.subscribe(topic)
        else:
            error_msg = self._get_connect_error(rc)
            self.errorOccurred.emit(f"Connection failed: {error_msg}")

    def _on_mqtt_disconnect(self, client, userdata, rc):
        """Called when MQTT disconnects."""
        self._set_connected(False)

    def _on_mqtt_message(self, client, userdata, message):
        """Called when MQTT message is received."""
        self.messageReceived.emit(message.topic, message.payload)

    def _on_mqtt_subscribe(self, client, userdata, mid, granted_qos):
        """Called when subscription is confirmed."""
        # Make a copy of the items to avoid "dictionary changed size during iteration" error
        for topic, subscribed in list(self._subscriptions.items()):
            if subscribed:
                print(f"Subscribed to: {topic}")

    def _on_ping_timeout(self):
        """Check connection state periodically."""
        if self._client and self._is_connected:
            # Paho handles ping automatically
            if not self._client.is_connected():
                self._set_connected(False)

    def _get_connect_error(self, rc):
        """Convert connection return code to error message."""
        errors = {
            1: "Invalid protocol version",
            2: "Client ID rejected",
            3: "Server unavailable",
            4: "Bad username or password",
            5: "Not authorized"
        }
        return errors.get(rc, f"Unknown error ({rc})")

    # ======================================
    # Internal State Handling
    # ======================================

    def _set_connected(self, state: bool):
        if self._is_connected != state:
            self._is_connected = state
            self.connectionStateChanged.emit()

            if state:
                self._ping_timer.start()
                self.connected.emit()
            else:
                self._ping_timer.stop()
                self.disconnected.emit()

    # ======================================
    # Properties
    # ======================================

    @Property(str, notify=hostChanged)
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        if self._host != value:
            self._host = value
            self.hostChanged.emit()

    # --------------------------------------

    @Property(int, notify=portChanged)
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        if self._port != value:
            self._port = value
            self.portChanged.emit()

    # --------------------------------------

    @Property(str, notify=clientIdChanged)
    def clientId(self):
        return self._client_id

    @clientId.setter
    def clientId(self, value):
        if self._client_id != value:
            self._client_id = value
            if self._client:
                self._client.reinitialise(client_id=value)
            self.clientIdChanged.emit()

    # --------------------------------------

    @Property(str)
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    # --------------------------------------

    @Property(str)
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    # --------------------------------------

    @Property(bool, notify=connectionStateChanged)
    def isConnected(self):
        return self._is_connected

    # ======================================
    # Public API (Slots)
    # ======================================

    @Slot()
    def connectToBroker(self):
        """Establish connection to MQTT broker."""
        self._setup_client()

        if self._is_connected:
            return

        try:
            # Set username/password if provided
            if self._username:
                self._client.username_pw_set(self._username, self._password)

            # Connect to broker
            self._client.connect(self._host, self._port, keepalive=60)

            # Start network loop in background thread
            self._client.loop_start()

        except Exception as e:
            self.errorOccurred.emit(f"Connection error: {str(e)}")

    @Slot()
    def disconnectFromBroker(self):
        """Disconnect from MQTT broker."""
        if self._client and self._is_connected:
            self._client.loop_stop()
            self._client.disconnect()

    @Slot(str, bytes)
    def publish(self, topic, payload, qos=0, retain=False):
        """Publish message to topic."""
        if self._client and self._is_connected:
            self._client.publish(topic, payload, qos=qos, retain=retain)
        else:
            self.errorOccurred.emit("Cannot publish: Not connected to broker")

    @Slot(str)
    def subscribe(self, topic, qos=0):
        """Subscribe to topic."""
        if not self._client or not self._is_connected:
            self.errorOccurred.emit("Cannot subscribe: Not connected to broker")
            return

        if topic in self._subscriptions and self._subscriptions[topic]:
            return  # Already subscribed

        self._client.subscribe(topic, qos=qos)
        self._subscriptions[topic] = True

    @Slot(str)
    def unsubscribe(self, topic):
        """Unsubscribe from topic."""
        if topic in self._subscriptions:
            if self._client and self._is_connected:
                self._client.unsubscribe(topic)
            del self._subscriptions[topic]
