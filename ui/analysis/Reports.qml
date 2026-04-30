import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../utiis" as Utils

Page {
    id: root

    signal exportPdfRequested(string reportId)
    signal exportCsvRequested(string reportId)
    signal deleteReportRequested(string reportId)

    property string selectedReportId: ""
    property var currentReport: ({})
    property var reportsList: []
    property bool showProgressDialog: false
    property int exportProgress: 0
    property string exportFilePath: ""

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ============================
        // TOP TOOLBAR
        // ============================
        Rectangle {
            height: 50
            Layout.fillWidth: true
            color: "#ffffff"
            border.color: "#e5e7eb"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Button {
                    text: "Export PDF"
                    icon.source: "qrc:/assets/analysis/icons8-pdf-50.svg"
                    icon.width: 20
                    icon.height: 20
                    enabled: root.selectedReportId !== ""
                    onClicked: exportToPdf()
                }

                Button {
                    text: "Delete"
                    icon.source: "qrc:/assets/analysis/icons8-delete-48.svg"
                    icon.width: 20
                    icon.height: 20
                    enabled: root.selectedReportId !== ""
                    onClicked: deleteCurrentReport()
                }

                Button {
                    text: "Refresh Reports"
                    onClicked: loadReports()
                }

                Item { Layout.fillWidth: true }

                Label {
                    text: root.selectedReportId === "" ?
                              "No report selected" :
                              "Selected: " + root.selectedReportId
                    color: "#6b7280"
                }
            }
        }

        // ============================
        // MAIN SPLIT VIEW
        // ============================
        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Horizontal

            // -------- REPORT VIEWER --------
            Rectangle {
                SplitView.fillWidth: true
                color: "white"
                border.color: "#e5e7eb"

                ScrollView {
                    anchors.fill: parent
                    anchors.margins: 12

                    Column {
                        width: parent.width
                        spacing: 12

                        Label {
                            id: reportTitle
                            text: "Select a report from the list"
                            font.pixelSize: 20
                            font.bold: true
                        }

                        Rectangle {
                            width: parent.width
                            height: 1
                            color: "#e5e7eb"
                        }

                        Label {
                            id: summaryLabel
                            text: "Report summary will appear here..."
                            wrapMode: Text.WordWrap
                            font.pixelSize: 12
                        }

                        Rectangle {
                            width: parent.width
                            height: 1
                            color: "#e5e7eb"
                            visible: reportRepeater.count > 0
                        }

                        Label {
                            text: "Detailed Results:"
                            font.bold: true
                            visible: reportRepeater.count > 0
                        }

                        Repeater {
                            id: reportRepeater
                            model: []
                            delegate: Rectangle {
                                width: parent.width
                                height: 50
                                border.color: "#e5e7eb"
                                radius: 4
                                color: index % 2 === 0 ? "#f8fafc" : "white"

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 10

                                    Label {
                                        text: modelData.section
                                        font.pixelSize: 13
                                        font.bold: true
                                        Layout.preferredWidth: parent.width * 0.35
                                        elide: Text.ElideRight
                                    }

                                    Label {
                                        text: modelData.value
                                        font.pixelSize: 12
                                        color: "#475569"
                                        Layout.fillWidth: true
                                        elide: Text.ElideRight
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // -------- REPORT LIST --------
            Rectangle {
                implicitWidth: 250
                SplitView.maximumWidth: 350
                SplitView.minimumWidth: 150
                color: "#f8fafc"
                border.color: "#e5e7eb"

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    Rectangle {
                        height: 40
                        Layout.fillWidth: true
                        color: "#f1f5f9"
                        border.color: "#e5e7eb"

                        Label {
                            anchors.centerIn: parent
                            text: "Saved Reports"
                            font.bold: true
                        }
                    }

                    ListView {
                        id: reportList
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: root.reportsList

                        delegate: Rectangle {
                            width: ListView.view.width
                            height: 70
                            radius: 4
                            color: ListView.isCurrentItem ? "#e0f2fe" : "white"
                            border.color: "#e5e7eb"

                            Column {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 4

                                Label {
                                    text: modelData.title || "Report"
                                    font.bold: true
                                    font.pixelSize: 13
                                    elide: Text.ElideRight
                                    width: parent.width
                                }

                                Label {
                                    text: modelData.createdAt ?
                                          new Date(modelData.createdAt).toLocaleString() : ""
                                    font.pixelSize: 11
                                    color: "#6b7280"
                                }

                                Label {
                                    text: modelData.type ?
                                          modelData.type.replace(/_/g, " ").toUpperCase() : ""
                                    font.pixelSize: 10
                                    color: "#3b82f6"
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    reportList.currentIndex = index
                                    root.selectedReportId = modelData.id
                                    displayReport(modelData)
                                }
                            }
                        }

                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                    }
                }
            }
        }
    }

    // ============================
    // Progress Dialog
    // ============================
    Dialog {
        id: progressDialog
        modal: true
        title: "Exporting PDF"
        width: 300
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        closePolicy: Popup.NoAutoClose

        ColumnLayout {
            spacing: 15
            anchors.fill: parent

            Label {
                text: "Generating PDF report..."
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
            }

            ProgressBar {
                id: progressBar
                value: root.exportProgress / 100
                Layout.fillWidth: true
            }

            Label {
                id: progressLabel
                text: Math.floor(root.exportProgress) + "%"
                Layout.alignment: Qt.AlignHCenter
                font.pixelSize: 12
                color: "#666"
            }

            Label {
                text: "Please wait..."
                font.pixelSize: 11
                color: "#888"
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }

    // ============================
    // Completion Dialog
    // ============================
    Dialog {
        id: completionDialog
        modal: true
        title: "Export Complete"
        width: 350
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2

        ColumnLayout {
            spacing: 20
            anchors.fill: parent

            Label {
                text: "PDF Report Generated Successfully!"
                font.bold: true
                color: "#2E7D32"
                Layout.alignment: Qt.AlignHCenter
            }

            Label {
                text: "File saved to:"
                font.pixelSize: 11
                color: "#666"
                Layout.alignment: Qt.AlignHCenter
            }

            Label {
                text: root.exportFilePath.split('/').pop()
                font.pixelSize: 12
                font.bold: true
                color: "#2196F3"
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }

            Rectangle {
                height: 1
                Layout.fillWidth: true
                color: "#ddd"
            }

            RowLayout {
                spacing: 10
                Layout.alignment: Qt.AlignHCenter

                Button {
                    text: "Open File"
                    onClicked: {
                        Qt.openUrlExternally("file:///" + root.exportFilePath)
                        completionDialog.close()
                    }
                }

                Button {
                    text: "Open Folder"
                    onClicked: {
                        FieldDataExplorer.openExportDirectory()
                        completionDialog.close()
                    }
                }

                Button {
                    text: "Close"
                    onClicked: completionDialog.close()
                }
            }
        }
    }

    // ============================
    // PDF Export Functions
    // ============================

    function exportToPdf() {
        if (!root.currentReport || !root.currentReport.data) {
            showNotification("No report selected")
            return
        }

        console.log("Exporting to PDF: " + root.currentReport.type)

        // Reset progress and show dialog
        root.exportProgress = 0
        progressDialog.open()

        // Call the PDF generation
        var result = FieldDataExplorer.generateReportPdf(
            root.currentReport.type,
            root.currentReport.data
        )

        console.log("generateReportPdf returned:", result)
    }

    function deleteCurrentReport() {
        if (!root.selectedReportId) return

        // Find and remove the report
        for (var i = 0; i < root.reportsList.length; i++) {
            if (root.reportsList[i].id === root.selectedReportId) {
                root.reportsList.splice(i, 1)
                break
            }
        }

        // Clear selection
        root.selectedReportId = ""
        root.currentReport = {}
        reportTitle.text = "Select a report from the list"
        summaryLabel.text = "Report summary will appear here..."
        reportRepeater.model = []

        showNotification("Report deleted")
    }

    function showNotification(message) {
        // Simple notification using a temporary label
        var notification = Qt.createQmlObject('
            import QtQuick 2.15
            import QtQuick.Controls 2.15

            Rectangle {
                id: notify
                color: "#333"
                radius: 5
                opacity: 0
                z: 999

                Label {
                    text: message
                    color: "white"
                    padding: 10
                }

                PropertyAnimation {
                    target: notify
                    property: "opacity"
                    from: 0
                    to: 0.9
                    duration: 300
                }

                PropertyAnimation {
                    target: notify
                    property: "opacity"
                    from: 0.9
                    to: 0
                    duration: 300
                    delay: 2000
                    onFinished: notify.destroy()
                }

                Component.onCompleted: {
                    parent = root
                    anchors.centerIn = parent
                    width = implicitWidth + 20
                    height = implicitHeight + 20
                }
            }
        ', root, {"message": message})
    }

    // ============================
    // Report Loading Functions
    // ============================

    function loadReports() {
        console.log("Loading reports...")

        // Get reports from FieldDataExplorer or StatisticalAnalyzer
        if (typeof FieldDataExplorer !== 'undefined' && FieldDataExplorer) {
            var reports = FieldDataExplorer.getSavedReports ?
                          FieldDataExplorer.getSavedReports() : []

            if (!reports || reports.length === 0) {
                loadFromAnalysisResults()
            } else {
                reportsList = reports
            }
        } else if (typeof StatisticalAnalyzer !== 'undefined' && StatisticalAnalyzer) {
            loadFromAnalysisResults()
        } else {
            // If no analyzer available, try to load from dataset directly
            loadFromFieldData()
        }
    }

    function loadFromAnalysisResults() {
        var reports = []

        // Disease Frequency Report
        var diseaseResult = StatisticalAnalyzer.getResult("disease_frequency")
        if (diseaseResult && diseaseResult.diseases) {
            reports.push({
                id: "disease_frequency_report_" + Date.now(),
                title: "Disease Frequency Analysis",
                createdAt: new Date().toISOString(),
                type: "disease_frequency",
                data: diseaseResult
            })
        }

        // Variety Susceptibility Report
        var varietyResult = StatisticalAnalyzer.getResult("variety_susceptibility")
        if (varietyResult && varietyResult.varieties) {
            reports.push({
                id: "variety_susceptibility_report_" + Date.now(),
                title: "Variety Susceptibility Analysis",
                createdAt: new Date().toISOString(),
                type: "variety_susceptibility",
                data: varietyResult
            })
        }

        // Infection Rate Report
        var infectionResult = StatisticalAnalyzer.getResult("infection_rate_comparison")
        if (infectionResult && infectionResult.varieties) {
            reports.push({
                id: "infection_rate_report_" + Date.now(),
                title: "Infection Rate Comparison",
                createdAt: new Date().toISOString(),
                type: "infection_rate",
                data: infectionResult
            })
        }

        // Disease By Region Report
        var regionResult = StatisticalAnalyzer.getResult("disease_by_region")
        if (regionResult && regionResult.regions) {
            reports.push({
                id: "disease_by_region_report_" + Date.now(),
                title: "Disease Distribution by Region",
                createdAt: new Date().toISOString(),
                type: "disease_by_region",
                data: regionResult
            })
        }

        reportsList = reports
    }

    function loadFromFieldData() {
        // Create reports directly from FieldDataExplorer if available
        if (typeof FieldDataExplorer === 'undefined' || !FieldDataExplorer) return

        var reports = []
        var records = FieldDataExplorer.getAllRecords()

        if (records && records.length > 0) {
            // Analyze disease frequency
            var diseaseMap = {}
            for (var i = 0; i < records.length; i++) {
                var disease = records[i].diseasname
                if (disease) {
                    diseaseMap[disease] = (diseaseMap[disease] || 0) + 1
                }
            }

            var diseases = []
            for (var name in diseaseMap) {
                diseases.push({
                    name: name,
                    count: diseaseMap[name],
                    percentage: (diseaseMap[name] / records.length * 100).toFixed(1)
                })
            }
            diseases.sort(function(a, b) { return b.count - a.count })

            reports.push({
                id: "disease_frequency_" + Date.now(),
                title: "Disease Frequency Analysis",
                createdAt: new Date().toISOString(),
                type: "disease_frequency",
                data: {
                    total_records: records.length,
                    diseases: diseases
                }
            })
        }

        reportsList = reports
    }

    // ============================
    // Display Functions
    // ============================

    function displayReport(report) {
        root.currentReport = report
        if (!report || !report.data) return

        var data = report.data

        if (report.type === "disease_frequency") {
            displayDiseaseFrequencyReport(data)
        } else if (report.type === "variety_susceptibility") {
            displayVarietySusceptibilityReport(data)
        } else if (report.type === "infection_rate") {
            displayInfectionRateReport(data)
        } else if (report.type === "disease_by_region") {
            displayDiseaseByRegionReport(data)
        }
    }

    function displayDiseaseFrequencyReport(data) {
        reportTitle.text = "Disease Frequency Analysis"

        var summaryText = "Total Records: " + data.total_records + "\n\n"
        summaryText += "Top Diseases:\n"
        for (var i = 0; i < Math.min(data.diseases.length, 5); i++) {
            summaryText += "• " + data.diseases[i].name + ": " +
                          data.diseases[i].count + " (" + data.diseases[i].percentage + "%)\n"
        }
        summaryText += "\nTotal Distinct Diseases: " + data.diseases.length
        summaryLabel.text = summaryText

        var sections = []
        for (var i = 0; i < data.diseases.length; i++) {
            sections.push({
                section: data.diseases[i].name,
                value: data.diseases[i].count + " (" + data.diseases[i].percentage + "%)"
            })
        }
        reportRepeater.model = sections
    }

    function displayVarietySusceptibilityReport(data) {
        reportTitle.text = "Variety Susceptibility Analysis"

        var summaryText = "Total Varieties Analyzed: " + data.varieties.length + "\n\n"
        summaryText += "Most Susceptible Varieties:\n"
        var sorted = [...data.varieties].sort((a, b) => b.total_infections - a.total_infections)
        for (var i = 0; i < Math.min(sorted.length, 5); i++) {
            summaryText += "• " + sorted[i].name + ": " + sorted[i].total_infections + " infections\n"
        }
        summaryLabel.text = summaryText

        var sections = []
        for (var i = 0; i < data.varieties.length; i++) {
            var v = data.varieties[i]
            var diseasesList = ""
            for (var j = 0; j < Math.min(v.susceptible_diseases.length, 3); j++) {
                diseasesList += v.susceptible_diseases[j].name + " (" +
                               v.susceptible_diseases[j].percentage + "%)"
                if (j < Math.min(v.susceptible_diseases.length, 3) - 1) diseasesList += ", "
            }
            sections.push({
                section: v.name,
                value: v.total_infections + " infections - " + diseasesList
            })
        }
        reportRepeater.model = sections
    }

    function displayInfectionRateReport(data) {
        reportTitle.text = "Infection Rate Comparison"

        var summaryText = "Total Varieties: " + data.varieties.length + "\n\n"
        summaryText += "Highest Infection Rates:\n"
        var sorted = [...data.varieties].sort((a, b) => b.total_infections - a.total_infections)
        for (var i = 0; i < Math.min(sorted.length, 5); i++) {
            summaryText += "• " + sorted[i].name + ": " + sorted[i].total_infections + " infections\n"
        }
        summaryLabel.text = summaryText

        var sections = []
        for (var i = 0; i < data.varieties.length; i++) {
            var v = data.varieties[i]
            sections.push({
                section: v.name,
                value: "Total: " + v.total_infections + " | Rate: " + v.infection_rate
            })
        }
        reportRepeater.model = sections
    }

    function displayDiseaseByRegionReport(data) {
        reportTitle.text = "Disease Distribution by Region"

        var summaryText = "Regions Analyzed: " + data.total_regions + "\n"
        summaryText += "Diseases Detected: " + data.total_diseases + "\n\n"
        summaryText += "Region with Highest Impact:\n"
        if (data.regions_detail && data.regions_detail.length > 0) {
            var topRegion = [...data.regions_detail].sort((a, b) => b.total_infections - a.total_infections)[0]
            summaryText += "• " + topRegion.name + ": " + topRegion.total_infections + " infections"
        }
        summaryLabel.text = summaryText

        var sections = []
        for (var i = 0; i < data.regions_detail.length; i++) {
            var r = data.regions_detail[i]
            var topDisease = r.diseases.sort((a, b) => b.count - a.count)[0]
            sections.push({
                section: r.name,
                value: r.total_infections + " infections - Top: " +
                       (topDisease ? topDisease.name + " (" + topDisease.count + ")" : "N/A")
            })
        }
        reportRepeater.model = sections
    }

    // ============================
    // Connections to Business Logic
    // ============================
    Connections {
        target: StatisticalAnalyzer

        function onAnalysisCompleted(analysisName, result) {
            console.log("Analysis completed, refreshing reports:", analysisName)
            loadReports()
        }

        function onDatasetChanged() {
            console.log("Dataset changed, refreshing reports")
            loadReports()
        }
    }

    Connections {
        target: FieldDataExplorer

        function onPdfGenerationProgress(progress) {
            console.log("PDF Progress:", progress + "%")
            root.exportProgress = progress
            if (progress >= 100) {
                // Close progress dialog after a short delay
                progressDialog.close()
            }
        }

        function onPdfGenerationCompleted(filePath) {
            console.log("PDF generation completed:", filePath)
            root.exportFilePath = filePath
            completionDialog.open()
            showNotification("PDF saved: " + filePath.split('/').pop())
        }

        function onPdfGenerationFailed(errorMessage) {
            console.error("PDF generation failed:", errorMessage)
            progressDialog.close()
            showNotification("PDF failed: " + errorMessage)
        }

        function onDataLoaded(recordCount) {
            console.log("Data loaded:", recordCount, "records")
            loadReports()
        }
    }

    Component.onCompleted: {
        console.log("ReportsPage loaded")
        loadReports()
    }
}