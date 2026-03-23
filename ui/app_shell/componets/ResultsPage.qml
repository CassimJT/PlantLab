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
                radius: 12
                color: "#f8fafc"

                Image {
                    anchors.fill: parent
                    anchors.margins: 10
                    fillMode: Image.PreserveAspectFit
                    source: root.selectedImagePath !== ""
                            ? "file://" + root.selectedImagePath
                            : ""
                }
            }

            /* RIGHT: RESULTS */
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 20

                DiseaseCard {
                    diseaseName: InfarenceRunner.disease_name
                }

                InfoCard {
                    title: "Description"
                    content: InfarenceRunner.description
                }

                InfoCard {
                    title: "Treatment"
                    content: InfarenceRunner.cure
                }

                RowLayout {
                    spacing: 10

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

                Button {
                    text: "← New Analysis"
                    Layout.fillWidth: true

                    onClicked: root.newAnalysis()
                }
            }
        }
    }
}