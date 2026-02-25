# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Slot, Signal, Property


class FieldDataset(QObject):
    # =======================================================
    # Signals
    # =======================================================
    dataChanged = Signal()
    datasetCleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._records = []

    # =======================================================
    # Properties
    # =======================================================
    def getCount(self):
        return len(self._records)

    count = Property(int, getCount, notify=dataChanged)

    # =======================================================
    # Internal State Methods
    # =======================================================
    def _setRecords(self, records: list):
        if self._records == records:
            return
        self._records = records
        self.dataChanged.emit()

    def _clear(self):
        if not self._records:
            return
        self._records = []
        self.datasetCleared.emit()
        self.dataChanged.emit()

    # =======================================================
    # Slots
    # =======================================================
    @Slot(list)
    def loadRecords(self, records):
        """Load raw records (list of dicts)"""
        if not records:
            return
        self._setRecords(records)

    @Slot()
    def clearRecords(self):
        """Clear all records"""
        self._clear()

    @Slot(result=list)
    def getRecords(self):
        """Return full dataset"""
        return self._records.copy()  # Prevent external mutation

    @Slot(str, result="QVariantList")
    def filterByField(self, fieldName):
        """
        Simple MVP filter:
        Returns list of records where the field exists and is truthy
        """
        filtered = [r for r in self._records if r.get(fieldName)]
        return filtered
