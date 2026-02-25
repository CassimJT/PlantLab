from PySide6.QtCore import (
    QAbstractListModel,
    Qt,
    QModelIndex
)


class PNDDeviceModel(QAbstractListModel):

    DeviceIdRole = Qt.UserRole + 1
    StateRole = Qt.UserRole + 2
    TemperatureRole = Qt.UserRole + 3
    HumidityRole = Qt.UserRole + 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self._devices = []

    # ----------------------------------

    def rowCount(self, parent=QModelIndex()):
        return len(self._devices)

    # ----------------------------------

    def data(self, index, role):
        if not index.isValid():
            return None

        device = self._devices[index.row()]

        if role == self.DeviceIdRole:
            return device.deviceId
        if role == self.StateRole:
            return device.state
        if role == self.TemperatureRole:
            return device.temperature
        if role == self.HumidityRole:
            return device.humidity

        return None

    # ----------------------------------

    def roleNames(self):
        return {
            self.DeviceIdRole: b"deviceId",
            self.StateRole: b"state",
            self.TemperatureRole: b"temperature",
            self.HumidityRole: b"humidity",
        }

    # ----------------------------------

    def addDevice(self, device):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._devices.append(device)
        self.endInsertRows()

    def getDevice(self, device_id: str):
        for d in self._devices:
            if d.deviceId == device_id:
                return d
        return None
