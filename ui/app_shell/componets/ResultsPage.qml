import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    property string selectedImagePath: ""
    signal newAnalysis()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 30
        spacing: 30

        /* ======================
           CONTENT
           ====================== */
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 30

            /* LEFT: IMAGE */
            Rectangle {
                Layout.preferredWidth: 350
                Layout.fillHeight: true
                radius: 14
                color: "#111827"
                border.color: "#2d3550"
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

                // Subtle corner badge showing image is loaded
                Rectangle {
                    visible: root.selectedImagePath !== ""
                    anchors.bottom: parent.bottom
                    anchors.right: parent.right
                    anchors.margins: 10
                    width: 28; height: 28; radius: 8
                    color: "#1a2035"
                    border.color: "#2d3550"; border.width: 1
                    Text {
                        anchors.centerIn: parent
                        text: "🌿"; font.pixelSize: 14
                    }
                }
            }

            /* RIGHT: RESULTS */
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 14

                // Disease name card
                DiseaseCard {
                    diseaseName: InfarenceRunner.disease_name
                }

                // Description card
                InfoCard {
                    title: "Description"
                    content: InfarenceRunner.description
                }

                // Treatment card
                InfoCard {
                    title: "Treatment"
                    content: InfarenceRunner.cure
                    Layout.bottomMargin: 10
                }

                // Metrics row
                RowLayout {
                    spacing: 12
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
                    height: 44
                    radius: 10
                    color: newAnalysisHover.containsMouse ? "#3d4fd6" : "#4f6ef7"
                    border.color: newAnalysisHover.containsMouse ? "#6b84f9" : "transparent"
                    border.width: 1
                    Behavior on color { ColorAnimation { duration: 150 } }

                    Text {
                        anchors.centerIn: parent
                        text: "← New Analysis"
                        color: "#ffffff"
                        font.pixelSize: 14
                        font.weight: Font.Medium
                    }

                    HoverHandler { id: newAnalysisHover }
                    TapHandler { onTapped: root.newAnalysis() }
                }
            }
        }
    }
}