import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Window {
    id: aboutWindow
    width: 680
    height: 600
    visible: true
    title: "About PlantLab"

    modality: Qt.ApplicationModal
    flags: Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 25
        spacing: 15

        // Header Section
        RowLayout {
            Layout.fillWidth: true
            ColumnLayout {
                spacing: 2
                Text {
                    text: "PlantLab Desktop"
                    font.pixelSize: 22
                    font.bold: true
                    color: "#2C3E50"
                }
                Text {
                    text: "User Navigation & Workflow Guide"
                    font.pixelSize: 13
                    color: "#7F8C8D"
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#BDC3C7"
        }

        // Intro
        Text {
            Layout.fillWidth: true
            text: "Welcome to PlantLab, the data and model management engine for the PlantDoctor ecosystem. Use this guide to quickly understand how to navigate the application workflow."
            wrapMode: Text.WordWrap
            font.pixelSize: 13
            color: "#34495E"
        }

        // Scrollable Document Body
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ColumnLayout {
                width: parent.width - 15
                spacing: 12

                // 1. DATA MANAGEMENT
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: dataColumn.height + 20
                    color: "#F8F9FA"
                    border.color: "#E2E8F0"
                    border.width: 1
                    radius: 6

                    ColumnLayout {
                        id: dataColumn
                        anchors.top: parent.top
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.margins: 12
                        spacing: 6

                        Text {
                            text: "1. Data Management"
                            font.pixelSize: 14
                            font.bold: true
                            color: "#2980B9"
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "• <b>Import:</b> Click <b>Data</b> in the main sidebar menu.\n• <b>Load:</b> Drag & drop a dataset folder or use the <i>Browse folder</i> button."
                            wrapMode: Text.WordWrap
                            font.pixelSize: 13
                            color: "#2C3E50"
                        }
                    }
                }

                // 2. MODEL MANAGEMENT
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: modelColumn.height + 20
                    color: "#F8F9FA"
                    border.color: "#E2E8F0"
                    border.width: 1
                    radius: 6

                    ColumnLayout {
                        id: modelColumn
                        anchors.top: parent.top
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.margins: 12
                        spacing: 6

                        Text {
                            text: "2. Model Management"
                            font.pixelSize: 14
                            font.bold: true
                            color: "#2980B9"
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "Click <b>Models</b> in the sidebar and use the inner sub-tabs:\n" +
                                  "• <b>Library:</b> View and select your local available models.\n" +
                                  "• <b>Download:</b> Pull pre-trained weights directly from Hugging Face repositories.\n" +
                                  "• <b>Transform:</b> Optimize and convert PyTorch (.pt) models into ONNX or ExecuTorch.\n" +
                                  "• <b>Train:</b> Load a normalized CSV, adjust hyper-parameters, and execute training."
                            wrapMode: Text.WordWrap
                            font.pixelSize: 13
                            lineHeight: 1.2
                            color: "#2C3E50"
                        }
                    }
                }

                // 3. ANALYSIS
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: analysisColumn.height + 20
                    color: "#F8F9FA"
                    border.color: "#E2E8F0"
                    border.width: 1
                    radius: 6

                    ColumnLayout {
                        id: analysisColumn
                        anchors.top: parent.top
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.margins: 12
                        spacing: 6

                        Text {
                            text: "3. Statistical Analysis"
                            font.pixelSize: 14
                            font.bold: true
                            color: "#2980B9"
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "Click <b>Analysis</b> in the sidebar and navigate via the inner icons:\n" +
                                  "• <b>Records (Compass):</b> Filter tabular survey data and export to CSV or JSON.\n" +
                                  "• <b>Graphics (Chart):</b> Run analytics to plot disease frequency graphs.\n" +
                                  "• <b>Reports (Folder):</b> View saved records, review metrics, and print or export to PDF."
                            wrapMode: Text.WordWrap
                            font.pixelSize: 13
                            lineHeight: 1.2
                            color: "#2C3E50"
                        }
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#EAEDED"
        }

        // Footer Section
        RowLayout {
            Layout.fillWidth: true

            ColumnLayout {
                spacing: 2
                Text {
                    text: "© 2026 PlantDoctor Systems Project. All rights reserved."
                    font.pixelSize: 11
                    color: "#95A5A6"
                }
            }

            Button {
                text: "Close"
                Layout.alignment: Qt.AlignRight
                onClicked: aboutWindow.close()
            }
        }
    }
}