# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Slot, Signal, Property
from FieldDataset import FieldDataset


class FieldDataExplorer(QObject):
    # =======================================================
    # Signals
    # =======================================================
    dataLoaded = Signal(int)
    exportCompleted = Signal(str)

    def __init__(self, dataService=None, parent=None):
        super().__init__(parent)
        self._dataset = FieldDataset()
        self._dataService = None

        if dataService:
            self.setDataService(dataService)

    # =======================================================
    # Properties
    # =======================================================
    def getDataset(self):
        return self._dataset

    dataset = Property(QObject, getDataset, constant=True)

    # =======================================================
    # DataService Setter / Wiring
    # =======================================================
    def setDataService(self, dataService):
        if self._dataService is dataService:
            return

        # Disconnect old
        if self._dataService:
            self._dataService.fieldDataReceived.disconnect(self.loadFieldData)

        self._dataService = dataService

        if self._dataService:
            self._dataService.fieldDataReceived.connect(self.loadFieldData)

    # =======================================================
    # Slots / Public API
    # =======================================================
    @Slot(list)
    def loadFieldData(self, records):
        """
        Accepts records from backend sync and loads into dataset.
        """
        if not records:
            return
        self._dataset.loadRecords(records)
        self.dataLoaded.emit(self._dataset.count)

    @Slot(str)
    def exportData(self, formatType):
        """
        Placeholder export logic.
        """
        fakePath = f"/tmp/field_data_export.{formatType}"
        # TODO: Implement CSV / JSON / Excel export
        self.exportCompleted.emit(fakePath)
