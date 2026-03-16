from PySide6.QtCore import QObject, Signal, Slot, Property, QTimer, QDateTime
from PySide6.QtCore import Qt
import json
from typing import Optional, Dict, Set

from .DeviceState import DeviceState
from .MQTTClient import MQTTClient
from .PNDDeviceModel import PNDDeviceModel
from .PNDTopics import PNDTopics
from .PNDDevice import PNDDevice


class PNDDeviceConfigurator(QObject):

    # Signals
    deviceDiscovered = Signal(str)
    deviceConnected = Signal(str)
    deviceDisconnected = Signal(str)
    deviceStatusUpdated = Signal(str, dict)
    deviceSensorsUpdated = Signal(str, float, float)
    errorOccurred = Signal(str)
    scanningChanged = Signal()
    discoveredDevicesChanged = Signal()
    brokerConnectionChanged = Signal()  # Renamed to avoid conflict
    brokerDisconnected = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create MQTT client
        self._mqtt = MQTTClient(self)
        self._device_model = PNDDeviceModel(self)

        print("=" * 50)
        print("PNDDeviceConfigurator initialized")
        print(f"Device model created: {self._device_model}")
        print("=" * 50)

        # Timers
        self._scan_timer = QTimer(self)
        self._scan_timer.setSingleShot(True)
        self._scan_timer.timeout.connect(self._on_scan_timeout)

        self._availability_timer = QTimer(self)
        self._availability_timer.setInterval(30000)  # 30 seconds
        self._availability_timer.timeout.connect(self._check_device_availability)

        # State
        self._is_scanning = False
        self._discovered_devices: Set[str] = set()
        self._last_seen: Dict[str, QDateTime] = {}
        self._availability_timeout = 120  # 2 minutes
        self._pending_commands: Dict[str, dict] = {}

        # Connect MQTT signals
        self._mqtt.connected.connect(self._on_mqtt_connected)
        self._mqtt.disconnected.connect(self._on_mqtt_disconnected)
        self._mqtt.errorOccurred.connect(self._on_mqtt_error)
        self._mqtt.messageReceived.connect(self._handle_mqtt_message)

        # Set default broker
        self._mqtt.host = "192.168.8.130"
        self._mqtt.port = 1883

    # ======================================
    # Properties
    # ======================================

    @Property(QObject, constant=True)
    def deviceModel(self):
        return self._device_model

    @Property(bool, notify=scanningChanged)
    def isScanning(self):
        return self._is_scanning

    @Property(int, notify=discoveredDevicesChanged)
    def discoveredDeviceCount(self):
        return len(self._discovered_devices)

    @Property(bool, notify=brokerConnectionChanged)
    def isBrokerConnected(self):
        """Property to check if broker is connected."""
        return self._mqtt.isConnected

    # ======================================
    # MQTT Configuration
    # ======================================

    def setMqttBroker(self, host: str, port: int):
        """Set MQTT broker address."""
        self._mqtt.host = host
        self._mqtt.port = port

    def setMqttCredentials(self, username: str, password: str):
        """Set MQTT credentials."""
        self._mqtt.username = username
        self._mqtt.password = password

    # ======================================
    # Public Slots
    # ======================================

    @Slot()
    def connectToBroker(self):
        """Connect to MQTT broker."""
        print("connectToBroker called")
        self._mqtt.connectToBroker()

    @Slot()
    def disconnectFromBroker(self):
        """Disconnect from MQTT broker."""
        print("disconnectFromBroker called")
        self._availability_timer.stop()
        self._mqtt.disconnectFromBroker()

    @Slot(int)
    def scanForDevices(self, timeout_seconds: int = 10):
        """Scan for devices via MQTT discovery."""
        print(f"scanForDevices called with timeout: {timeout_seconds}s")

        if self._is_scanning:
            print("Already scanning, ignoring request")
            return

        self._is_scanning = True
        self._discovered_devices.clear()
        self.scanningChanged.emit()
        self.discoveredDevicesChanged.emit()

        if self._mqtt.isConnected:
            print("MQTT connected, subscribing to discovery topic")
            # Subscribe to discovery topic
            self._mqtt.subscribe(PNDTopics.discovery_topic())

            # Publish discovery request
            request = {
                "command": "discover",
                "timestamp": QDateTime.currentDateTime().toString(Qt.ISODate)
            }
            payload = json.dumps(request).encode('utf-8')
            print(f"Publishing discovery request: {request}")
            self._mqtt.publish(
                PNDTopics.discovery_topic(),
                payload
            )
        else:
            print("MQTT not connected, cannot publish discovery request")

        # Start timeout timer
        print(f"Starting scan timer for {timeout_seconds} seconds")
        self._scan_timer.start(timeout_seconds * 1000)

    @Slot()
    def stopScan(self):
        """Stop scanning for devices."""
        print("stopScan called")
        if self._is_scanning:
            self._scan_timer.stop()
            self._is_scanning = False
            self.scanningChanged.emit()
            print("Scan stopped")

    @Slot(str)
    def connectToDevice(self, device_id: str):
        """Connect to a specific device."""
        print(f"connectToDevice called for device: {device_id}")

        if not self._device_model.contains(device_id):
            print(f"Device {device_id} not in model, adding it")
            self._device_model.addDeviceById(device_id)
        else:
            print(f"Device {device_id} already in model")

        device = self._device_model.getDevice(device_id)
        if device:
            print(f"Device found in model, current state: {device.state}")
            self._update_device_state(device_id, DeviceState.CONNECTING)

            # Subscribe to device topics
            print(f"Subscribing to device topics for {device_id}")
            self._mqtt.subscribe(PNDTopics.device_status_topic(device_id))
            self._mqtt.subscribe(PNDTopics.device_sensors_topic(device_id))
            self._mqtt.subscribe(PNDTopics.device_availability_topic(device_id))
            self._mqtt.subscribe(PNDTopics.device_config_topic(device_id))

            # Request status
            print(f"Requesting status for {device_id}")
            self.requestDeviceStatus(device_id)
        else:
            print(f"ERROR: Device {device_id} not found in model after adding!")

    @Slot(str)
    def disconnectDevice(self, device_id: str):
        """Disconnect from a device."""
        print(f"disconnectDevice called for device: {device_id}")

        device = self._device_model.getDevice(device_id)
        if device:
            print(f"Device found, current state: {device.state}")
            self._update_device_state(device_id, DeviceState.DISCONNECTED)

            # Unsubscribe from device topics
            print(f"Unsubscribing from device topics for {device_id}")
            self._mqtt.unsubscribe(PNDTopics.device_status_topic(device_id))
            self._mqtt.unsubscribe(PNDTopics.device_sensors_topic(device_id))
            self._mqtt.unsubscribe(PNDTopics.device_availability_topic(device_id))
            self._mqtt.unsubscribe(PNDTopics.device_config_topic(device_id))

            # Remove from last seen
            if device_id in self._last_seen:
                del self._last_seen[device_id]
                print(f"Removed {device_id} from last_seen tracking")
        else:
            print(f"Device {device_id} not found in model")

    @Slot(str, bool)
    def setDevicePower(self, device_id: str, power_on: bool):
        """
        Publish a power command to a specific device.
        """
        print(f"setDevicePower called for {device_id}: power_on={power_on}")

        if not self._mqtt.isConnected:
            error_msg = "MQTT client not connected"
            print(f"ERROR: {error_msg}")
            self.errorOccurred.emit(error_msg)
            return

        command = {
            "command": "power",
            "value": power_on,
            "timestamp": QDateTime.currentDateTime().toString(Qt.ISODate)
        }

        topic = PNDTopics.device_command_topic(device_id)
        payload = json.dumps(command).encode('utf-8')
        print(f"Publishing power command to {topic}: {command}")
        self._mqtt.publish(topic, payload)

        # Track pending command
        self._pending_commands[device_id] = {
            "command": "power",
            "timestamp": QDateTime.currentDateTime(),
            "data": {"power_on": power_on}
        }
        print(f"Pending command tracked for {device_id}")

    @Slot(str, dict)
    def configureDevice(self, device_id: str, config: dict):
        """Send configuration to device."""
        print(f"configureDevice called for {device_id}: {config}")

        if not self._mqtt.isConnected:
            error_msg = "MQTT client not connected"
            print(f"ERROR: {error_msg}")
            self.errorOccurred.emit(error_msg)
            return

        command = {
            "command": "configure",
            "config": config,
            "timestamp": QDateTime.currentDateTime().toString(Qt.ISODate)
        }

        topic = PNDTopics.device_command_topic(device_id)
        payload = json.dumps(command).encode('utf-8')
        print(f"Publishing configure command to {topic}: {command}")
        self._mqtt.publish(topic, payload)

    @Slot(str)
    def requestDeviceStatus(self, device_id: str):
        """Request device status."""
        print(f"requestDeviceStatus called for {device_id}")

        if not self._mqtt.isConnected:
            print("MQTT not connected, cannot request status")
            return

        command = {
            "command": "get_status",
            "timestamp": QDateTime.currentDateTime().toString(Qt.ISODate)
        }

        topic = PNDTopics.device_command_topic(device_id)
        payload = json.dumps(command).encode('utf-8')
        print(f"Publishing status request to {topic}: {command}")
        self._mqtt.publish(topic, payload)

    @Slot(str)
    def requestDeviceSensors(self, device_id: str):
        """Request device sensor readings."""
        print(f"requestDeviceSensors called for {device_id}")

        if not self._mqtt.isConnected:
            print("MQTT not connected, cannot request sensors")
            return

        command = {
            "command": "get_sensors",
            "timestamp": QDateTime.currentDateTime().toString(Qt.ISODate)
        }

        topic = PNDTopics.device_command_topic(device_id)
        payload = json.dumps(command).encode('utf-8')
        print(f"Publishing sensors request to {topic}: {command}")
        self._mqtt.publish(topic, payload)

    # ======================================
    # Private Slots
    # ======================================

    def _handle_mqtt_message(self, topic: str, payload: bytes):
        """Handle incoming MQTT messages."""
        print(f"\n--- MQTT Message Received ---")
        print(f"Topic: {topic}")
        print(f"Payload: {payload}")

        is_device_topic, device_id = PNDTopics.is_device_topic(topic)
        print(f"is_device_topic: {is_device_topic}, device_id: {device_id}")

        if is_device_topic and device_id:
            # Update last seen timestamp
            self._last_seen[device_id] = QDateTime.currentDateTime()
            print(f"Updated last_seen for {device_id}")

        if topic == PNDTopics.discovery_topic():
            print("Processing discovery message")
            self._process_discovery_message(payload)

        elif is_device_topic and device_id:
            if topic.endswith(PNDTopics.STATUS):
                print(f"Processing status message for {device_id}")
                self._process_status_message(device_id, payload)
            elif topic.endswith(PNDTopics.SENSORS):
                print(f"Processing sensors message for {device_id}")
                self._process_sensors_message(device_id, payload)
            elif topic.endswith(PNDTopics.ERROR):
                print(f"Processing error message for {device_id}")
                self._process_error_message(device_id, payload)
            elif topic.endswith(PNDTopics.AVAILABILITY):
                print(f"Processing availability message for {device_id}")
                self._process_availability_message(device_id, payload)

    def _on_mqtt_connected(self):
        """Handle MQTT connected event."""
        print("\n*** MQTT Connected ***")

        # Subscribe to global topics
        print("Subscribing to global topics...")
        self._mqtt.subscribe(PNDTopics.discovery_topic())
        self._mqtt.subscribe("plantdoctor/device/+/availability")

        # Start availability timer
        self._availability_timer.start()
        print("Availability timer started")

        # Resubscribe to all active devices
        active_count = 0
        for i in range(self._device_model.rowCount()):
            device = self._device_model.getDeviceByIndex(i)
            if device and device.state != DeviceState.DISCONNECTED:
                active_count += 1
                print(f"Resubscribing to active device: {device.deviceId}")
                self.connectToDevice(device.deviceId)

        print(f"Resubscribed to {active_count} active devices")

        # Emit connection changed signal
        self.brokerConnectionChanged.emit()
        print("brokerConnectionChanged signal emitted")

    def _on_mqtt_disconnected(self):
        """Handle MQTT disconnected event."""
        print("\n*** MQTT Disconnected ***")

        self._availability_timer.stop()
        print("Availability timer stopped")

        # Update all device states to disconnected
        disconnected_count = 0
        for i in range(self._device_model.rowCount()):
            device = self._device_model.getDeviceByIndex(i)
            if device and device.state == DeviceState.CONNECTED:
                disconnected_count += 1
                print(f"Marking device as disconnected: {device.deviceId}")
                self._update_device_state(device.deviceId, DeviceState.DISCONNECTED)

        print(f"Marked {disconnected_count} devices as disconnected")
        self._last_seen.clear()
        print("last_seen cleared")

        # Emit signals
        self.brokerConnectionChanged.emit()
        self.brokerDisconnected.emit()
        print("Signals emitted: brokerConnectionChanged, brokerDisconnected")

    def _on_mqtt_error(self, error: str):
        """Handle MQTT error."""
        print(f"\n*** MQTT Error: {error} ***")
        self.errorOccurred.emit(f"MQTT Error: {error}")

    def _on_scan_timeout(self):
        """Handle scan timeout."""
        print("\n*** Scan timeout ***")
        self.stopScan()

    def _check_device_availability(self):
        """Check if devices are still available."""
        now = QDateTime.currentDateTime()
        print(f"\n--- Checking device availability ---")
        print(f"Tracked devices: {len(self._last_seen)}")
        print(f"Current time: {now.toString()}")

        for device_id, last_seen in list(self._last_seen.items()):
            seconds_since = last_seen.secsTo(now)
            print(f"Device {device_id}: last seen {seconds_since} seconds ago")

            device = self._device_model.getDevice(device_id)
            if not device:
                print(f"Device {device_id} no longer in model, removing from tracking")
                del self._last_seen[device_id]
                continue

            if device.state == DeviceState.CONNECTED:
                if seconds_since > self._availability_timeout:
                    print(f"Device {device_id} not seen for {seconds_since} seconds (> {self._availability_timeout})")
                    print(f"Marking device as disconnected")
                    self._update_device_state(device_id, DeviceState.DISCONNECTED)
                    self.deviceDisconnected.emit(device_id)
                    del self._last_seen[device_id]

    # ======================================
    # Private Methods
    # ======================================

    def _process_discovery_message(self, payload: bytes):
        """Process device discovery message."""
        print("\n--- Processing discovery message ---")
        try:
            data = json.loads(payload)
            print(f"Discovery data: {data}")

            if "device_id" in data:
                device_id = data["device_id"]
                print(f"Found device ID: {device_id}")

                # Check if device already exists
                existing_device = self._device_model.getDevice(device_id)

                if device_id not in self._discovered_devices:
                    print(f"New device discovered: {device_id}")
                    self._discovered_devices.add(device_id)
                    self.discoveredDevicesChanged.emit()

                # Add to model if not already there
                if not self._device_model.contains(device_id):
                    print(f"Adding device {device_id} to model")
                    self._device_model.addDeviceById(device_id)

                    # Verify it was added
                    if self._device_model.contains(device_id):
                        print(f"Device {device_id} successfully added to model")
                        print(f"Model now has {self._device_model.rowCount()} devices")
                    else:
                        print(f"ERROR: Device {device_id} was NOT added to model!")
                else:
                    print(f"Device {device_id} already in model")

                # Always emit discovered signal for new discoveries
                if device_id not in self._discovered_devices or not existing_device:
                    self.deviceDiscovered.emit(device_id)
                    print(f"deviceDiscovered signal emitted for {device_id}")
            else:
                print("No device_id in discovery message")

        except Exception as e:
            print(f"Error processing discovery: {e}")
            import traceback
            traceback.print_exc()

    def _process_status_message(self, device_id: str, payload: bytes):
        """Process device status message."""
        print(f"\n--- Processing status message for {device_id} ---")
        try:
            data = json.loads(payload)
            print(f"Status data: {data}")

            # Update device state
            if "state" in data:
                state_str = data["state"]
                print(f"State string: {state_str}")

                if state_str in ["connected", "on"]:
                    print(f"Device {device_id} is connected")
                    self._update_device_state(device_id, DeviceState.CONNECTED)
                    self.deviceConnected.emit(device_id)
                elif state_str in ["disconnected", "off"]:
                    print(f"Device {device_id} is disconnected")
                    self._update_device_state(device_id, DeviceState.DISCONNECTED)
                    self.deviceDisconnected.emit(device_id)

            self.deviceStatusUpdated.emit(device_id, data)
            print(f"deviceStatusUpdated signal emitted for {device_id}")

        except Exception as e:
            print(f"Error processing status: {e}")
            import traceback
            traceback.print_exc()

    def _process_sensors_message(self, device_id: str, payload: bytes):
        """Process device sensors message."""
        print(f"\n--- Processing sensors message for {device_id} ---")
        try:
            data = json.loads(payload)
            print(f"Sensors data: {data}")

            temperature = float(data.get("temperature", 0.0))
            humidity = float(data.get("humidity", 0.0))
            print(f"Temperature: {temperature}, Humidity: {humidity}")

            device = self._device_model.getDevice(device_id)
            if device:
                print(f"Device found in model, updating sensor values")
                old_temp = device.temperature
                old_hum = device.humidity

                device.temperature = temperature
                device.humidity = humidity

                print(f"Updated: {old_temp}°C -> {temperature}°C, {old_hum}% -> {humidity}%")

                if device.state != DeviceState.CONNECTED:
                    print(f"Device state was {device.state}, updating to CONNECTED")
                    self._update_device_state(device_id, DeviceState.CONNECTED)
                    self.deviceConnected.emit(device_id)
            else:
                print(f"ERROR: Device {device_id} not found in model!")

            self.deviceSensorsUpdated.emit(device_id, temperature, humidity)
            print(f"deviceSensorsUpdated signal emitted for {device_id}")

        except Exception as e:
            print(f"Error processing sensors: {e}")
            import traceback
            traceback.print_exc()

    def _process_error_message(self, device_id: str, payload: bytes):
        """Process device error message."""
        error_msg = payload.decode('utf-8')
        print(f"\n--- Error message from {device_id}: {error_msg} ---")
        self.errorOccurred.emit(f"Device {device_id} error: {error_msg}")

    def _process_availability_message(self, device_id: str, payload: bytes):
        """Process device availability message (including LWT)."""

        availability = payload.decode('utf-8').strip().lower()
        print(f"\n--- Availability message for {device_id}: {availability} ---")

        device = self._device_model.getDevice(device_id)

        if availability == "online":

            print(f"Device {device_id} is online")

            # Add device if missing
            if not device:
                print(f"Device {device_id} not in model yet, adding it")
                self._device_model.addDeviceById(device_id)
                device = self._device_model.getDevice(device_id)

            if device:

                # Subscribe to device topics (CRITICAL FIX)
                print(f"Subscribing to device topics for {device_id}")

                self._mqtt.subscribe(PNDTopics.device_sensors_topic(device_id))
                self._mqtt.subscribe(PNDTopics.device_status_topic(device_id))
                self._mqtt.subscribe(PNDTopics.device_config_topic(device_id))

                print(f"Subscribed to:")
                print(PNDTopics.device_sensors_topic(device_id))
                print(PNDTopics.device_status_topic(device_id))
                print(PNDTopics.device_config_topic(device_id))

                # Update device state
                self._update_device_state(device_id, DeviceState.CONNECTED)

                self.deviceConnected.emit(device_id)

                # Update last seen
                self._last_seen[device_id] = QDateTime.currentDateTime()

                print(f"Added {device_id} to last_seen tracking")

            else:
                print(f"ERROR: Failed to create device {device_id}")

        elif availability == "offline":

            print(f"Device {device_id} went offline")

            if device:
                self._update_device_state(device_id, DeviceState.DISCONNECTED)
                self.deviceDisconnected.emit(device_id)

            if device_id in self._last_seen:
                del self._last_seen[device_id]

    def _update_device_state(self, device_id: str, state: DeviceState):
        """Update device state in model."""
        print(f"\n--- Updating device state for {device_id} to {state} ---")
        device = self._device_model.getDevice(device_id)
        if device:
            old_state = device.state
            device.setState(state)
            print(f"Device state changed from {old_state} to {state}")

            # Verify the update
            current_state = device.state
            print(f"Verified current state: {current_state}")
        else:
            print(f"ERROR: Device {device_id} not found in model!")
