import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    property string selectedImagePath: ""
    signal newAnalysis()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Math.min(root.width, root.height) * 0.04
        spacing: root.height * 0.03

        /* ======================
           CONTENT
           ====================== */
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: root.width * 0.03

            /* LEFT: IMAGE */
            Rectangle {
                Layout.preferredWidth: Math.min(root.width * 0.38, 380)
                Layout.fillHeight: true
                radius: 14
                color: "#ffffff"
                border.color: "#dde3ed"
                border.width: 1
                clip: true

                Image {
                    anchors.fill: parent
                    anchors.margins: 10
                    fillMode: Image.PreserveAspectFit
                    source: root.selectedImagePath !== ""
                            ? "file://" + root.selectedImagePath
                            : ""
                    layer.enabled: true
                    layer.smooth: true
                }
            }

            /* RIGHT: RESULTS */
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: root.height * 0.018

                // Disease name card
                DiseaseCard {
                    diseaseName: InfarenceRunner.disease_name
                    Layout.fillWidth: true
                }

                // Description card
                InfoCard {
                    title: "Description"
                    content: InfarenceRunner.description
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }

                // Treatment card
                InfoCard {
                    title: "Treatment"
                    content: InfarenceRunner.cure
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.bottomMargin: 10
                }

                // Metrics row
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12
                    Layout.bottomMargin: 10

                    MetricCard {
                        title: "Confidence"
                        value: InfarenceRunner.confidence.toFixed(1) + "%"
                        Layout.fillWidth: true
                    }
                    MetricCard {
                        title: "Framework"
                        value: InfarenceRunner.current_framework
                        Layout.fillWidth: true
                    }
                }

                Item { Layout.fillHeight: true }

                /* ======================
                   NEW ANALYSIS BUTTON
                   ====================== */
                Rectangle {
                    Layout.fillWidth: true
                    height: Math.max(38, root.height * 0.062)
                    radius: 10
                    color: newAnalysisHover.containsMouse ? "#3d4fd6" : "#4f6ef7"
                    border.color: newAnalysisHover.containsMouse ? "#6b84f9" : "transparent"
                    border.width: 1
                    Behavior on color { ColorAnimation { duration: 150 } }

                    Text {
                        anchors.centerIn: parent
                        text: "← New Analysis"
                        color: "#ffffff"
                        font.pixelSize: Math.max(12, root.height * 0.02)
                        font.weight: Font.Medium
                    }
                    HoverHandler { id: newAnalysisHover }
                    TapHandler { onTapped: root.newAnalysis() }
                }
            }
        }
    }
}