from PySide6.QtCore import QObject, Signal, Slot, Property
from DeviceState import PNDDeviceModel
from PNDTopics import PNDTopics
from MQTTClient import MQTTClient


class PNDDeviceConfigurator(QObject):

    deviceDiscovered = Signal(str)
    deviceConnected = Signal(str)
    deviceDisconnected = Signal(str)
    errorOccurred = Signal(str)

    def __init__(self, mqtt_client=None, parent=None):
        super().__init__(parent)

        self._mqtt = MQTTClient()
        self._device_model = PNDDeviceModel()

    # ----------------------------------

    @Property(QObject, constant=True)
    def deviceModel(self):
        return self._device_model

    # ----------------------------------
    @Slot(str, bool)
    def setDevicePower(self, device_id: str, power_on: bool):
        """
        Publish a power command to a specific device.

        :param device_id: ID of the device
        :param power_on: True to turn on, False to turn off
        """
        if not self._mqtt:
            self.errorOccurred.emit("MQTT client not initialized")
            return

        # Build topic: pnd/<deviceId>/command/power
        topic = PNDTopics.device_topic(device_id, PNDTopics.POWER)

        # Payload: simple 1/0 as bytes
        payload = b"1" if power_on else b"0"

        # Publish via MQTT
        self._mqtt.publish(topic, payload)

    @Slot()
    def scanForDevices(self):
        """Trigger device discovery via MQTT."""
        pass

    @Slot(str)
    def connectToDevice(self, device_id: str):
        """Mark device as connecting and initiate MQTT communication."""
        pass

    @Slot(str)
    def disconnectDevice(self, device_id: str):
        """Disconnect device."""
        pass

    @Slot(str, dict)
    def configureDevice(self, device_id: str, config: dict):
        """Send configuration payload to device."""
        pass

    # ----------------------------------

    def _handleMqttMessage(self, topic: str, payload: bytes):
        """Parse topic and update device state/sensors."""
        pass
