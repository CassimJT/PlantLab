import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "./componets"

Page {
    id: root
    signal generateReport()

    property bool isRunning: false

    function callAnalysis(analysisType) {
        console.log("Calling analysis:", analysisType)
        if (StatisticalAnalyzer) {
            root.isRunning = true
            StatisticalAnalyzer.runAnalysis(analysisType)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Toolbar
        Rectangle {
            height: 60
            Layout.fillWidth: true
            color: "#ffffff"
            border.color: "#e5e7eb"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                ComboBox {
                    id: analysisSelector
                    Layout.preferredWidth: 300
                    model: [
                        "Disease Frequency",
                        "Variety Susceptibility",
                        "Infection Rate Comparison",
                        "Disease By Region"
                    ]

                    // Auto-run when selection changes
                    onCurrentIndexChanged: {
                        if (root.visible) {   // only run if page is visible
                            callAnalysis(analysisSelector.currentText)
                        }
                    }
                }

                Button {
                    text: "Run Analysis"
                    onClicked: callAnalysis(analysisSelector.currentText)
                }

                Button {
                    text: "Generate Report"
                    onClicked: root.generateReport()
                }

                Item { Layout.fillWidth: true }

                Label {
                    text: root.isRunning ? "Running..." : "Ready"
                    color: root.isRunning ? "orange" : "green"
                    font.bold: true
                }
            }
        }

        // Summary Cards
        Rectangle {
            Layout.fillWidth: true
            height: 110
            color: "#f8fafc"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 20

                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    Column {
                        anchors.centerIn: parent
                        Label { text: "Total Records" }
                        Label { id: totalRecordsLabel; text: "—"; font.bold: true; font.pixelSize: 20 }
                    }
                }
                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    Column {
                        anchors.centerIn: parent
                        Label { text: "Top Category" }
                        Label { id: topCategoryLabel; text: "—"; font.bold: true; font.pixelSize: 18 }
                    }
                }
                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    Column {
                        anchors.centerIn: parent
                        Label { text: "Region Impact" }
                        Label { id: regionImpactLabel; text: "—"; font.bold: true; font.pixelSize: 18 }
                    }
                }
            }
        }

        // Chart Area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "white"
            border.color: "#e5e7eb"

            StackLayout {
                anchors.fill: parent
                anchors.margins: 12
                currentIndex: {
                    switch (analysisSelector.currentText) {
                        case "Disease Frequency":
                        case "Infection Rate Comparison": return 0
                        case "Variety Susceptibility":    return 1
                        case "Disease By Region":         return 2
                        default: return 0
                    }
                }

                BarSeriesChart     { chartMapper: StatisticalAnalyzer ? StatisticalAnalyzer.plotModel.chartMapper : null }
                ScatterSeriesChart { chartMapper: StatisticalAnalyzer ? StatisticalAnalyzer.plotModel.chartMapper : null }
                PieSeriesChart    { chartMapper: StatisticalAnalyzer ? StatisticalAnalyzer.plotModel.chartMapper : null }   // your QtCharts version
            }
        }
    }

    Connections {
        target: StatisticalAnalyzer
        function onAnalysisCompleted(analysisName, result) {
            console.log("Analysis completed:", analysisName)
            root.isRunning = false

            if (analysisName === "Disease Frequency" || analysisName === "Infection Rate Comparison") {
                totalRecordsLabel.text = result.total_records || "—"
                topCategoryLabel.text = result.diseases?.[0]?.name || result.varieties?.[0]?.name || "—"
            }
            else if (analysisName === "Variety Susceptibility") {
                topCategoryLabel.text = result.varieties?.[0]?.name || "—"
            }
            else if (analysisName === "Disease By Region") {
                totalRecordsLabel.text = result.total_records || "—"
                regionImpactLabel.text = result.regions_detail?.[0]?.name || "—"
            }
        }

        function onAnalysisError(analysisName, errorMessage) {
            console.error("Analysis error:", errorMessage)
            root.isRunning = false
        }
    }

    Component.onCompleted: {
        analysisSelector.currentIndex = 0
        // Initial load
        callAnalysis("Disease Frequency")
    }
}