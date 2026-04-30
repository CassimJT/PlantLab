# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Slot, Signal, Property, QUrl, QMarginsF
from PySide6.QtGui import QTextDocument, QPageSize, QPageLayout
from PySide6.QtPrintSupport import QPrinter
from .FieldDataset import FieldDataset
import os
from datetime import datetime
class FieldDataExplorer(QObject):
    # =======================================================
    # Signals
    # =======================================================
    dataLoaded = Signal(int)
    exportCompleted = Signal(str)
    exportFailed = Signal(str)
    filterChanged = Signal()
    pdfGenerationCompleted = Signal(str)  # Emits file path
    pdfGenerationFailed = Signal(str)     # Emits error message
    pdfGenerationProgress = Signal(int)

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

    # =======================================================
    # PDF Report Generation Methods
    # =======================================================

    @Slot(str, 'QVariant', result=str)
    def generateReportPdf(self, reportType, reportData):
        """
        Generate PDF from report data with progress updates
        """
        try:
            # IMPORTANT: Convert QML object safely
            if reportData is None:
                reportData = {}
            elif hasattr(reportData, "value"):          # QVariant case
                reportData = reportData.value() or {}

            print(f"Generating PDF for report type: {reportType}")

            # Emit progress: 10% - Starting
            self.pdfGenerationProgress.emit(10)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_report_type = reportType.replace(" ", "_").replace("/", "_")
            filename = f"{safe_report_type}_{timestamp}.pdf"
            filepath = os.path.join(self._dataset.getExportDirectory(), filename)

            # Emit progress: 30% - Generating HTML
            self.pdfGenerationProgress.emit(30)

            # Generate HTML content
            html_content = self._generateHtmlReport(reportType, reportData)

            # Emit progress: 60% - Creating PDF
            self.pdfGenerationProgress.emit(60)

            # Convert HTML to PDF
            if self._htmlToPdf(html_content, filepath):
                # Emit progress: 100% - Complete
                self.pdfGenerationProgress.emit(100)
                self.pdfGenerationCompleted.emit(filepath)
                print(f"PDF generated successfully: {filepath}")
                return filepath
            else:
                error_msg = "Failed to create PDF from HTML"
                self.pdfGenerationFailed.emit(error_msg)
                return error_msg

        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = f"PDF generation failed: {str(e)}"
            self.pdfGenerationFailed.emit(error_msg)
            return error_msg

    def _generateHtmlReport(self, reportType, data):
        """Generate HTML content for the report - Professional clean styling"""
        css_styles = """
        <style>
            @page {
                size: A4 portrait;
                margin: 25mm;
            }
            body {
                font-family: Arial, Helvetica, sans-serif;
                color: #333333;
                line-height: 1.6;
                font-size: 11pt;
            }
            .header {
                text-align: center;
                margin-bottom: 50px;
                padding-bottom: 35px;
                border-bottom: 4px solid #2E7D32;
            }
            .title {
                font-size: 28pt;
                font-weight: bold;
                color: #2E7D32;
                margin: 0 0 15px 0;
            }
            .subtitle {
                font-size: 14pt;
                color: #555555;
                margin: 8px 0;
            }
            .summary {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 40px;
                border-left: 5px solid #4CAF50;
            }
            .summary-title {
                font-size: 16pt;
                font-weight: bold;
                margin-bottom: 12px;
                color: #2E7D32;
            }
            h3 {
                font-size: 18pt;
                color: #2E7D32;
                margin: 40px 0 18px 0;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 25px 0;
                font-size: 11pt;
            }
            th, td {
                border: 1px solid #dddddd;
                padding: 12px 10px;
                text-align: left;
            }
            th {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 12pt;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .footer {
                text-align: center;
                font-size: 10pt;
                color: #777777;
                margin-top: 80px;
                padding-top: 25px;
                border-top: 1px solid #eeeeee;
            }
        </style>
        """

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_title = reportType.replace('_', ' ').title()

        if reportType == "disease_frequency":
            content = self._generateDiseaseFrequencyHtml(data)
        elif reportType == "variety_susceptibility":
            content = self._generateVarietySusceptibilityHtml(data)
        elif reportType == "infection_rate":
            content = self._generateInfectionRateHtml(data)
        elif reportType == "disease_by_region":
            content = self._generateDiseaseByRegionHtml(data)
        else:
            content = "<p>Unknown report type</p>"

        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{report_title} Report</title>
            {css_styles}
        </head>
        <body>
            <div class="header">
                <div class="title">PlantLab Analysis Report</div>
                <div class="subtitle">Report Type: {report_title}</div>
                <div class="subtitle">Generated: {timestamp}</div>
            </div>
            {content}
            <div class="footer">
                Generated by PlantLab Data Analysis System<br>
                © {datetime.now().year} PlantLab - All Rights Reserved
            </div>
        </body>
        </html>
        """
        return html

    def _generateDiseaseFrequencyHtml(self, data):
        """Generate HTML for disease frequency report"""
        html = '<div class="summary">'
        html += '<div class="summary-title">Summary Statistics</div>'
        html += f'<p><strong>Total Records:</strong> {data.get("total_records", 0)}</p>'
        html += f'<p><strong>Distinct Diseases:</strong> {len(data.get("diseases", []))}</p>'
        html += '</div>'

        html += '<h3>Disease Frequency Distribution</h3>'
        html += '<table>'
        html += '<tr><th>Disease Name</th><th>Count</th><th>Percentage</th></tr>'

        diseases = data.get("diseases", [])
        for disease in diseases:
            html += f'<tr>'
            html += f'<td>{disease.get("name", "N/A")}</td>'
            html += f'<td>{disease.get("count", 0)}</td>'
            html += f'<td>{disease.get("percentage", 0)}%</td>'
            html += f'</tr>'

        html += '</table>'
        return html

    def _generateVarietySusceptibilityHtml(self, data):
        """Generate HTML for variety susceptibility report"""
        html = '<div class="summary">'
        html += '<div class="summary-title">Susceptibility Overview</div>'
        html += f'<p><strong>Total Varieties:</strong> {len(data.get("varieties", []))}</p>'
        html += '</div>'

        html += '<h3>Variety Susceptibility Details</h3>'
        html += '<table>'
        html += '<tr><th>Variety Name</th><th>Total Infections</th><th>Susceptible Diseases</th></tr>'

        varieties = data.get("varieties", [])
        for variety in varieties:
            diseases = variety.get("susceptible_diseases", [])
            disease_list = ", ".join([f"{d.get('name', 'N/A')} ({d.get('percentage', 0)}%)" for d in diseases[:3]])

            html += f'<tr>'
            html += f'<td>{variety.get("name", "N/A")}</td>'
            html += f'<td>{variety.get("total_infections", 0)}</td>'
            html += f'<td>{disease_list}</td>'
            html += f'</tr>'

        html += '</table>'
        return html

    def _generateInfectionRateHtml(self, data):
        """Generate HTML for infection rate report"""
        html = '<div class="summary">'
        html += '<div class="summary-title">Infection Rate Analysis</div>'
        html += f'<p><strong>Total Varieties:</strong> {len(data.get("varieties", []))}</p>'
        html += '</div>'

        html += '<h3>Infection Rates by Variety</h3>'
        html += '<table>'
        html += '<tr><th>Variety Name</th><th>Total Infections</th><th>Infection Rate</th></tr>'

        varieties = data.get("varieties", [])
        for variety in varieties:
            html += f'<tr>'
            html += f'<td>{variety.get("name", "N/A")}</td>'
            html += f'<td>{variety.get("total_infections", 0)}</td>'
            html += f'<td>{variety.get("infection_rate", "0")}%</td>'
            html += f'</tr>'

        html += '</table>'
        return html

    def _generateDiseaseByRegionHtml(self, data):
        """Generate HTML for disease by region report"""
        html = '<div class="summary">'
        html += '<div class="summary-title">Regional Distribution</div>'
        html += f'<p><strong>Regions Analyzed:</strong> {data.get("total_regions", 0)}</p>'
        html += f'<p><strong>Diseases Detected:</strong> {data.get("total_diseases", 0)}</p>'
        html += '</div>'

        html += '<h3>Disease Distribution by Region</h3>'

        regions = data.get("regions_detail", [])
        for region in regions:
            html += f'<h4>{region.get("name", "N/A")}</h4>'
            html += '<table>'
            html += '<tr><th>Disease</th><th>Cases</th></tr>'

            diseases = region.get("diseases", [])
            for disease in diseases[:5]:  # Top 5 diseases per region
                html += f'<tr>'
                html += f'<td>{disease.get("name", "N/A")}</td>'
                html += f'<td>{disease.get("count", 0)}</td>'
                html += f'</tr>'

            html += '</table>'

        return html

    def _htmlToPdf(self, html_content, output_path):
        """Convert HTML to PDF - Clean version with good scaling"""
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(output_path)
            printer.setResolution(300)

            # Force A4 Portrait
            page_size = QPageSize(QPageSize.A4)
            printer.setPageSize(page_size)

            layout = QPageLayout()
            layout.setPageSize(page_size)
            layout.setOrientation(QPageLayout.Portrait)
            layout.setMode(QPageLayout.StandardMode)

            margins = QMarginsF(20, 20, 20, 20)
            layout.setMargins(margins)
            printer.setPageLayout(layout)

            # Create document
            doc = QTextDocument()
            doc.setHtml(html_content)
            doc.print_(printer)

            print(f"PDF generated successfully: {output_path}")
            return True

        except Exception as e:
            print(f"Error in _htmlToPdf: {e}")
            import traceback
            traceback.print_exc()
            return False