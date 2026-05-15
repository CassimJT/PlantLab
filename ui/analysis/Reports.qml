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
                    anchors.margins: 16
                    contentWidth: availableWidth
                    clip: true

                    ColumnLayout {
                        width: parent.width
                        spacing: 20

                        Label {
                            id: reportTitle
                            text: "Select a report from the list"
                            font.pixelSize: 22
                            font.bold: true
                            Layout.fillWidth: true
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: "#e5e7eb"
                        }

                        // --- TWO HORIZONTAL CARDS ---
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 16
                            visible: root.selectedReportId !== ""

                            // Card 1: Main Summary
                            Rectangle {
                                Layout.fillWidth: true
                                // Matched to the insights card height with a little addition
                                Layout.preferredHeight: Math.min(insightsContent.implicitHeight + 40, 200)
                                color: "#f8fafc"
                                border.color: "#e5e7eb"
                                border.width: 1
                                radius: 6

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    spacing: 4

                                    Label {
                                        text: "Overview"
                                        font.bold: true
                                        font.pixelSize: 14
                                        color: "#0f172a"
                                    }

                                    ScrollView {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        clip: true
                                        contentWidth: availableWidth

                                        Label {
                                            id: summaryLabel
                                            width: parent.width
                                            text: "Report summary will appear here..."
                                            wrapMode: Text.WordWrap
                                            font.pixelSize: 13
                                            color: "#475569"
                                            verticalAlignment: Text.AlignTop
                                        }
                                    }
                                }
                            }

                            // Card 2: Insights / Top Items
                            Rectangle {
                                Layout.fillWidth: true
                                // Matched to the insights card height with a little addition
                                Layout.preferredHeight: Math.min(insightsContent.implicitHeight + 40, 200)
                                color: "#f8fafc"
                                border.color: "#e5e7eb"
                                border.width: 1
                                radius: 6

                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 12
                                    spacing: 4

                                    Label {
                                        text: "Key Insights"
                                        font.bold: true
                                        font.pixelSize: 14
                                        color: "#0f172a"
                                    }

                                    ScrollView {
                                        id: insightsScroll
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        clip: true
                                        contentWidth: availableWidth

                                        Label {
                                            id: insightsLabel
                                            width: parent.width
                                            text: "Additional insights will appear here..."
                                            wrapMode: Text.WordWrap
                                            font.pixelSize: 13
                                            color: "#475569"
                                            verticalAlignment: Text.AlignTop
                                        }
                                    }
                                }
                            }
                        }

                        // Hidden items used to calculate the natural height of the text for the cards
                        Item { id: summaryContent; property real implicitHeight: summaryLabel.implicitHeight }
                        Item { id: insightsContent; property real implicitHeight: insightsLabel.implicitHeight }
                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: "#e5e7eb"
                            visible: reportRepeater.count > 0
                        }

                        Label {
                            text: "Detailed Results:"
                            font.bold: true
                            font.pixelSize: 16
                            visible: reportRepeater.count > 0
                            Layout.topMargin: 10
                        }

                        // --- TWO OR THREE COLUMN GRID FOR DETAILS ---
                        GridLayout {
                            Layout.fillWidth: true
                            // Adjusts dynamically based on available width, perfect for desktop
                            columns: parent.width > 800 ? 3 : 2
                            columnSpacing: 16
                            rowSpacing: 16

                            Repeater {
                                id: reportRepeater
                                model: []
                                delegate: Rectangle {
                                    Layout.fillWidth: true
                                    Layout.alignment: Qt.AlignTop
                                    implicitHeight: detailLayout.implicitHeight + 24
                                    border.color: "#e5e7eb"
                                    radius: 6
                                    color: index % 2 === 0 ? "#f8fafc" : "white"

                                    ColumnLayout {
                                        id: detailLayout
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        spacing: 6

                                        Label {
                                            text: modelData.section
                                            font.pixelSize: 14
                                            font.bold: true
                                            color: "#0f172a"
                                            Layout.fillWidth: true
                                            wrapMode: Text.Wrap
                                        }

                                        Label {
                                            text: modelData.value
                                            font.pixelSize: 13
                                            color: "#475569"
                                            Layout.fillWidth: true
                                            wrapMode: Text.Wrap
                                        }
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
        insightsLabel.text = "Additional insights will appear here..."
        reportRepeater.model = []

        showNotification("Report deleted")
    }

    function showNotification(message) {
        var notification = Qt.createQmlObject(`
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
                                              `, root, {"message": message})
    }

    // ============================
    // Report Loading Functions
    // ============================

    function loadReports() {
        console.log("Loading reports...")

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
            loadFromFieldData()
        }
    }

    function loadFromAnalysisResults() {
        var reports = []

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
        if (typeof FieldDataExplorer === 'undefined' || !FieldDataExplorer) return

        var reports = []
        var records = FieldDataExplorer.getAllRecords()

        if (records && records.length > 0) {
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

        // Split data between the two cards
        summaryLabel.text = "Total Records Analyzed: " + data.total_records + "\n" +
                "Total Distinct Diseases: " + data.diseases.length

        var insightsText = ""
        for (var i = 0; i < Math.min(data.diseases.length, 5); i++) {
            insightsText += "• " + data.diseases[i].name + ": " +
                    data.diseases[i].count + " (" + data.diseases[i].percentage + "%)\n"
        }
        insightsLabel.text = insightsText.trim()

        var sections = []
        for (var j = 0; j < data.diseases.length; j++) {
            sections.push({
                              section: data.diseases[j].name,
                              value: "Total cases: " + data.diseases[j].count + "\nPercentage: " + data.diseases[j].percentage + "%"
                          })
        }
        reportRepeater.model = sections
    }

    function displayVarietySusceptibilityReport(data) {
        reportTitle.text = "Variety Susceptibility Analysis"

        // Split data between the two cards
        summaryLabel.text = "Total Varieties Analyzed: " + data.varieties.length

        var insightsText = ""
        var sorted = [...data.varieties].sort((a, b) => b.total_infections - a.total_infections)
        for (var i = 0; i < Math.min(sorted.length, 5); i++) {
            insightsText += "• " + sorted[i].name + ": " + sorted[i].total_infections + " infections\n"
        }
        insightsLabel.text = insightsText.trim()

        var sections = []
        for (var k = 0; k < data.varieties.length; k++) {
            var v = data.varieties[k]
            var diseasesList = ""
            for (var l = 0; l < Math.min(v.susceptible_diseases.length, 3); l++) {
                diseasesList += v.susceptible_diseases[l].name + " (" + v.susceptible_diseases[l].percentage + "%)"
                if (l < Math.min(v.susceptible_diseases.length, 3) - 1) diseasesList += ", "
            }
            sections.push({
                              section: v.name,
                              value: v.total_infections + " infections\n" + diseasesList
                          })
        }
        reportRepeater.model = sections
    }

    function displayInfectionRateReport(data) {
        reportTitle.text = "Infection Rate Comparison"

        // Split data between the two cards
        summaryLabel.text = "Total Varieties Compared: " + data.varieties.length

        var insightsText = ""
        var sorted = [...data.varieties].sort((a, b) => b.total_infections - a.total_infections)
        for (var i = 0; i < Math.min(sorted.length, 5); i++) {
            insightsText += "• " + sorted[i].name + ": " + sorted[i].total_infections + " infections\n"
        }
        insightsLabel.text = insightsText.trim()

        var sections = []
        for (var m = 0; m < data.varieties.length; m++) {
            var v = data.varieties[m]
            sections.push({
                              section: v.name,
                              value: "Total: " + v.total_infections + "\nRate: " + v.infection_rate
                          })
        }
        reportRepeater.model = sections
    }

    function displayDiseaseByRegionReport(data) {
        reportTitle.text = "Disease Distribution by Region"

        // Split data between the two cards
        summaryLabel.text = "Regions Analyzed: " + data.total_regions + "\n" +
                "Diseases Detected: " + data.total_diseases

        var insightsText = ""
        if (data.regions_detail && data.regions_detail.length > 0) {
            var topRegion = [...data.regions_detail].sort((a, b) => b.total_infections - a.total_infections)[0]
            insightsText += "• Top Region: " + topRegion.name + "\n  (" + topRegion.total_infections + " infections)"
        } else {
            insightsText = "No regional data available."
        }
        insightsLabel.text = insightsText

        var sections = []
        for (var n = 0; n < data.regions_detail.length; n++) {
            var r = data.regions_detail[n]
            var topDisease = r.diseases.sort((a, b) => b.count - a.count)[0]
            sections.push({
                              section: r.name,
                              value: "Total infections: " + r.total_infections + "\nTop Disease: " +
                                     (topDisease ? topDisease.name + " (" + topDisease.count + ")" : "N/A")
                          })
        }
        reportRepeater.model = sections
    }

    // ============================
    // Connections to Business Logic
    // ============================
    Connections {
        target: typeof StatisticalAnalyzer !== 'undefined' ? StatisticalAnalyzer : null

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
        target: typeof FieldDataExplorer !== 'undefined' ? FieldDataExplorer : null

        function onPdfGenerationProgress(progress) {
            console.log("PDF Progress:", progress + "%")
            root.exportProgress = progress
            if (progress >= 100) {
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