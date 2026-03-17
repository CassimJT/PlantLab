import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property string selectedImagePath: ""
    signal newAnalysis()

    RowLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 24

        /* ======================
           LEFT PANEL - IMAGE
           ====================== */
        Rectangle {
            Layout.preferredWidth: 350
            Layout.fillHeight: true

            color: "#ffffff"
            radius: 16
            border.color: "#e2e8f0"

            ColumnLayout {
                anchors.fill: parent
                spacing: 16

                /* Image header */
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60

                    color: "#f8fafc"
                    radius: 16
                    border.color: "#e2e8f0"

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 12

                        Text {
                            text: "" //image
                            font.pixelSize: 24
                        }

                        ColumnLayout {
                            spacing: 2

                            Text {
                                text: qsTr("Uploaded Image")
                                font.bold: true
                                color: "#0f172a"
                            }

                            Text {
                                text: root.selectedImagePath.length > 0
                                      ? root.selectedImagePath.split("/").pop()
                                      : ""

                                font.pixelSize: 12
                                color: "#64748b"
                                elide: Text.ElideMiddle
                                Layout.preferredWidth: 200
                            }
                        }
                    }
                }

                /* Image display */
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.leftMargin: 16
                    Layout.rightMargin: 16

                    color: "#f8fafc"
                    radius: 12

                    Image {
                        anchors.fill: parent
                        anchors.margins: 8
                        fillMode: Image.PreserveAspectFit

                        source: root.selectedImagePath.length > 0
                                ? "file://" + root.selectedImagePath
                                : ""
                    }
                }

                /* Back button */
                Button {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    Layout.leftMargin: 16
                    Layout.rightMargin: 16
                    Layout.bottomMargin: 16

                    text: "← " + qsTr("New Analysis")
                    flat: true

                    background: Rectangle {
                        radius: 8
                        color: parent.hovered ? "#f1f5f9" : "transparent"
                    }

                    onClicked: root.newAnalysis()
                }
            }
        }

        /* ======================
           RIGHT PANEL - RESULTS
           ====================== */
        ResultsContent {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}
