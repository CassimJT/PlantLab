# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Slot, Signal, Property, QAbstractListModel, QModelIndex, Qt
from pathlib import Path
from datetime import datetime
import json
import csv
import os
import traceback


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
            print(f"[FieldDataset] Export directory ready: {self._exportDir}")
            print(f"[FieldDataset] Export directory exists: {self._exportDir.exists()}")
            print(f"[FieldDataset] Export directory is writable: {os.access(str(self._exportDir), os.W_OK)}")
        except Exception as e:
            print(f"[FieldDataset] ERROR creating export directory: {e}")
            traceback.print_exc()

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
        print(f"[FieldDataset] loadRecords called with {len(records) if records else 0} records")
        if not records:
            print("[FieldDataset] No records to load")
            return
        self._setRecords(records)
        print(f"[FieldDataset] Loaded {len(records)} records into dataset")

    @Slot()
    def clearRecords(self):
        """Clear all records"""
        print("[FieldDataset] clearRecords called")
        self._clear()

    @Slot(result=list)
    def getRecords(self):
        """Return full dataset"""
        print(f"[FieldDataset] getRecords returning {len(self._records)} records")
        return self._records.copy()

    @Slot(str, result="QVariantList")
    def filterByField(self, fieldName):
        """
        Simple MVP filter:
        Returns list of records where the field exists and is truthy
        """
        print(f"[FieldDataset] filterByField called with fieldName: {fieldName}")
        filtered = [r for r in self._records if r.get(fieldName)]
        print(f"[FieldDataset] filterByField found {len(filtered)} records")
        return filtered

    @Slot(str, str, result="QVariantList")
    def filterByValue(self, fieldName, value):
        """
        Filter records by field value
        """
        print(f"[FieldDataset] filterByValue called with fieldName: {fieldName}, value: {value}")
        print(f"[FieldDataset] Total records before filter: {len(self._records)}")
        filtered = [r for r in self._records if r.get(fieldName) == value]
        print(f"[FieldDataset] filterByValue found {len(filtered)} records")
        if len(filtered) > 0:
            print(f"[FieldDataset] First filtered record sample: {filtered[0]}")
        return filtered

    @Slot(str, result="QVariantList")
    def getUniqueValues(self, fieldName):
        """
        Get unique values for a field
        """
        print(f"[FieldDataset] getUniqueValues called with fieldName: {fieldName}")
        unique = set()
        for record in self._records:
            val = record.get(fieldName)
            if val:
                unique.add(val)
        result = sorted(list(unique))
        print(f"[FieldDataset] getUniqueValues found {len(result)} unique values: {result[:5]}...")  # Show first 5
        return result

    @Slot(result=str)
    def exportToJson(self):
        """
        Export dataset to JSON file in PlantLab directory
        """
        print(f"[FieldDataset] exportToJson called")
        print(f"[FieldDataset] Total records to export: {len(self._records)}")

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"field_data_export_{timestamp}.json"
            print(f"[FieldDataset] Generated filename: {filename}")

            filepath = self._exportDir / filename
            print(f"[FieldDataset] Full export path: {filepath}")

            # Ensure directory still exists
            self._ensureExportDirectory()

            # Write JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._records, f, indent=2, default=str)

            # Verify file was created
            if filepath.exists():
                file_size = filepath.stat().st_size
                print(f"[FieldDataset] JSON export successful! File size: {file_size} bytes")
                print(f"[FieldDataset] File path: {filepath}")
                return str(filepath)
            else:
                print(f"[FieldDataset] ERROR: File was not created at {filepath}")
                return f"Error: File not created at {filepath}"

        except Exception as e:
            print(f"[FieldDataset] EXPORT ERROR: {e}")
            traceback.print_exc()
            return f"Error: {str(e)}"

    @Slot(result=str)
    def exportToCsv(self):
        """
        Export dataset to CSV file in PlantLab directory
        """
        print(f"[FieldDataset] exportToCsv called")
        print(f"[FieldDataset] Total records to export: {len(self._records)}")

        try:
            if not self._records:
                print("[FieldDataset] ERROR: No data to export")
                return "Error: No data to export"

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"field_data_export_{timestamp}.csv"
            print(f"[FieldDataset] Generated filename: {filename}")

            # Get all field names from all records
            fieldnames = set()
            for record in self._records:
                fieldnames.update(record.keys())

            print(f"[FieldDataset] CSV fieldnames: {sorted(fieldnames)}")

            filepath = self._exportDir / filename
            print(f"[FieldDataset] Full export path: {filepath}")

            # Ensure directory still exists
            self._ensureExportDirectory()

            # Write CSV file
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                writer.writeheader()
                writer.writerows(self._records)

            # Verify file was created
            if filepath.exists():
                file_size = filepath.stat().st_size
                print(f"[FieldDataset] CSV export successful! File size: {file_size} bytes")
                print(f"[FieldDataset] File path: {filepath}")
                return str(filepath)
            else:
                print(f"[FieldDataset] ERROR: File was not created at {filepath}")
                return f"Error: File not created at {filepath}"

        except Exception as e:
            print(f"[FieldDataset] EXPORT ERROR: {e}")
            traceback.print_exc()
            return f"Error: {str(e)}"

    @Slot(result=str)
    def getExportDirectory(self):
        """Get the export directory path"""
        print(f"[FieldDataset] getExportDirectory returning: {self._exportDir}")
        return str(self._exportDir)