# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QObject, Slot, Signal, Property, QAbstractListModel, QModelIndex, Qt, QByteArray
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import json
import csv
import os


class InferenceListModel(QAbstractListModel):
    """List model for displaying inferences in QML"""

    # Define roles
    LocationRole = Qt.UserRole + 1
    DiseaseNameRole = Qt.UserRole + 2
    ConfidenceRole = Qt.UserRole + 3
    VarietyRole = Qt.UserRole + 4
    TimestampRole = Qt.UserRole + 5

    def __init__(self, parent=None):
        super().__init__(parent)
        self._inferences = []

    def roleNames(self):
        return {
            self.LocationRole: b"location",
            self.DiseaseNameRole: b"diseaseName",
            self.ConfidenceRole: b"confidence",
            self.VarietyRole: b"variety",
            self.TimestampRole: b"timestamp"
        }

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._inferences):
            return None

        inference = self._inferences[index.row()]

        if role == self.LocationRole:
            return inference.get("location", "")
        elif role == self.DiseaseNameRole:
            return inference.get("diseasname", inference.get("diseaseName", ""))
        elif role == self.ConfidenceRole:
            return inference.get("confidence", 0.0)
        elif role == self.VarietyRole:
            return inference.get("variaty", inference.get("variety", ""))
        elif role == self.TimestampRole:
            return inference.get("timestamp", "")

        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._inferences)

    @Slot(list)
    def setInferences(self, inferences):
        self.beginResetModel()
        self._inferences = inferences
        self.endResetModel()

    def getInferences(self):
        return self._inferences


class StatisticalAnalyzer(QObject):
    # =======================================================
    # Signals
    # =======================================================
    datasetChanged = Signal()
    resultsChanged = Signal()
    analysisStarted = Signal(str)
    analysisCompleted = Signal(str, object)  # Added result parameter
    reportGenerated = Signal(str)
    reportFailed = Signal(str)
    analysisError = Signal(str, str)  # analysis name, error message

    # =======================================================
    # Init
    # =======================================================
    def __init__(self, parent=None):
        super().__init__(parent)
        self._inferences = []
        self._results = {}
        self._listModel = InferenceListModel(self)
        self._exportDir = Path.home() / "Documents" / "PlantLab"
        self._ensureExportDirectory()

    # =======================================================
    # Properties
    # =======================================================
    @Property(QObject, notify=datasetChanged)
    def listModel(self):
        return self._listModel

    @Property(int, notify=resultsChanged)
    def getResultsCount(self):
        return len(self._results)

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

    def _storeResult(self, resultId, value):
        if self._results.get(resultId) == value:
            return
        self._results[resultId] = value
        self.resultsChanged.emit()

    def _getRecords(self):
        """Get records as list of dicts"""
        return self._listModel.getInferences()

    # =======================================================
    # Dataset Management
    # =======================================================
    @Slot(list)
    def loadInferences(self, inferences):
        """
        Load inferences from backend
        """
        self._inferences = inferences
        self._listModel.setInferences(inferences)
        self.datasetChanged.emit()
        print(f"Loaded {len(inferences)} inferences")

    @Slot()
    def clearResults(self):
        if not self._results:
            return
        self._results.clear()
        self.resultsChanged.emit()

    # =======================================================
    # 1. Disease Frequency Analysis
    # =======================================================
    @Slot()
    def computeDiseaseFrequency(self):
        self.analysisStarted.emit("disease_frequency")
        try:
            records = self._getRecords()
            if not records:
                self.analysisError.emit("disease_frequency", "No data available")
                return

            disease_counts = Counter()
            for record in records:
                disease = record.get("diseasname", record.get("diseaseName", "Unknown"))
                disease_counts[disease] += 1

            total = len(records)
            result = {
                "total_records": total,
                "diseases": [
                    {"name": name, "count": count, "percentage": (count/total)*100}
                    for name, count in disease_counts.most_common()
                ]
            }

            self._storeResult("disease_frequency", result)
            self.analysisCompleted.emit("disease_frequency", result)

        except Exception as e:
            self.analysisError.emit("disease_frequency", str(e))

    # =======================================================
    # 2. Variety Susceptibility
    # =======================================================
    @Slot()
    def computeVarietySusceptibility(self):
        self.analysisStarted.emit("variety_susceptibility")
        try:
            records = self._getRecords()
            if not records:
                self.analysisError.emit("variety_susceptibility", "No data available")
                return

            variety_disease_map = defaultdict(lambda: Counter())
            variety_counts = Counter()

            for record in records:
                variety = record.get("variaty", record.get("variety", "Unknown"))
                disease = record.get("diseasname", record.get("diseaseName", "Unknown"))

                variety_disease_map[variety][disease] += 1
                variety_counts[variety] += 1

            result = {
                "varieties": []
            }

            for variety, diseases in variety_disease_map.items():
                total_for_variety = variety_counts[variety]
                susceptible_diseases = [
                    {"name": name, "count": count, "percentage": (count/total_for_variety)*100}
                    for name, count in diseases.most_common()
                ]

                result["varieties"].append({
                    "name": variety,
                    "total_infections": total_for_variety,
                    "susceptible_diseases": susceptible_diseases
                })

            self._storeResult("variety_susceptibility", result)
            self.analysisCompleted.emit("variety_susceptibility", result)

        except Exception as e:
            self.analysisError.emit("variety_susceptibility", str(e))

    # =======================================================
    # 3. Infection Rate Comparison (by variety)
    # =======================================================
    @Slot()
    def computeInfectionRateComparison(self):
        self.analysisStarted.emit("infection_rate_comparison")
        try:
            records = self._getRecords()
            if not records:
                self.analysisError.emit("infection_rate_comparison", "No data available")
                return

            # Group by variety and disease
            variety_infection_rates = defaultdict(lambda: {"total": 0, "diseases": Counter()})

            for record in records:
                variety = record.get("variaty", record.get("variety", "Unknown"))
                disease = record.get("diseasname", record.get("diseaseName", "Unknown"))

                variety_infection_rates[variety]["total"] += 1
                variety_infection_rates[variety]["diseases"][disease] += 1

            result = {
                "varieties": []
            }

            for variety, data in variety_infection_rates.items():
                total = data["total"]
                result["varieties"].append({
                    "name": variety,
                    "total_infections": total,
                    "infection_rate": total,  # Raw count
                    "disease_breakdown": [
                        {"name": name, "count": count, "percentage": (count/total)*100}
                        for name, count in data["diseases"].most_common()
                    ]
                })

            # Sort by infection rate (highest first)
            result["varieties"].sort(key=lambda x: x["total_infections"], reverse=True)

            self._storeResult("infection_rate_comparison", result)
            self.analysisCompleted.emit("infection_rate_comparison", result)

        except Exception as e:
            self.analysisError.emit("infection_rate_comparison", str(e))

    # =======================================================
    # 4. Disease By Region (Geographic Analysis)
    # =======================================================
    @Slot()
    def computeDiseaseByRegion(self):
        self.analysisStarted.emit("disease_by_region")
        try:
            records = self._getRecords()
            if not records:
                self.analysisError.emit("disease_by_region", "No data available")
                return

            region_disease_map = defaultdict(lambda: Counter())
            region_counts = Counter()

            for record in records:
                location = record.get("location", "Unknown")
                disease = record.get("diseasname", record.get("diseaseName", "Unknown"))

                region_disease_map[location][disease] += 1
                region_counts[location] += 1

            result = {
                "regions": []
            }

            for region, diseases in region_disease_map.items():
                total_for_region = region_counts[region]
                result["regions"].append({
                    "name": region,
                    "total_infections": total_for_region,
                    "diseases": [
                        {"name": name, "count": count, "percentage": (count/total_for_region)*100}
                        for name, count in diseases.most_common()
                    ]
                })

            self._storeResult("disease_by_region", result)
            self.analysisCompleted.emit("disease_by_region", result)

        except Exception as e:
            self.analysisError.emit("disease_by_region", str(e))

    # =======================================================
    # 5. Improvement Dataset (For model training)
    # =======================================================
    @Slot()
    def generateImprovementDataset(self):
        self.analysisStarted.emit("improvement_dataset")
        try:
            records = self._getRecords()
            if not records:
                self.analysisError.emit("improvement_dataset", "No data available")
                return

            # Prepare dataset for model improvement
            improvement_data = []
            confidence_distribution = {"0-0.5": 0, "0.5-0.7": 0, "0.7-0.9": 0, "0.9-1.0": 0}

            for record in records:
                confidence = record.get("confidence", 0)

                # Categorize confidence
                if confidence < 0.5:
                    confidence_distribution["0-0.5"] += 1
                elif confidence < 0.7:
                    confidence_distribution["0.5-0.7"] += 1
                elif confidence < 0.9:
                    confidence_distribution["0.7-0.9"] += 1
                else:
                    confidence_distribution["0.9-1.0"] += 1

                improvement_data.append({
                    "disease": record.get("diseasname", record.get("diseaseName", "Unknown")),
                    "confidence": confidence,
                    "location": record.get("location", "Unknown"),
                    "variety": record.get("variaty", record.get("variety", "Unknown")),
                    "timestamp": record.get("timestamp", "")
                })

            result = {
                "total_records": len(records),
                "confidence_distribution": confidence_distribution,
                "low_confidence_records": [r for r in improvement_data if r["confidence"] < 0.7],
                "high_confidence_records": [r for r in improvement_data if r["confidence"] >= 0.9],
                "training_data": improvement_data
            }

            self._storeResult("improvement_dataset", result)
            self.analysisCompleted.emit("improvement_dataset", result)

        except Exception as e:
            self.analysisError.emit("improvement_dataset", str(e))

    # =======================================================
    # Run All Analyses
    # =======================================================
    @Slot()
    def runAllAnalyses(self):
        """
        Run all statistical analyses
        """
        self.computeDiseaseFrequency()
        self.computeVarietySusceptibility()
        self.computeInfectionRateComparison()
        self.computeDiseaseByRegion()
        self.generateImprovementDataset()

    # =======================================================
    # Result Access
    # =======================================================
    @Slot(str, result="QVariant")
    def getResult(self, resultId):
        return self._results.get(resultId)

    @Slot(result="QVariantMap")
    def getAllResults(self):
        return self._results.copy()

    # =======================================================
    # Reporting with Export to ~/Documents/PlantLab
    # =======================================================
    @Slot(str)
    def exportAnalysisReport(self, formatType):
        """
        Export analysis report to ~/Documents/PlantLab directory
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if formatType.lower() == "json":
                filename = f"analysis_report_{timestamp}.json"
                filepath = self._exportDir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self._results, f, indent=2, default=str)

            elif formatType.lower() == "csv":
                filename = f"analysis_report_{timestamp}.csv"
                filepath = self._exportDir / filename
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Analysis Type", "Result Summary"])
                    for key, value in self._results.items():
                        # Convert result to string summary
                        if isinstance(value, dict):
                            summary = str(value)[:200] + "..." if len(str(value)) > 200 else str(value)
                        else:
                            summary = str(value)[:200]
                        writer.writerow([key, summary])

            elif formatType.lower() == "txt":
                filename = f"analysis_report_{timestamp}.txt"
                filepath = self._exportDir / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("PLANT DOCTOR - STATISTICAL ANALYSIS REPORT\n")
                    f.write("=" * 50 + "\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total Records: {len(self._inferences)}\n")
                    f.write("=" * 50 + "\n\n")

                    for key, value in self._results.items():
                        f.write(f"\n{key.upper()}\n")
                        f.write("-" * 30 + "\n")
                        f.write(json.dumps(value, indent=2, default=str))
                        f.write("\n\n")
            else:
                self.reportFailed.emit(f"Unsupported format: {formatType}")
                return

            self.reportGenerated.emit(str(filepath))
            print(f"Report exported to: {filepath}")

        except Exception as e:
            error_msg = f"Export failed: {str(e)}"
            print(error_msg)
            self.reportFailed.emit(error_msg)

    @Slot(result=str)
    def getExportDirectory(self):
        """Get the export directory path"""
        return str(self._exportDir)

    @Slot(result=bool)
    def openExportDirectory(self):
        """Open the export directory in file explorer"""
        import subprocess
        import platform

        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", str(self._exportDir)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", str(self._exportDir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(self._exportDir)])
            return True
        except Exception as e:
            print(f"Error opening directory: {e}")
            return False