from PySide6.QtCore import (
    QAbstractListModel,
    Qt,
    QModelIndex,
    Signal,
    Slot,
    Property
)
from .PNDDevice import PNDDevice
from .DeviceState import DeviceState
from typing import Optional, Dict, List


class PNDDeviceModel(QAbstractListModel):

    # Signals
    countChanged = Signal()
    deviceAdded = Signal(str)
    deviceRemoved = Signal(str)
    deviceUpdated = Signal(str)

    # Roles
    DeviceIdRole = Qt.UserRole + 1
    StateRole = Qt.UserRole + 2
    TemperatureRole = Qt.UserRole + 3
    HumidityRole = Qt.UserRole + 4
    LastSeenRole = Qt.UserRole + 5
    DeviceObjectRole = Qt.UserRole + 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self._devices: List[PNDDevice] = []
        self._device_map: Dict[str, PNDDevice] = {}
        print("=" * 50)
        print("PNDDeviceModel initialized")
        print(f"Initial row count: {self.rowCount()}")
        print("=" * 50)

    # ======================================
    # QAbstractListModel Overrides
    # ======================================

    def rowCount(self, parent=QModelIndex()):
        count = len(self._devices)
        return count

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._devices):
            return None

        device = self._devices[index.row()]

        if role == self.DeviceIdRole:
            return device.deviceId
        elif role == self.StateRole:
            return device.state
        elif role == self.TemperatureRole:
            return device.temperature
        elif role == self.HumidityRole:
            return device.humidity
        elif role == self.LastSeenRole:
            return device.lastSeen
        elif role == self.DeviceObjectRole:
            return device
        elif role == Qt.DisplayRole:
            return f"{device.deviceId} (T: {device.temperature}°C, H: {device.humidity}%)"
        elif role == Qt.UserRole:
            return device.deviceId

        return None

    def roleNames(self):
        return {
            self.DeviceIdRole: b"deviceId",
            self.StateRole: b"state",
            self.TemperatureRole: b"temperature",
            self.HumidityRole: b"humidity",
            self.LastSeenRole: b"lastSeen",
            self.DeviceObjectRole: b"deviceObject"
        }

    # ======================================
    # Properties
    # ======================================

    @Property(int, notify=countChanged)
    def count(self):
        return len(self._devices)

    # ======================================
    # Public Methods
    # ======================================

    @Slot(object)
    def addDevice(self, device: PNDDevice):
        """Add a device to the model."""
        if not device or device.deviceId in self._device_map:
            print(f"addDevice: Device {device.deviceId if device else 'None'} already exists or invalid")
            return

        print(f"\n addDevice: Adding device {device.deviceId}")
        print(f"addDevice: Current row count: {self.rowCount()}")

        self.beginInsertRows(QModelIndex(), len(self._devices), len(self._devices))
        self._devices.append(device)
        self._device_map[device.deviceId] = device
        self._connect_device_signals(device)
        self.endInsertRows()

        print(f"addDevice: New row count: {self.rowCount()}")
        print(f"addDevice: Device map size: {len(self._device_map)}")

        self.countChanged.emit()
        self.deviceAdded.emit(device.deviceId)

        # DEBUG: Print all devices
        self.debug_print_devices()

        # Force a data change notification
        topLeft = self.createIndex(0, 0)
        bottomRight = self.createIndex(self.rowCount() - 1, 0)
        self.dataChanged.emit(topLeft, bottomRight)

    @Slot(str)
    def addDeviceById(self, device_id: str):
        """Create and add a device by ID."""
        print(f"\n addDeviceById: Adding device {device_id}")

        if device_id in self._device_map:
            print(f"addDeviceById: Device {device_id} already exists")
            return

        device = PNDDevice(device_id, self)
        self.addDevice(device)

        # Verify it was added
        if device_id in self._device_map:
            print(f"addDeviceById: Device {device_id} successfully added, new count: {self.rowCount()}")
        else:
            print(f"addDeviceById: ERROR - Device {device_id} not found after add!")

    @Slot(str)
    def removeDevice(self, device_id: str):
        """Remove a device from the model."""
        print(f"\nremoveDevice: Removing device {device_id}")

        if device_id not in self._device_map:
            print(f"removeDevice: Device {device_id} not found")
            return

        device = self._device_map[device_id]
        index = self._devices.index(device)

        print(f"removeDevice: Found at index {index}")

        self.beginRemoveRows(QModelIndex(), index, index)
        self._devices.pop(index)
        del self._device_map[device_id]
        self._disconnect_device_signals(device)
        device.deleteLater()
        self.endRemoveRows()

        print(f"removeDevice: New row count: {self.rowCount()}")

        self.debug_print_devices()
        self.countChanged.emit()
        self.deviceRemoved.emit(device_id)

    @Slot(str, result="QObject*")
    def getDevice(self, device_id: str):
        return self._device_map.get(device_id)

    @Slot(int, result="QObject*")   # Add this
    def getDeviceByIndex(self, index: int):
        if 0 <= index < len(self._devices):
            return self._devices[index]
        return None

    @Slot()
    def clear(self):
        """Remove all devices."""
        if not self._devices:
            return

        print(f"\nclear: Removing all {len(self._devices)} devices")

        self.beginResetModel()

        for device in self._devices:
            self._disconnect_device_signals(device)
            device.deleteLater()

        self._devices.clear()
        self._device_map.clear()

        self.endResetModel()

        print(f"clear: Model cleared, count: {self.rowCount()}")
        self.debug_print_devices()
        self.countChanged.emit()

    @Slot(str, result=bool)
    def contains(self, device_id: str) -> bool:
        """Check if device exists."""
        return device_id in self._device_map

    @Slot(str, result=int)
    def indexOf(self, device_id: str) -> int:
        """Get index of device by ID."""
        device = self._device_map.get(device_id)
        if device:
            return self._devices.index(device)
        return -1

    # ======================================
    # Update Methods
    # ======================================

    @Slot(str, int)
    def updateDeviceState(self, device_id: str, state: int):
        """Update device connection state."""
        device = self.getDevice(device_id)
        if device:
            device.setState(DeviceState(state))

    @Slot(str, float, float)
    def updateDeviceSensors(self, device_id: str, temperature: float, humidity: float):
        """Update device sensor readings."""
        device = self.getDevice(device_id)
        if device:
            device.temperature = temperature
            device.humidity = humidity

    @Slot(str, bytes)
    def updateDeviceFromJson(self, device_id: str, json_data: bytes):
        """Update device from JSON data."""
        device = self.getDevice(device_id)
        if device:
            device.updateFromJson(json_data)

    # ======================================
    # Debug Methods
    # ======================================

    @Slot()
    def debug_print_devices(self):
        """Print all devices in the model for debugging."""
        print("\n" + "=" * 60)
        print(f"DEBUG: Model has {self.rowCount()} devices:")
        if self.rowCount() == 0:
            print("  (no devices)")
        else:
            for i, device in enumerate(self._devices):
                state_str = {
                    0: "DISCONNECTED",
                    1: "CONNECTING",
                    2: "CONNECTED",
                    3: "ERROR"
                }.get(device.state, "UNKNOWN")

                print(f"  [{i}] {device.deviceId}")
                print(f"       State: {state_str} ({device.state})")
                print(f"       Temp: {device.temperature}°C, Hum: {device.humidity}%")
                print(f"       LastSeen: {device.lastSeen}")
        print("=" * 60 + "\n")

        # Force flush
        import sys
        sys.stdout.flush()

    # ======================================
    # Private Methods
    # ======================================

    def _connect_device_signals(self, device: PNDDevice):
        """Connect device change signals."""
        device.stateChanged.connect(self._on_device_data_changed)
        device.temperatureChanged.connect(self._on_device_data_changed)
        device.humidityChanged.connect(self._on_device_data_changed)
        device.lastSeenChanged.connect(self._on_device_data_changed)
        device.dataUpdated.connect(self._on_device_data_changed)

    def _disconnect_device_signals(self, device: PNDDevice):
        """Disconnect device change signals."""
        try:
            device.stateChanged.disconnect(self._on_device_data_changed)
            device.temperatureChanged.disconnect(self._on_device_data_changed)
            device.humidityChanged.disconnect(self._on_device_data_changed)
            device.lastSeenChanged.disconnect(self._on_device_data_changed)
            device.dataUpdated.disconnect(self._on_device_data_changed)
        except:
            pass  # Ignore disconnection errors

    def _on_device_data_changed(self):
        """Handle device data changes - update model."""
        device = self.sender()
        if device and device.deviceId in self._device_map:
            try:
                index = self._devices.index(device)
                if index >= 0:
                    model_index = self.createIndex(index, 0)
                    self.dataChanged.emit(model_index, model_index)
                    self.deviceUpdated.emit(device.deviceId)
                    print(f"Device {device.deviceId} data changed, view updated at index {index}")

                    # Debug current state
                    state_str = {
                        0: "DISCONNECTED",
                        1: "CONNECTING",
                        2: "CONNECTED",
                        3: "ERROR"
                    }.get(device.state, "UNKNOWN")
                    print(f"   New state: {state_str}, Temp: {device.temperature}°C, Hum: {device.humidity}%")

                    import sys
                    sys.stdout.flush()
            except ValueError:
                pass  # Device not in list anymore
