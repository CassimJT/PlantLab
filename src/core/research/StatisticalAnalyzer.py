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
    infectionRateDataChanged = Signal()  # Signal for grouped bar chart

    def __init__(self, parent=None):
        super().__init__(parent)
        self._barCategories = []
        self._barValues = []
        self._barSeriesName = ""

        self._lineSeries = []
        self._lineCategories = []

        self._scatterPoints = []

        # Grouped bar chart data for Infection Rate Comparison
        self._infectionRateCategories = []   # Varieties
        self._diseaseGroups = []              # Disease names
        self._infectionRateValuesMatrix = []  # 2D array

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
    # Properties for Infection Rate (Grouped Bar Chart)
    # =======================================================
    @Property("QVariantList", notify=infectionRateDataChanged)
    def infectionRateCategories(self):
        """Returns varieties for grouped bar chart X-axis"""
        return self._infectionRateCategories

    @Property("QVariantList", notify=infectionRateDataChanged)
    def diseaseGroups(self):
        """Returns disease groups for grouped bar chart"""
        return self._diseaseGroups

    @Property("QVariantList", notify=infectionRateDataChanged)
    def infectionRateValuesMatrix(self):
        """Returns 2D values matrix for grouped bar chart"""
        return self._infectionRateValuesMatrix

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
            # Update grouped bar chart data
            varieties = result.get("varieties", [])
            diseases = result.get("diseases", [])
            values_matrix = result.get("values_matrix", [])

            print(f"[ChartMapper] Infection Rate Comparison - Varieties: {len(varieties)}, Diseases: {len(diseases)}")
            if values_matrix:
                print(f"[ChartMapper] Values matrix shape: {len(values_matrix)} x {len(values_matrix[0]) if values_matrix else 0}")

            self._infectionRateCategories = varieties
            self._diseaseGroups = diseases
            self._infectionRateValuesMatrix = values_matrix
            self.infectionRateDataChanged.emit()
            print(f"[ChartMapper] Grouped bar chart updated: {len(varieties)} varieties, {len(diseases)} diseases")

        elif analysis_type == "Variety Susceptibility":
            # Get the scatter points directly from the result
            points = result.get("scatter_points", [])
            if not points:
                # Fallback: create from varieties if scatter_points not present
                varieties = result.get("varieties", [])
                for variety in varieties:
                    for disease in variety.get("susceptible_diseases", []):
                        points.append({
                            "x": float(variety.get("total_infections", 0)),
                            "y": float(disease.get("percentage", 0)),
                            "variety": variety.get("name"),
                            "disease": disease.get("name"),
                            "percentage": float(disease.get("percentage", 0)),
                            "count": disease.get("count", 0)
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
        self._infectionRateCategories = []
        self._diseaseGroups = []
        self._infectionRateValuesMatrix = []
        self.barDataChanged.emit()
        self.lineDataChanged.emit()
        self.scatterDataChanged.emit()
        self.infectionRateDataChanged.emit()
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
        if chartType in self._plotData or chartType == "grouped_bar":
            if chartType != "grouped_bar":
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
            bar_result = {
                "analysis_type": "Disease Frequency",
                "diseases": [{"name": c, "count": v} for c, v in zip(data["categories"], data["values"])]
            }
            self._chartMapper.updateFromAnalysisResult(bar_result)

        elif chartType == "grouped_bar" and "varieties" in data and "diseases" in data:
            # Update ChartMapper for grouped bar chart
            print(f"[PlotModel] Updating grouped_bar with {len(data['varieties'])} varieties and {len(data['diseases'])} diseases")
            grouped_result = {
                "analysis_type": "Infection Rate Comparison",
                "varieties": data.get("varieties", []),
                "diseases": data.get("diseases", []),
                "values_matrix": data.get("values_matrix", [])
            }
            self._chartMapper.updateFromAnalysisResult(grouped_result)

        elif chartType == "scatter" and "points" in data:
            # Convert points to scatter model format
            points_data = []
            for point in data["points"]:
                points_data.append({
                    "x": point.get("x", 0),
                    "y": point.get("y", 0),
                    "z": point.get("z", point.get("count", 1)),
                    "label": point.get("label", ""),
                    "variety": point.get("variety", ""),
                    "disease": point.get("disease", "")
                })
            self._scatterModel.setDataList(points_data)
            print(f"[PlotModel] Updated scatter model with {len(points_data)} points")

            # Also update ChartMapper for 2D scatter charts
            scatter_result = {
                "analysis_type": "Variety Susceptibility",
                "scatter_points": data.get("points", []),
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
        self._fieldDataset = fieldDataset
        self._plotModel = plotModel
        self._results = {}
        self._exportDir = Path.home() / "Documents" / "PlantLab"
        self._ensureExportDirectory()

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
        try:
            self._exportDir.mkdir(parents=True, exist_ok=True)
            print(f"[StatisticalAnalyzer] Export directory ready: {self._exportDir}")
        except Exception as e:
            print(f"[StatisticalAnalyzer] Error creating export directory: {e}")

    def _getRecords(self):
        if self._fieldDataset:
            return self._fieldDataset.getRecords()
        return []

    def _storeResult(self, resultId, value):
        self._results[resultId] = value
        self.resultsChanged.emit()

    def _onDatasetChanged(self):
        self.datasetChanged.emit()
        print("[StatisticalAnalyzer] Source data changed")

    # =======================================================
    # Dataset Management
    # =======================================================
    @Slot()
    def refreshFromSource(self):
        print("[StatisticalAnalyzer] Refreshing all analyses from source")
        self.runAllAnalyses()

    @Slot()
    def clearResults(self):
        self._results.clear()
        self.resultsChanged.emit()
        if self._plotModel:
            self._plotModel.clear()

    # =======================================================
    # Analysis Methods
    # =======================================================
    @Slot(str)
    def runAnalysis(self, analysisName):
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
        self.runAnalysis(analysisName)

    # =======================================================
    # 1. Disease Frequency Analysis -> BAR CHART
    # =======================================================
    @Slot()
    def computeDiseaseFrequency(self):
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
        analysis_name = "Variety Susceptibility"
        print(f"[StatisticalAnalyzer] Starting {analysis_name}")
        self.analysisStarted.emit(analysis_name)

        try:
            records = self._getRecords()
            if not records:
                self.analysisError.emit(analysis_name, "No data available")
                return

            # DEBUG: Print all records for Local tomato
            print("\n=== DEBUG: Local tomato records ===")
            local_tomato_records = [r for r in records if r.get("variaty") == "Local tomato"]
            print(f"Total Local tomato records: {len(local_tomato_records)}")
            for r in local_tomato_records:
                print(f"  Disease: {r.get('diseasname')}, Location: {r.get('location')}, Confidence: {r.get('confidence')}")

            variety_disease_map = defaultdict(lambda: Counter())
            variety_counts = Counter()

            for record in records:
                variety = record.get("variaty", "Unknown")
                disease = record.get("diseasname", "Unknown")
                variety_disease_map[variety][disease] += 1
                variety_counts[variety] += 1

            # DEBUG: Print counts for Local tomato
            print("\n=== DEBUG: Local tomato counts ===")
            local_tomato_diseases = variety_disease_map.get("Local tomato", {})
            local_tomato_total = variety_counts.get("Local tomato", 0)
            print(f"Total infections: {local_tomato_total}")
            for disease, count in local_tomato_diseases.items():
                percentage = (count / local_tomato_total) * 100 if local_tomato_total > 0 else 0
                print(f"  {disease}: {count} infections ({percentage:.1f}%)")

            result = {
                "analysis_type": analysis_name,
                "varieties": []
            }

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

                    # Each disease-variety pair becomes ONE scatter point
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

            # DEBUG: Print scatter points for Local tomato
            print("\n=== DEBUG: Scatter points for Local tomato ===")
            local_scatter = [p for p in scatter_points if p.get("variety") == "Local tomato"]
            for p in local_scatter:
                print(f"  Disease: {p['disease']}, X={p['x']}, Y={p['y']}%, Count={p['count']}")

            result["scatter_points"] = scatter_points

            if self._plotModel:
                plot_data = {
                    "title": "Variety Susceptibility Analysis",
                    "xAxis": "Total Infections per Variety",
                    "yAxis": "Disease Percentage (%)",
                    "points": scatter_points,
                    "varieties_for_mapper": result["varieties"]
                }
                self._plotModel.setPlotData("scatter", plot_data)

            self._storeResult("variety_susceptibility", result)
            self.analysisCompleted.emit(analysis_name, result)
            print(f"[StatisticalAnalyzer] Completed {analysis_name} with {len(scatter_points)} points")

        except Exception as e:
            self.analysisError.emit(analysis_name, str(e))
            print(f"[StatisticalAnalyzer] Error in {analysis_name}: {e}")
    # =======================================================
    # 3. Infection Rate Comparison -> GROUPED BAR CHART
    # =======================================================
    @Slot()
    def computeInfectionRateComparison(self):
        analysis_name = "Infection Rate Comparison"
        print(f"[StatisticalAnalyzer] Starting {analysis_name}")
        self.analysisStarted.emit(analysis_name)

        try:
            records = self._getRecords()
            if not records:
                self.analysisError.emit(analysis_name, "No data available")
                return

            # Track: variety -> disease -> count
            variety_disease_map = defaultdict(lambda: defaultdict(int))
            variety_totals = defaultdict(int)

            # Also track diseases across all varieties for ordering
            all_diseases = set()

            for record in records:
                variety = record.get("variaty", "Unknown")
                disease = record.get("diseasname", "Unknown")
                variety_disease_map[variety][disease] += 1
                variety_totals[variety] += 1
                all_diseases.add(disease)

            # Sort diseases by overall frequency (most common first)
            disease_global_counts = defaultdict(int)
            for record in records:
                disease = record.get("diseasname", "Unknown")
                disease_global_counts[disease] += 1

            # Get top N diseases to show (limit to avoid overcrowding)
            DISPLAY_LIMIT = 8
            top_diseases = sorted(disease_global_counts.items(), key=lambda x: x[1], reverse=True)
            display_diseases = [d[0] for d in top_diseases[:DISPLAY_LIMIT]]

            # Add "Other" category for remaining diseases
            if len(top_diseases) > DISPLAY_LIMIT:
                display_diseases.append("Other Diseases")

            # Prepare data for grouped bar chart
            varieties_list = sorted(variety_totals.keys(), key=lambda x: variety_totals[x], reverse=True)
            varieties_list = varieties_list[:15]  # Limit to top 15 varieties to avoid overcrowding

            # Create a matrix of values: [variety][disease_index]
            values_matrix = []

            for variety in varieties_list:
                variety_row = []
                for disease in display_diseases:
                    if disease == "Other Diseases":
                        # Sum up all diseases not in top list
                        other_count = sum(
                            count for d, count in variety_disease_map[variety].items()
                            if d not in display_diseases
                        )
                        variety_row.append(other_count)
                    else:
                        variety_row.append(variety_disease_map[variety].get(disease, 0))
                values_matrix.append(variety_row)

            # Prepare result with detailed breakdown
            result = {
                "analysis_type": analysis_name,
                "varieties": varieties_list,
                "diseases": display_diseases,
                "values_matrix": values_matrix,
                "varieties_detail": []
            }

            # Build detailed variety info
            for i, variety in enumerate(varieties_list):
                variety_detail = {
                    "name": variety,
                    "total_infections": variety_totals[variety],
                    "disease_breakdown": []
                }
                for j, disease in enumerate(display_diseases):
                    count = values_matrix[i][j]
                    if count > 0:
                        percentage = round((count / variety_totals[variety]) * 100, 2) if variety_totals[variety] > 0 else 0
                        variety_detail["disease_breakdown"].append({
                            "name": disease,
                            "count": count,
                            "percentage": percentage
                        })
                result["varieties_detail"].append(variety_detail)

            # Update the plot model with grouped bar data
            if self._plotModel:
                plot_data = {
                    "title": "Infection Rate by Variety & Disease",
                    "xAxis": "Variety",
                    "yAxis": "Number of Infections",
                    "varieties": varieties_list,
                    "diseases": display_diseases,
                    "values_matrix": values_matrix
                }
                self._plotModel.setPlotData("grouped_bar", plot_data)

            self._storeResult("infection_rate_comparison", result)
            self.analysisCompleted.emit(analysis_name, result)
            print(f"[StatisticalAnalyzer] Completed {analysis_name} with {len(varieties_list)} varieties and {len(display_diseases)} disease groups")

        except Exception as e:
            self.analysisError.emit(analysis_name, str(e))
            print(f"[StatisticalAnalyzer] Error in {analysis_name}: {e}")

    # =======================================================
    # 4. Disease By Region -> LINE CHART (2D) / SURFACE (3D)
    # =======================================================
    @Slot()
    def computeDiseaseByRegion(self):
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

            regions_list = sorted(region_disease_map.keys())
            all_diseases = set()
            for diseases in region_disease_map.values():
                all_diseases.update(diseases.keys())
            diseases_list = sorted(list(all_diseases))

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

            # Find region with highest diseases
            region_with_most_diseases = None
            max_disease_count = 0
            for region, diseases in region_disease_map.items():
                total = sum(diseases.values())
                if total > max_disease_count:
                    max_disease_count = total
                    region_with_most_diseases = region

            # Find most frequent diseases overall
            disease_frequency = Counter()
            for record in records:
                disease = record.get("diseasname", "Unknown")
                disease_frequency[disease] += 1

            most_frequent_diseases = disease_frequency.most_common(5)

            result = {
                "analysis_type": analysis_name,
                "total_records": len(records),
                "total_regions": len(regions_list),
                "total_diseases": len(diseases_list),
                "regions": regions_list,
                "diseases": diseases_list,
                "lines_data": lines_data,
                "region_with_most_diseases": region_with_most_diseases,
                "most_frequent_diseases": [
                    {"name": name, "count": count}
                    for name, count in most_frequent_diseases
                ],
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

            if self._plotModel:
                plot_data = {
                    "title": "Disease Distribution by Region",
                    "xAxis": "Regions",
                    "yAxis": "Diseases",
                    "zAxis": "Number of Infections",
                    "surfaceData": surface_data
                }
                self._plotModel.setPlotData("surface", plot_data)
                self._plotModel.chartMapper.updateFromAnalysisResult(result)

            self._storeResult("disease_by_region", result)
            self.analysisCompleted.emit(analysis_name, result)
            print(f"[StatisticalAnalyzer] Completed with {len(lines_data)} disease lines across {len(regions_list)} regions")
            print(f"[StatisticalAnalyzer] Region with most diseases: {region_with_most_diseases} ({max_disease_count} infections)")
            print(f"[StatisticalAnalyzer] Most frequent diseases: {most_frequent_diseases[:3]}")

        except Exception as e:
            self.analysisError.emit(analysis_name, str(e))
            print(f"[StatisticalAnalyzer] Error: {e}")

    # =======================================================
    # Additional Helper Methods for QML
    # =======================================================

    @Slot(result=str)
    def getRegionWithMostDiseases(self):
        """Return the region with the highest number of disease cases"""
        result = self._results.get("disease_by_region", {})
        region = result.get("region_with_most_diseases", "Unknown")
        if region != "Unknown":
            # Find the count for that region
            for region_detail in result.get("regions_detail", []):
                if region_detail.get("name") == region:
                    return f"{region} ({region_detail.get('total_infections', 0)} cases)"
        return "No data available"

    @Slot(int, result="QVariantList")
    def getMostFrequentDiseases(self, limit=5):
        """Return the most frequent diseases across all data"""
        result = self._results.get("disease_by_region", {})
        diseases = result.get("most_frequent_diseases", [])
        return diseases[:limit]

    @Slot(int, result="QVariantList")
    def getTopDiseases(self, limit=10):
        """Return top N diseases from disease frequency analysis"""
        result = self._results.get("disease_frequency", {})
        diseases = result.get("diseases", [])
        return diseases[:limit]

    @Slot(int, result="QVariantList")
    def getTopVarietiesByInfection(self, limit=10):
        """Return top N varieties with highest infection rates"""
        result = self._results.get("infection_rate_comparison", {})
        varieties = result.get("varieties_detail", [])
        # Sort by total_infections descending
        varieties_sorted = sorted(varieties, key=lambda x: x.get("total_infections", 0), reverse=True)
        return varieties_sorted[:limit]

    @Slot(str, result="QVariantList")
    def getDiseasesForVariety(self, varietyName):
        """Get disease breakdown for a specific variety"""
        result = self._results.get("infection_rate_comparison", {})
        for variety in result.get("varieties_detail", []):
            if variety.get("name") == varietyName:
                return variety.get("disease_breakdown", [])
        return []

    @Slot(result="QVariantMap")
    def getSummaryStatistics(self):
        """Return summary statistics for the dashboard - only 3 cards"""
        disease_freq = self._results.get("disease_frequency", {})
        disease_region = self._results.get("disease_by_region", {})

        # Get top disease
        top_disease_data = disease_freq.get("diseases", [{}])[0] if disease_freq.get("diseases") else {}
        top_disease = top_disease_data.get("name", "Unknown")

        # Get most affected region
        most_affected_region = disease_region.get("region_with_most_diseases", "Unknown")

        return {
            "total_records": disease_freq.get("total_records", 0),
            "top_disease": top_disease,
            "most_affected_region": most_affected_region
        }
    @Slot()
    def debugChartMapper(self):
        """Debug method to check ChartMapper data"""
        if self._plotModel and self._plotModel.chartMapper:
            mapper = self._plotModel.chartMapper
            print("=== ChartMapper Debug ===")
            print(f"infectionRateCategories: {mapper.infectionRateCategories}")
            print(f"diseaseGroups: {mapper.diseaseGroups}")
            print(f"infectionRateValuesMatrix: {mapper.infectionRateValuesMatrix}")
            print(f"barCategories: {mapper.barCategories}")
            print(f"barValues: {mapper.barValues}")

    # =======================================================
    # Run All Analyses
    # =======================================================
    @Slot()
    def runAllAnalyses(self):
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
        return self._results.get(resultId)

    @Slot(result="QVariantMap")
    def getAllResults(self):
        return self._results.copy()

    @Slot()
    def refreshCurrentChart(self):
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