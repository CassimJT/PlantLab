# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Slot, Signal, Property
from .FieldDataset import FieldDataset
from pathlib import Path


class FieldDataExplorer(QObject):
    # =======================================================
    # Signals
    # =======================================================
    dataLoaded = Signal(int)
    exportCompleted = Signal(str)
    exportFailed = Signal(str)
    filterChanged = Signal()

    def __init__(self, dataService=None, parent=None):
        super().__init__(parent)
        self._dataset = FieldDataset()
        self._dataService = None
        self._currentFilter = ""

        if dataService:
            self.setDataService(dataService)

    # =======================================================
    # Properties
    # =======================================================
    @Property(QObject, constant=True)
    def dataset(self):
        return self._dataset

    @Property(str, notify=filterChanged)
    def currentFilter(self):
        return self._currentFilter

    @currentFilter.setter
    def currentFilter(self, value):
        if self._currentFilter != value:
            self._currentFilter = value
            self.filterChanged.emit()
            self.applyFilter()

    # =======================================================
    # DataService Setter / Wiring
    # =======================================================
    def setDataService(self, dataService):
        if self._dataService is dataService:
            return

        # Disconnect old
        if self._dataService:
            try:
                self._dataService.inferencesFetched.disconnect(self.loadFieldData)
            except:
                pass

        self._dataService = dataService

        if self._dataService:
            self._dataService.inferencesFetched.connect(self.loadFieldData)

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
        print(f"Loaded {self._dataset.count} records into FieldDataExplorer")

    @Slot(str)
    def exportData(self, formatType):
        """
        Export data in specified format to PlantLab directory
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if formatType.lower() == "json":
            filename = f"field_data_export_{timestamp}.json"
            result = self._dataset.exportToJson(filename)
            if result and not result.startswith("Error"):
                self.exportCompleted.emit(result)
            else:
                self.exportFailed.emit(result)
        elif formatType.lower() == "csv":
            filename = f"field_data_export_{timestamp}.csv"
            result = self._dataset.exportToCsv(filename)
            if result and not result.startswith("Error"):
                self.exportCompleted.emit(result)
            else:
                self.exportFailed.emit(result)
        else:
            self.exportFailed.emit(f"Unsupported format: {formatType}")

    @Slot(str, result=str)
    def exportToJson(self, filename):
        """Export to JSON file with specific name in PlantLab directory"""
        result = self._dataset.exportToJson(filename)
        if result and not result.startswith("Error"):
            self.exportCompleted.emit(result)
        else:
            self.exportFailed.emit(result)
        return result

    @Slot(str, result=str)
    def exportToCsv(self, filename):
        """Export to CSV file with specific name in PlantLab directory"""
        result = self._dataset.exportToCsv(filename)
        if result and not result.startswith("Error"):
            self.exportCompleted.emit(result)
        else:
            self.exportFailed.emit(result)
        return result

    @Slot(result=int)
    def getRecordCount(self):
        """Get total record count"""
        return self._dataset.count

    @Slot(result=list)
    def getAllRecords(self):
        """Get all records"""
        return self._dataset.getRecords()

    @Slot(result="QVariantList")
    def getUniqueLocations(self):
        """Get unique locations"""
        return self._dataset.getUniqueValues("location")

    @Slot(result="QVariantList")
    def getUniqueDiseases(self):
        """Get unique diseases"""
        return self._dataset.getUniqueValues("diseasname")

    @Slot(result="QVariantList")
    def getUniqueVarieties(self):
        """Get unique varieties"""
        return self._dataset.getUniqueValues("variaty")

    @Slot()
    def applyFilter(self):
        """Apply current filter to the dataset view"""
        if self._currentFilter:
            filtered = self._dataset.filterByValue("diseasname", self._currentFilter)
            print(f"Filter applied: {self._currentFilter} -> {len(filtered)} records")

    @Slot()
    def clearFilter(self):
        """Clear current filter"""
        self.currentFilter = ""
        print("Filter cleared")

    @Slot(result=str)
    def getExportDirectory(self):
        """Get the export directory path"""
        return self._dataset.getExportDirectory()

    @Slot(result=bool)
    def openExportDirectory(self):
        """Open the export directory in file explorer"""
        import subprocess
        import platform

        export_dir = self._dataset.getExportDirectory()

        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", export_dir])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", export_dir])
            else:  # Linux
                subprocess.run(["xdg-open", export_dir])
            return True
        except Exception as e:
            print(f"Error opening directory: {e}")
            return False