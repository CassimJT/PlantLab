import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "./component"
import "../analysis/componets"

Page {
    id: dashboard

    property real metricCardheight: dashboard.height * 0.30
    property real chartHeight: dashboard.height * 0.40
    property int uniqueDiseaseCount: 0
    property string topDisease: "—"
    property string mostAffectedRegion: "—"

    background: Rectangle {
        color: Qt.rgba(0, 0, 0, 0)
        radius: 10
    }

    Timer {
        id: analysisTimer
        interval: 500
        repeat: false
        onTriggered: {
            console.log("Running analysis...")  
            if (StatisticalAnalyzer) {
                busy.visible = false
                StatisticalAnalyzer.runAnalysis("Disease Frequency")
                StatisticalAnalyzer.runAnalysis("Infection Rate Comparison")
                StatisticalAnalyzer.runAnalysis("Disease By Region")
                updateSummaryData() 
            }
        }
    }

    // Update summary data after analysis completes
    function updateSummaryData() {
        if (StatisticalAnalyzer) {
            var stats = StatisticalAnalyzer.getSummaryStatistics()
            uniqueDiseaseCount = stats.total_diseases || 0
            topDisease = stats.top_disease || "—"
            mostAffectedRegion = stats.most_affected_region || "—"
            console.log("Summary - Top Disease:", topDisease, "Region:", mostAffectedRegion)

            // Update the SummaryCard content
            if (summaryCard) {
                summaryCard.updateData(topDisease, mostAffectedRegion)
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16

            MetricCard {
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.metricCardheight
                DHTMeter {
                    id: dhtMeter
                    t_value: 0.0
                    h_value: 0.0
                    stateLabel: "OFF"
                }
            }

            SummaryCard {
                id: summaryCard
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.metricCardheight
                top_deseas: dashboard.topDisease
                top_rigeon: dashboard.mostAffectedRegion
            }

            MetricCard {
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.metricCardheight
                title: "Total Disease"

                Column {
                    anchors.centerIn: parent
                    spacing: 8

                    CircularProgressBar {
                        id: diseaseProgress
                        width: 100
                        height: 100
                        rawValue: uniqueDiseaseCount
                        maxValue: 38
                        progressColor: "#55aaff"
                        text: "Diseases"
                        textShowValue: true
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
        }

        ChartCard {
            id: chartCard
            Layout.fillWidth: true
            Layout.preferredHeight: dashboard.height * 0.45

            BusyIndicator {
                id: busy
                visible: true
                anchors.centerIn: parent
            }
        }
    }

    Connections {
        target: ResearcherDataService

        function onInferencesFetched(records) {
            console.log("Data fetched:", records.length, "records")
            busy.visible = true
            analysisTimer.start()
        }

        function onErrorOccurred(error) {
            console.error("DataService error:", error)
        }
    }

    Connections {
        target: StatisticalAnalyzer

        function onAnalysisCompleted(analysisName, result) {
            console.log("Analysis completed:", analysisName)
            if (analysisName === "Disease By Region") {
                updateSummaryData()
            }
        }
    }

    Component.onCompleted: {
        updateSummaryData()
    }
}