# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QObject, Slot, Signal, Property, QAbstractListModel, QModelIndex, Qt
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import json
import csv
import os


# =======================================================
# PLOT MODELS FOR QML VISUALIZATION
# =======================================================

class BasePlotModel(QAbstractListModel):
    """Base class for all plot models"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def setDataList(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def getDataList(self):
        return self._data


class BarDataModel(BasePlotModel):
    RowRole = Qt.UserRole + 1
    ColumnRole = Qt.UserRole + 2
    ValueRole = Qt.UserRole + 3

    def roleNames(self):
        return {
            self.RowRole: b"row",
            self.ColumnRole: b"column",
            self.ValueRole: b"value",
        }

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self._data):
            return None

        item = self._data[index.row()]
        if role == self.RowRole:
            return item.get("row", "")
        if role == self.ColumnRole:
            return item.get("column", "")
        if role == self.ValueRole or role == Qt.DisplayRole:
            return item.get("value", 0)
        return None


class ScatterDataModel(BasePlotModel):
    """Model for scatter plot data - exposes x, y, z roles"""

    XRole = Qt.UserRole + 1
    YRole = Qt.UserRole + 2
    ZRole = Qt.UserRole + 3
    LabelRole = Qt.UserRole + 4

    def roleNames(self):
        return {
            self.XRole: b"x",
            self.YRole: b"y",
            self.ZRole: b"z",
            self.LabelRole: b"label",
        }

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self._data):
            return None

        item = self._data[index.row()]
        if role == self.XRole:
            return item.get("x", 0)
        if role == self.YRole:
            return item.get("y", 0)
        if role == self.ZRole:
            return item.get("z", 0)
        if role == self.LabelRole:
            return item.get("label", "")
        return None


class SurfaceDataModel(BasePlotModel):
    """Model for surface/3D chart data - exposes row, column, value roles"""

    RowRole = Qt.UserRole + 1
    ColumnRole = Qt.UserRole + 2
    ValueRole = Qt.UserRole + 3

    def roleNames(self):
        return {
            self.RowRole: b"row",
            self.ColumnRole: b"column",
            self.ValueRole: b"value",
        }

    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self._data):
            return None

        item = self._data[index.row()]
        if role == self.RowRole:
            return item.get("row", "")
        if role == self.ColumnRole:
            return item.get("column", "")
        if role == self.ValueRole:
            return item.get("value", 0)
        return None


# =======================================================
# CHART MAPPER ADAPTER LAYER - For 2D Charts
# =======================================================

class ChartMapper(QObject):
    """
    Adapter class that converts model data into formats suitable for 2D charts.
    Acts as a bridge between your data models and Qt Charts components.
    """

    # Signals for chart data changes
    barDataChanged = Signal()
    lineDataChanged = Signal()
    scatterDataChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._barCategories = []
        self._barValues = []
        self._barSeriesName = ""

        self._lineSeries = []
        self._lineCategories = []

        self._scatterPoints = []

    # =======================================================
    # Properties for Bar Chart
    # =======================================================
    @Property("QVariantList", notify=barDataChanged)
    def barCategories(self):
        """Returns categories for bar chart X-axis"""
        return self._barCategories

    @Property("QVariantList", notify=barDataChanged)
    def barValues(self):
        """Returns values for bar chart"""
        return self._barValues

    @Property(str, notify=barDataChanged)
    def barSeriesName(self):
        """Returns the series name for the bar chart"""
        return self._barSeriesName

    @Property(int, notify=barDataChanged)
    def barCount(self):
        """Returns number of bars"""
        return len(self._barValues)

    # =======================================================
    # Properties for Line Chart
    # =======================================================
    @Property("QVariantList", notify=lineDataChanged)
    def lineSeries(self):
        """Returns list of line series: each with 'name' and 'points'"""
        return self._lineSeries

    @Property("QVariantList", notify=lineDataChanged)
    def lineCategories(self):
        """Returns X-axis categories for line chart"""
        return self._lineCategories

    @Property(int, notify=lineDataChanged)
    def lineSeriesCount(self):
        """Returns number of line series"""
        return len(self._lineSeries)

    # =======================================================
    # Properties for Scatter Chart
    # =======================================================
    @Property("QVariantList", notify=scatterDataChanged)
    def scatterPoints(self):
        """Returns list of (x, y) points for scatter chart"""
        return self._scatterPoints

    @Property(int, notify=scatterDataChanged)
    def scatterCount(self):
        """Returns number of scatter points"""
        return len(self._scatterPoints)

    # =======================================================
    # Public Methods
    # =======================================================
    @Slot("QVariantMap")
    def updateFromAnalysisResult(self, result):
        """
        Main method to update charts from analysis result.
        Call this after any analysis completes.
        """
        if not result:
            return

        analysis_type = result.get("analysis_type", "")
        print(f"[ChartMapper] Updating from analysis: {analysis_type}")

        if analysis_type == "Disease Frequency":
            # Update bar chart
            diseases = result.get("diseases", [])
            self._barCategories = [d["name"] for d in diseases]
            self._barValues = [d["count"] for d in diseases]
            self._barSeriesName = "Disease Frequency"
            self.barDataChanged.emit()
            print(f"[ChartMapper] Bar chart updated: {len(self._barCategories)} diseases")

        elif analysis_type == "Infection Rate Comparison":
            # Update bar chart with variety data
            varieties = result.get("varieties", [])
            self._barCategories = [v["name"] for v in varieties]
            self._barValues = [v["total_infections"] for v in varieties]
            self._barSeriesName = "Infection Rate by Variety"
            self.barDataChanged.emit()
            print(f"[ChartMapper] Bar chart updated: {len(self._barCategories)} varieties")

        elif analysis_type == "Variety Susceptibility":
            # Update scatter chart
            varieties = result.get("varieties", [])
            points = []
            for variety in varieties:
                for disease in variety.get("susceptible_diseases", []):
                    points.append({
                        "x": float(variety.get("total_infections", 0)),
                        "y": float(disease.get("percentage", 0))
                    })
            self._scatterPoints = points
            self.scatterDataChanged.emit()
            print(f"[ChartMapper] Scatter chart updated: {len(points)} points")

        elif analysis_type == "Disease By Region":
            lines_data = result.get("lines_data", [])
            self._lineSeries = []
            for line in lines_data:
                points = []
                for p in line.get("points", []):
                    points.append({"x": p.get("x", 0), "y": p.get("y", 0)})
                self._lineSeries.append({
                    "name": line.get("name", ""),
                    "points": points
                })
            # Add this line - set line categories
            self._lineCategories = result.get("regions", [])
            self.lineDataChanged.emit()
            print(f"[ChartMapper] Line chart updated: {len(self._lineSeries)} disease lines")

    @Slot()
    def clear(self):
        """Clear all chart data"""
        self._barCategories = []
        self._barValues = []
        self._lineSeries = []
        self._lineCategories = []
        self._scatterPoints = []
        self.barDataChanged.emit()
        self.lineDataChanged.emit()
        self.scatterDataChanged.emit()
        print("[ChartMapper] All chart data cleared")


class PlotDataModel(QObject):
    """
    PlotModel - Modified by StatisticalAnalyzer for 3D plotting
    Provides formatted data for bar, surface, and scatter charts
    Now integrated with ChartMapper for 2D chart support
    """

    # =======================================================
    # Signals
    # =======================================================
    plotDataChanged = Signal()
    chartTypeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._currentChartType = "bar"  # bar, surface, scatter
        self._plotData = {
            "bar": {},
            "surface": {},
            "scatter": {}
        }

        # Initialize the detailed models for QML (3D Charts)
        self._barModel = BarDataModel(self)
        self._scatterModel = ScatterDataModel(self)
        self._surfaceModel = SurfaceDataModel(self)

        # Initialize ChartMapper for 2D Charts
        self._chartMapper = ChartMapper(self)

    # =======================================================
    # Properties
    # =======================================================
    @Property(str, notify=chartTypeChanged)
    def chartType(self):
        return self._currentChartType

    @chartType.setter
    def chartType(self, value):
        if self._currentChartType != value:
            self._currentChartType = value
            self.chartTypeChanged.emit()

    @Property("QVariantMap", notify=plotDataChanged)
    def barData(self):
        return self._plotData.get("bar", {})

    @Property("QVariantMap", notify=plotDataChanged)
    def surfaceData(self):
        return self._plotData.get("surface", {})

    @Property("QVariantMap", notify=plotDataChanged)
    def scatterData(self):
        return self._plotData.get("scatter", {})

    @Property("QVariantMap", notify=plotDataChanged)
    def lineData(self):
        return self._plotData.get("line", {})

    # Expose the detailed models to QML (for 3D charts)
    @Property(QObject, constant=True)
    def barModel(self):
        return self._barModel

    @Property(QObject, constant=True)
    def scatterModel(self):
        return self._scatterModel

    @Property(QObject, constant=True)
    def surfaceModel(self):
        return self._surfaceModel

    # Expose ChartMapper to QML (for 2D charts)
    @Property(QObject, constant=True)
    def chartMapper(self):
        return self._chartMapper

    # =======================================================
    # Public Methods
    # =======================================================
    @Slot(str, "QVariant")
    def setPlotData(self, chartType, data):
        """Set plot data for a specific chart type"""
        if chartType in self._plotData:
            self._plotData[chartType] = data
            self.plotDataChanged.emit()
            print(f"[PlotModel] Updated {chartType} chart data")

            # Update the corresponding detailed model
            self._updateDetailedModel(chartType, data)

    @Slot(str, result="QVariant")
    def getPlotData(self, chartType):
        """Get plot data for a specific chart type"""
        return self._plotData.get(chartType, {})

    @Slot()
    def clear(self):
        """Clear all plot data"""
        self._plotData = {
            "bar": {},
            "surface": {},
            "scatter": {}
        }
        self._barModel.setDataList([])
        self._scatterModel.setDataList([])
        self._surfaceModel.setDataList([])
        self._chartMapper.clear()
        self.plotDataChanged.emit()

    # =======================================================
    # Internal Methods
    # =======================================================
    def _updateDetailedModel(self, chartType, data):
        """Update the detailed model based on chart type"""
        if chartType == "bar" and "categories" in data and "values" in data:
            # Convert to row/column format for bar model
            rows = []
            for i, (category, value) in enumerate(zip(data["categories"], data["values"])):
                rows.append({
                    "row": category,
                    "column": "Value",
                    "value": value
                })
            self._barModel.setDataList(rows)
            print(f"[PlotModel] Updated bar model with {len(rows)} items")

            # Also update ChartMapper for 2D bar charts
            # This creates a result dict that ChartMapper understands
            bar_result = {
                "analysis_type": "Disease Frequency",
                "diseases": [{"name": c, "count": v} for c, v in zip(data["categories"], data["values"])]
            }
            self._chartMapper.updateFromAnalysisResult(bar_result)

        elif chartType == "scatter" and "points" in data:
            # Convert points to scatter model format
            points_data = []
            for point in data["points"]:
                points_data.append({
                    "x": point.get("x", 0),
                    "y": point.get("y", 0),
                    "z": point.get("z", point.get("count", 1)),
                    "label": point.get("label", "")
                })
            self._scatterModel.setDataList(points_data)
            print(f"[PlotModel] Updated scatter model with {len(points_data)} points")

            # Also update ChartMapper for 2D scatter charts
            scatter_result = {
                "analysis_type": "Variety Susceptibility",
                "varieties": data.get("varieties_for_mapper", [])
            }
            self._chartMapper.updateFromAnalysisResult(scatter_result)

        elif chartType == "surface":
            if "surfaceData" in data:
                formatted_data = []
                for item in data["surfaceData"]:
                    formatted_data.append({
                        "row": float(item.get("row", 0)),
                        "column": float(item.get("column", 0)),
                        "value": float(item.get("value", 0))
                    })
                self._surfaceModel.setDataList(formatted_data)
                print(f"[PlotModel] Updated surface model with {len(formatted_data)} points")
            else:
                print(f"[PlotModel] Warning: No surfaceData found")


class StatisticalAnalyzer(QObject):
    """
    StatisticalAnalyzer - Runs different statistics
    Reads from FieldDataset (single source of truth)
    Updates PlotDataModel with plotable data for visualization
    """

    # =======================================================
    # Signals
    # =======================================================
    datasetChanged = Signal()
    resultsChanged = Signal()
    analysisStarted = Signal(str)
    analysisCompleted = Signal(str, object)
    reportGenerated = Signal(str)
    reportFailed = Signal(str)
    analysisError = Signal(str, str)

    # =======================================================
    # Init
    # =======================================================
    def __init__(self, fieldDataset=None, plotModel=None, parent=None):
        super().__init__(parent)
        self._fieldDataset = fieldDataset  # Single source of truth
        self._plotModel = plotModel        # Plot model for visualization
        self._results = {}
        self._exportDir = Path.home() / "Documents" / "PlantLab"
        self._ensureExportDirectory()

        # Connect to dataset changes
        if self._fieldDataset:
            self._fieldDataset.dataChanged.connect(self._onDatasetChanged)

    # =======================================================
    # Properties
    # =======================================================
    @Property(int, notify=resultsChanged)
    def resultsCount(self):
        return len(self._results)

    @Property(str, constant=True)
    def exportDirectory(self):
        return str(self._exportDir)

    @Property(QObject, constant=True)
    def plotModel(self):
        return self._plotModel

    # =======================================================
    # Internal Methods
    # =======================================================
    def _ensureExportDirectory(self):
        """Ensure the export directory exists"""
        try:
            self._exportDir.mkdir(parents=True, exist_ok=True)
            print(f"[StatisticalAnalyzer] Export directory ready: {self._exportDir}")
        except Exception as e:
            print(f"[StatisticalAnalyzer] Error creating export directory: {e}")

    def _getRecords(self):
        """Get records from single source of truth (FieldDataset)"""
        if self._fieldDataset:
            return self._fieldDataset.getRecords()
        return []

    def _storeResult(self, resultId, value):
        """Store analysis result"""
        self._results[resultId] = value
        self.resultsChanged.emit()

    def _onDatasetChanged(self):
        """React to changes in source of truth"""
        self.datasetChanged.emit()
        print("[StatisticalAnalyzer] Source data changed")

    # =======================================================
    # Dataset Management
    # =======================================================
    @Slot()
    def refreshFromSource(self):
        """Refresh all analyses from current source data"""
        print("[StatisticalAnalyzer] Refreshing all analyses from source")
        self.runAllAnalyses()

    @Slot()
    def clearResults(self):
        """Clear all stored results"""
        self._results.clear()
        self.resultsChanged.emit()
        if self._plotModel:
            self._plotModel.clear()

    # =======================================================
    # Analysis Methods (callable from QML)
    # =======================================================
    @Slot(str)
    def runAnalysis(self, analysisName):
        """Main slot called from QML to run an analysis"""
        print(f"[StatisticalAnalyzer] runAnalysis called with: {analysisName}")

        analysis_map = {
            "Disease Frequency": self.computeDiseaseFrequency,
            "Variety Susceptibility": self.computeVarietySusceptibility,
            "Infection Rate Comparison": self.computeInfectionRateComparison,
            "Disease By Region": self.computeDiseaseByRegion
        }

        if analysisName in analysis_map:
            analysis_map[analysisName]()
        else:
            error_msg = f"Unknown analysis: {analysisName}"
            print(f"[StatisticalAnalyzer] {error_msg}")
            self.analysisError.emit(analysisName, error_msg)

    @Slot(str)
    def runSingleAnalysis(self, analysisName):
        """Alternative slot for running a single analysis"""
        self.runAnalysis(analysisName)

    # =======================================================
    # 1. Disease Frequency Analysis -> BAR CHART
    # =======================================================
    @Slot()
    def computeDiseaseFrequency(self):
        """
        Disease Frequency Analysis
        Returns plotable data for Bar Chart
        """
        analysis_name = "Disease Frequency"
        print(f"[StatisticalAnalyzer] Starting {analysis_name}")
        self.analysisStarted.emit(analysis_name)

        try:
            records = self._getRecords()
            if not records:
                self.analysisError.emit(analysis_name, "No data available")
                return

            disease_counts = Counter()
            for record in records:
                disease = record.get("diseasname", "Unknown")
                disease_counts[disease] += 1

            total = len(records)

            # Prepare result
            diseases_list = []
            for name, count in disease_counts.most_common():
                diseases_list.append({
                    "name": name,
                    "count": count,
                    "percentage": round((count / total) * 100, 2)
                })

            result = {
                "analysis_type": analysis_name,
                "total_records": total,
                "diseases": diseases_list
            }

            # Prepare plotable data for Bar Chart (3D)
            if self._plotModel:
                plot_data = {
                    "title": "Disease Frequency Distribution",
                    "xAxis": "Disease",
                    "yAxis": "Frequency",
                    "categories": [d["name"] for d in diseases_list],
                    "values": [d["count"] for d in diseases_list],
                    "percentages": [d["percentage"] for d in diseases_list]
                }
                self._plotModel.setPlotData("bar", plot_data)

                # Also update ChartMapper for 2D charts
                self._plotModel.chartMapper.updateFromAnalysisResult(result)

            self._storeResult("disease_frequency", result)
            self.analysisCompleted.emit(analysis_name, result)
            print(f"[StatisticalAnalyzer] Completed {analysis_name}")

        except Exception as e:
            self.analysisError.emit(analysis_name, str(e))
            print(f"[StatisticalAnalyzer] Error in {analysis_name}: {e}")

    # =======================================================
    # 2. Variety Susceptibility Analysis -> SCATTER PLOT
    # =======================================================
    @Slot()
    def computeVarietySusceptibility(self):
        """
        Variety Susceptibility Analysis
        Returns plotable data for Scatter Plot
        """
        analysis_name = "Variety Susceptibility"
        print(f"[StatisticalAnalyzer] Starting {analysis_name}")
        self.analysisStarted.emit(analysis_name)

        try:
            records = self._getRecords()
            if not records:
                self.analysisError.emit(analysis_name, "No data available")
                return

            variety_disease_map = defaultdict(lambda: Counter())
            variety_counts = Counter()

            for record in records:
                variety = record.get("variaty", "Unknown")
                disease = record.get("diseasname", "Unknown")

                variety_disease_map[variety][disease] += 1
                variety_counts[variety] += 1

            result = {
                "analysis_type": analysis_name,
                "varieties": []
            }

            # Prepare scatter points
            scatter_points = []

            for variety, diseases in variety_disease_map.items():
                total_for_variety = variety_counts[variety]
                susceptible_diseases = []

                for name, count in diseases.most_common():
                    percentage = round((count / total_for_variety) * 100, 2)
                    susceptible_diseases.append({
                        "name": name,
                        "count": count,
                        "percentage": percentage
                    })

                    # Add point for scatter plot
                    scatter_points.append({
                        "x": total_for_variety,
                        "y": percentage,
                        "z": count,
                        "label": f"{variety} - {name}",
                        "disease": name,
                        "variety": variety,
                        "count": count
                    })

                result["varieties"].append({
                    "name": variety,
                    "total_infections": total_for_variety,
                    "susceptible_diseases": susceptible_diseases
                })

            # Prepare plotable data for Scatter Plot (3D)
            if self._plotModel:
                plot_data = {
                    "title": "Variety Susceptibility Analysis",
                    "xAxis": "Total Infections per Variety",
                    "yAxis": "Disease Percentage (%)",
                    "points": scatter_points,
                    "varieties_for_mapper": result["varieties"]
                }
                self._plotModel.setPlotData("scatter", plot_data)

                # Also update ChartMapper for 2D charts
                self._plotModel.chartMapper.updateFromAnalysisResult(result)

            self._storeResult("variety_susceptibility", result)
            self.analysisCompleted.emit(analysis_name, result)
            print(f"[StatisticalAnalyzer] Completed {analysis_name}")

        except Exception as e:
            self.analysisError.emit(analysis_name, str(e))
            print(f"[StatisticalAnalyzer] Error in {analysis_name}: {e}")

    # =======================================================
    # 3. Infection Rate Comparison -> BAR CHART
    # =======================================================
    @Slot()
    def computeInfectionRateComparison(self):
        """
        Infection Rate Comparison Analysis
        Compares infection rates across varieties
        """
        analysis_name = "Infection Rate Comparison"
        print(f"[StatisticalAnalyzer] Starting {analysis_name}")
        self.analysisStarted.emit(analysis_name)

        try:
            records = self._getRecords()
            if not records:
                self.analysisError.emit(analysis_name, "No data available")
                return

            # Group by variety
            variety_infection_rates = defaultdict(lambda: {"total": 0, "diseases": Counter()})

            for record in records:
                variety = record.get("variaty", "Unknown")
                disease = record.get("diseasname", "Unknown")

                variety_infection_rates[variety]["total"] += 1
                variety_infection_rates[variety]["diseases"][disease] += 1

            result = {
                "analysis_type": analysis_name,
                "varieties": []
            }

            comparison_data = []

            for variety, data in variety_infection_rates.items():
                total = data["total"]
                comparison_data.append({
                    "variety": variety,
                    "total_infections": total
                })

                result["varieties"].append({
                    "name": variety,
                    "total_infections": total,
                    "infection_rate": total,
                    "disease_breakdown": [
                        {
                            "name": name,
                            "count": count,
                            "percentage": round((count / total) * 100, 2)
                        }
                        for name, count in data["diseases"].most_common()
                    ]
                })

            # Sort by infection rate (highest first)
            comparison_data.sort(key=lambda x: x["total_infections"], reverse=True)

            # Prepare plotable data for Bar Chart (3D)
            if self._plotModel:
                plot_data = {
                    "title": "Infection Rate by Variety",
                    "xAxis": "Variety",
                    "yAxis": "Total Infections",
                    "categories": [item["variety"] for item in comparison_data],
                    "values": [item["total_infections"] for item in comparison_data]
                }
                self._plotModel.setPlotData("bar", plot_data)

                # Also update ChartMapper for 2D charts
                # Convert to format ChartMapper expects for infection rate
                infection_result = {
                    "analysis_type": "Infection Rate Comparison",
                    "varieties": result["varieties"]
                }
                self._plotModel.chartMapper.updateFromAnalysisResult(infection_result)

            self._storeResult("infection_rate_comparison", result)
            self.analysisCompleted.emit(analysis_name, result)
            print(f"[StatisticalAnalyzer] Completed {analysis_name}")

        except Exception as e:
            self.analysisError.emit(analysis_name, str(e))
            print(f"[StatisticalAnalyzer] Error in {analysis_name}: {e}")

    # =======================================================
    # 4. Disease By Region -> LINE CHART (2D) / SURFACE (3D)
    # =======================================================
    @Slot()
    def computeDiseaseByRegion(self):
        """
        Disease By Region Analysis
        Returns data for Line Chart (2D) and Surface Plot (3D)
        """
        analysis_name = "Disease By Region"
        print(f"[StatisticalAnalyzer] Starting {analysis_name}")
        self.analysisStarted.emit(analysis_name)

        try:
            records = self._getRecords()
            if not records:
                self.analysisError.emit(analysis_name, "No data available")
                return

            region_disease_map = defaultdict(lambda: Counter())
            region_counts = Counter()

            for record in records:
                location = record.get("location", "Unknown")
                disease = record.get("diseasname", "Unknown")
                region_disease_map[location][disease] += 1
                region_counts[location] += 1

            # Get sorted lists
            regions_list = sorted(region_disease_map.keys())
            all_diseases = set()
            for diseases in region_disease_map.values():
                all_diseases.update(diseases.keys())
            diseases_list = sorted(list(all_diseases))

            # Prepare Line Series data (for 2D charts)
            lines_data = []
            for disease in diseases_list:
                points = []
                for region_idx, region in enumerate(regions_list):
                    count = region_disease_map[region].get(disease, 0)
                    points.append({
                        "x": region_idx,
                        "y": count
                    })
                lines_data.append({
                    "name": disease,
                    "points": points
                })

            # Prepare Surface data (for 3D charts)
            surface_data = []
            for region_idx, region in enumerate(regions_list):
                diseases = region_disease_map[region]
                for disease_idx, disease in enumerate(diseases_list):
                    count = diseases.get(disease, 0)
                    surface_data.append({
                        "row": float(region_idx),
                        "column": float(disease_idx),
                        "value": float(count)
                    })

            result = {
                "analysis_type": analysis_name,
                "total_records": len(records),
                "total_regions": len(regions_list),
                "total_diseases": len(diseases_list),
                "regions": regions_list,
                "diseases": diseases_list,
                "lines_data": lines_data,
                "regions_detail": []
            }

            for region, diseases in region_disease_map.items():
                total_for_region = region_counts[region]
                region_diseases_data = []
                for disease, count in diseases.items():
                    region_diseases_data.append({
                        "name": disease,
                        "count": count,
                        "percentage": round((count / total_for_region) * 100, 2) if total_for_region > 0 else 0
                    })
                result["regions_detail"].append({
                    "name": region,
                    "total_infections": total_for_region,
                    "diseases": region_diseases_data
                })

            # Update Plot Model (for 3D charts)
            if self._plotModel:
                plot_data = {
                    "title": "Disease Distribution by Region",
                    "xAxis": "Regions",
                    "yAxis": "Diseases",
                    "zAxis": "Number of Infections",
                    "surfaceData": surface_data
                }
                self._plotModel.setPlotData("surface", plot_data)

                # Update ChartMapper for 2D line charts
                self._plotModel.chartMapper.updateFromAnalysisResult(result)

            self._storeResult("disease_by_region", result)
            self.analysisCompleted.emit(analysis_name, result)
            print(f"[StatisticalAnalyzer] Completed with {len(lines_data)} disease lines across {len(regions_list)} regions")

        except Exception as e:
            self.analysisError.emit(analysis_name, str(e))
            print(f"[StatisticalAnalyzer] Error: {e}")

    # =======================================================
    # Run All Analyses
    # =======================================================
    @Slot()
    def runAllAnalyses(self):
        """
        Run all statistical analyses
        Each analysis updates the PlotModel with chart-specific data
        """
        print("[StatisticalAnalyzer] Running all analyses...")
        self.computeDiseaseFrequency()
        self.computeVarietySusceptibility()
        self.computeInfectionRateComparison()
        self.computeDiseaseByRegion()

    # =======================================================
    # Result Access
    # =======================================================
    @Slot(str, result="QVariant")
    def getResult(self, resultId):
        """Get analysis result by ID"""
        return self._results.get(resultId)

    @Slot(result="QVariantMap")
    def getAllResults(self):
        """Get all analysis results"""
        return self._results.copy()

    @Slot()
    def refreshCurrentChart(self):
        """Refresh the current chart based on last analysis"""
        if "disease_frequency" in self._results:
            self.computeDiseaseFrequency()
        elif "variety_susceptibility" in self._results:
            self.computeVarietySusceptibility()
        elif "infection_rate_comparison" in self._results:
            self.computeInfectionRateComparison()
        elif "disease_by_region" in self._results:
            self.computeDiseaseByRegion()

    # =======================================================
    # Reporting
    # =======================================================
    @Slot(str)
    def exportAnalysisReport(self, formatType):
        """Export analysis report to ~/Documents/PlantLab directory"""
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
                    writer.writerow(["Analysis Type", "Key Findings"])
                    for key, value in self._results.items():
                        summary = self._generateSummary(value)
                        writer.writerow([key, summary])

            else:
                self.reportFailed.emit(f"Unsupported format: {formatType}")
                return

            self.reportGenerated.emit(str(filepath))
            print(f"[StatisticalAnalyzer] Report exported to: {filepath}")

        except Exception as e:
            error_msg = f"Export failed: {str(e)}"
            print(error_msg)
            self.reportFailed.emit(error_msg)

    def _generateSummary(self, result):
        """Generate a text summary from analysis result"""
        if not isinstance(result, dict):
            return str(result)[:200]

        if "analysis_type" in result:
            if "diseases" in result:
                top_diseases = result["diseases"][:3]
                return f"Top diseases: {', '.join([d['name'] for d in top_diseases])}"

            if "varieties" in result:
                return f"Analyzed {len(result['varieties'])} varieties"

            if "regions" in result:
                return f"Analyzed {len(result['regions'])} regions"

        return str(result)[:200]