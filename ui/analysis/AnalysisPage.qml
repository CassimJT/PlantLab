import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    id: root

    signal runAnalysis(string type)
    signal generateReport()
    signal varietySelected(string name)

    property string currentAnalysis: ""
    property bool isRunning: false

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // =============================
        // TOP CONTROL BAR
        // =============================
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
                    Layout.preferredWidth: 260
                    Layout.preferredHeight: run.height
                    model: [
                        "Disease Frequency",
                        "Pest Frequency",
                        "Variety Susceptibility",
                        "Infection Rate Comparison",
                        "Disease By Region",
                        "Improvement Dataset"
                    ]
                }

                TextField {
                    id: varietyField
                    placeholderText: "Variety (if required)"
                    visible: analysisSelector.currentIndex === 2
                    Layout.preferredWidth: 180
                    onAccepted: root.varietySelected(text)
                }

                Button {
                    id: run
                    text: "Run"
                    enabled: !root.isRunning
                    onClicked: {
                        root.currentAnalysis = analysisSelector.currentText
                        root.runAnalysis(root.currentAnalysis)
                    }
                }

                Button {
                    text: "Generate Report"
                    onClicked: root.generateReport()
                }

                Item { Layout.fillWidth: true }

                Label {
                    text: root.isRunning ? "Running..." : "Idle"
                    color: root.isRunning ? "orange" : "green"
                }
            }
        }

        // =============================
        // METRIC CARDS AREA
        // =============================
        Rectangle {
            Layout.fillWidth: true
            height: 110
            color: "#f8fafc"
            border.color: "#e5e7eb"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 20

                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    radius: 6
                    color: "white"
                    border.color: "#e5e7eb"

                    Column {
                        anchors.centerIn: parent
                        Label { text: "Total Records" }
                        Label { text: "—" }   // bind to analyzer result
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    radius: 6
                    color: "white"
                    border.color: "#e5e7eb"

                    Column {
                        anchors.centerIn: parent
                        Label { text: "Top Category" }
                        Label { text: "—" }  // bind dynamically
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    radius: 6
                    color: "white"
                    border.color: "#e5e7eb"

                    Column {
                        anchors.centerIn: parent
                        Label { text: "Region Impact" }
                        Label { text: "—" }
                    }
                }
            }
        }

        // =============================
        // VISUALIZATION AREA
        // =============================
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "white"
            border.color: "#e5e7eb"

            Label {
                text: "Analysis Result Visualization"
                anchors.centerIn: parent
                color: "#9ca3af"
            }

            /*
            Later:
            - Replace with QtCharts
            - Or custom BarChart component
            - Or dynamic Repeater-based visualization
            */
        }
    }
}
