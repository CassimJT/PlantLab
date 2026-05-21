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

    // Function to refresh all summary data
    function refreshSummaryData() {
        if (StatisticalAnalyzer) {
            var stats = StatisticalAnalyzer.getSummaryStatistics()
            console.log("Summary stats:", JSON.stringify(stats))

            totalRecordsLabel.text = stats.total_records || "—"
            topDiseaseLabel.text = stats.top_disease || "—"
            regionImpactLabel.text = stats.most_affected_region || "—"
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
                    Layout.preferredHeight: analysisBtn.height
                    model: [
                        "Disease Frequency",
                        "Variety Susceptibility",
                        "Infection Rate Comparison",
                        "Disease By Region"
                    ]

                    onCurrentIndexChanged: {
                        if (root.visible) {
                            callAnalysis(analysisSelector.currentText)
                        }
                    }
                }

                Button {
                    id: analysisBtn
                    text: "Run Analysis"
                    onClicked: callAnalysis(analysisSelector.currentText)
                }

                Button {
                    id: analysisAllBtn
                    text: "Run All Analysis"
                    onClicked: {
                        if (StatisticalAnalyzer) {
                            StatisticalAnalyzer.runAllAnalyses()
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                Label {
                    text: root.isRunning ? "Running..." : "Ready"
                    color: root.isRunning ? "orange" : "green"
                    font.bold: true
                }
            }
        }

        // Summary Cards - 3 cards only
        Rectangle {
            Layout.fillWidth: true
            height: 110
            color: "#f8fafc"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 20

                // Card 1: Total Records
                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    color: "white"
                    radius: 8
                    border.color: "#e5e7eb"
                    border.width: 1

                    Column {
                        anchors.centerIn: parent
                        spacing: 5

                        Label {
                            text: "TOTAL RECORDS"
                            font.pixelSize: 11
                            color: "#6B7280"
                            font.bold: true
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Label {
                            id: totalRecordsLabel
                            text: "—"
                            font.pixelSize: 28
                            font.bold: true
                            color: "#3B82F6"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Label {
                            text: "total infections"
                            font.pixelSize: 10
                            color: "#9CA3AF"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }

                // Card 2: Top Disease
                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    color: "white"
                    radius: 8
                    border.color: "#e5e7eb"
                    border.width: 1

                    Column {
                        anchors.centerIn: parent
                        spacing: 5

                        Label {
                            text: "TOP DISEASE"
                            font.pixelSize: 11
                            color: "#6B7280"
                            font.bold: true
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Label {
                            id: topDiseaseLabel
                            text: "—"
                            font.pixelSize: 16
                            font.bold: true
                            color: "#EF4444"
                            anchors.horizontalCenter: parent.horizontalCenter
                            wrapMode: Text.WordWrap
                            maximumLineCount: 2
                        }
                        Label {
                            text: "most frequent"
                            font.pixelSize: 10
                            color: "#9CA3AF"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }

                // Card 3: Most Affected Region
                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    color: "white"
                    radius: 8
                    border.color: "#e5e7eb"
                    border.width: 1

                    Column {
                        anchors.centerIn: parent
                        spacing: 5

                        Label {
                            text: "MOST AFFECTED REGION"
                            font.pixelSize: 11
                            color: "#6B7280"
                            font.bold: true
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Label {
                            id: regionImpactLabel
                            text: "—"
                            font.pixelSize: 14
                            font.bold: true
                            color: "#8B5CF6"
                            anchors.horizontalCenter: parent.horizontalCenter
                            wrapMode: Text.WordWrap
                            maximumLineCount: 2
                        }
                        Label {
                            text: "highest cases"
                            font.pixelSize: 10
                            color: "#9CA3AF"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
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
                id: chartStack
                anchors.fill: parent
                anchors.margins: 12
                currentIndex: {
                    switch (analysisSelector.currentText) {
                        case "Disease Frequency": return 0
                        case "Infection Rate Comparison": return 1
                        case "Variety Susceptibility": return 2
                        case "Disease By Region": return 3
                        default: return 0
                    }
                }

                // Disease Frequency Bar Chart
                DiseaseFrequencyChart {
                    id: diseaseFreqChart
                    chartMapper: StatisticalAnalyzer ? StatisticalAnalyzer.plotModel.chartMapper : null
                }

                // Infection Rate Bar Chart
                InfectionRateChart {
                    id: infectionRateChart
                    chartMapper: StatisticalAnalyzer ? StatisticalAnalyzer.plotModel.chartMapper : null
                }

                // Scatter Chart for Variety Susceptibility
                ScatterSeriesChart {
                    id: scatterChart
                    chartMapper: StatisticalAnalyzer ? StatisticalAnalyzer.plotModel.chartMapper : null
                }

                // Pie/Line Chart for Disease By Region
                PieSeriesChart {
                    id: pieChart
                    chartMapper: StatisticalAnalyzer ? StatisticalAnalyzer.plotModel.chartMapper : null
                }
            }
        }
    }

    Connections {
        target: StatisticalAnalyzer
        function onAnalysisCompleted(analysisName, result) {
            console.log("Analysis completed:", analysisName)
            root.isRunning = false
            refreshSummaryData()

            if (analysisName === "Disease Frequency") {
                if (diseaseFreqChart) diseaseFreqChart.updateFromMapper()
            }
            else if (analysisName === "Infection Rate Comparison") {
                if (infectionRateChart) infectionRateChart.updateFromMapper()
            }
            else if (analysisName === "Variety Susceptibility") {
                if (scatterChart) scatterChart.updateFromMapper()
            }
            else if (analysisName === "Disease By Region") {
                if (pieChart) pieChart.updateFromMapper()
            }
        }

        function onAnalysisError(analysisName, errorMessage) {
            console.error("Analysis error:", errorMessage)
            root.isRunning = false
        }
    }

    Component.onCompleted: {
        analysisSelector.currentIndex = 0
        callAnalysis("Disease Frequency")
        StatisticalAnalyzer.runAllAnalyses()
        Qt.callLater(refreshSummaryData, 500)
    }
}