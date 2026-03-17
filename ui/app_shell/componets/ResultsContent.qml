import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    Layout.fillWidth: true
    Layout.fillHeight: true
    color: "#ffffff"
    radius: 16
    border.color: "#e2e8f0"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 20

        // Results header
        RowLayout {
            Layout.fillWidth: true

            Text {
                text: qsTr("Analysis Results")
                font.pixelSize: 20
                font.bold: true
                color: "#0f172a"
            }

            Item { Layout.fillWidth: true }

            Rectangle {
                color: "#dbeafe"
                radius: 20
                RowLayout {
                    spacing: 8
                    Text { text: ""; font.pixelSize: 16 }
                    Text {
                        text: InfarenceRunner.confidence.toFixed(1) + "%"
                        font.bold: true
                        color: "#1e40af"
                    }
                }
            }
        }

        // Scrollable results
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ColumnLayout {
                width: parent.width
                spacing: 16

                // Disease name card
                DiseaseCard {
                    diseaseName: InfarenceRunner.disease_name
                }

                // Description card
                InfoCard {
                    title: qsTr("Description")
                    icon: ""
                    content: InfarenceRunner.description || qsTr("No description available")
                }

                // Treatment card
                InfoCard {
                    title: qsTr("Treatment")
                    icon: ""
                    content: InfarenceRunner.cure || qsTr("No treatment information available")
                }

                // Metrics row
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    MetricCard {
                        title: qsTr("Class ID")
                        value: InfarenceRunner.class_index >= 0 ? InfarenceRunner.class_index : "—"
                        icon: ""
                        Layout.fillWidth: true
                    }

                    MetricCard {
                        title: qsTr("Framework")
                        value: InfarenceRunner.current_framework || "—"
                        icon: ""
                        Layout.fillWidth: true
                    }
                }
            }
        }
    }
}
