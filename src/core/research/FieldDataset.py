# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Slot, Signal, Property, QAbstractListModel, QModelIndex, Qt
from pathlib import Path
import json
import csv
import os


class FieldDataListModel(QAbstractListModel):
    """List model for displaying field data in QML"""

    # Define roles
    LocationRole = Qt.UserRole + 1
    DiseaseNameRole = Qt.UserRole + 2
    ConfidenceRole = Qt.UserRole + 3
    VarietyRole = Qt.UserRole + 4
    TimestampRole = Qt.UserRole + 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self._records = []

    def roleNames(self):
        return {
            self.LocationRole: b"location",
            self.DiseaseNameRole: b"diseaseName",
            self.ConfidenceRole: b"confidence",
            self.VarietyRole: b"variety",
            self.TimestampRole: b"timestamp"
        }

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._records):
            return None

        record = self._records[index.row()]

        if role == self.LocationRole:
            return record.get("location", "")
        elif role == self.DiseaseNameRole:
            return record.get("diseasname", record.get("diseaseName", ""))
        elif role == self.ConfidenceRole:
            return record.get("confidence", 0.0)
        elif role == self.VarietyRole:
            return record.get("variaty", record.get("variety", ""))
        elif role == self.TimestampRole:
            return record.get("timestamp", "")

        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._records)

    @Slot(list)
    def setRecords(self, records):
        self.beginResetModel()
        self._records = records
        self.endResetModel()

    def getRecords(self):
        return self._records


class FieldDataset(QObject):
    # =======================================================
    # Signals
    # =======================================================
    dataChanged = Signal()
    datasetCleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._records = []
        self._listModel = FieldDataListModel(self)
        self._exportDir = Path.home() / "Documents" / "PlantLab"
        self._ensureExportDirectory()

    # =======================================================
    # Properties
    # =======================================================
    @Property(QObject, constant=True)
    def listModel(self):
        return self._listModel

    def getCount(self):
        return len(self._records)

    count = Property(int, getCount, notify=dataChanged)

    @Property(str, constant=True)
    def exportDirectory(self):
        return str(self._exportDir)

    # =======================================================
    # Internal Methods
    # =======================================================
    def _ensureExportDirectory(self):
        """Ensure the export directory exists"""
        try:
            self._exportDir.mkdir(parents=True, exist_ok=True)
            print(f"Export directory ready: {self._exportDir}")
        except Exception as e:
            print(f"Error creating export directory: {e}")

    def _setRecords(self, records: list):
        if self._records == records:
            return
        self._records = records
        self._listModel.setRecords(records)
        self.dataChanged.emit()

    def _clear(self):
        if not self._records:
            return
        self._records = []
        self._listModel.setRecords([])
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
        print(f"Loaded {len(records)} records into dataset")

    @Slot()
    def clearRecords(self):
        """Clear all records"""
        self._clear()

    @Slot(result=list)
    def getRecords(self):
        """Return full dataset"""
        return self._records.copy()

    @Slot(str, result="QVariantList")
    def filterByField(self, fieldName):
        """
        Simple MVP filter:
        Returns list of records where the field exists and is truthy
        """
        filtered = [r for r in self._records if r.get(fieldName)]
        return filtered

    @Slot(str, str, result="QVariantList")
    def filterByValue(self, fieldName, value):
        """
        Filter records by field value
        """
        filtered = [r for r in self._records if r.get(fieldName) == value]
        return filtered

    @Slot(str, result="QVariantList")
    def getUniqueValues(self, fieldName):
        """
        Get unique values for a field
        """
        unique = set()
        for record in self._records:
            val = record.get(fieldName)
            if val:
                unique.add(val)
        return sorted(list(unique))

    @Slot(str, result=str)
    def exportToJson(self, filename=None):
        """
        Export dataset to JSON file in PlantLab directory
        """
        try:
            if filename is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"field_data_export_{timestamp}.json"

            filepath = self._exportDir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._records, f, indent=2, default=str)

            print(f"Exported to JSON: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"Export error: {e}")
            return f"Error: {str(e)}"

    @Slot(str, result=str)
    def exportToCsv(self, filename=None):
        """
        Export dataset to CSV file in PlantLab directory
        """
        try:
            if filename is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"field_data_export_{timestamp}.csv"

            if not self._records:
                return "Error: No data to export"

            # Get all field names from all records
            fieldnames = set()
            for record in self._records:
                fieldnames.update(record.keys())

            filepath = self._exportDir / filename
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                writer.writeheader()
                writer.writerows(self._records)

            print(f"Exported to CSV: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"Export error: {e}")
            return f"Error: {str(e)}"

    @Slot(result=str)
    def getExportDirectory(self):
        """Get the export directory path"""
        return str(self._exportDir)