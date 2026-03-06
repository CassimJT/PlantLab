import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    id: propertyPage

    property int totalImages: fileController?.imageCount || 0
    property bool hasImages: totalImages > 0

    background: Rectangle {
        color: "#ffffff"
    }
    BusyIndicator {
        id: busyIndicator
        visible: DatasetProcessor.isProcessing
        anchors.centerIn: parent
        z:5
    }

    ScrollView {
        anchors.fill: parent
        clip: true
        contentWidth: availableWidth
        padding: 10

        ColumnLayout {
            width: parent.width
            spacing: 16
            anchors.margins: 16

            // ===== DATASET INFO =====
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 60
                color: "#f8fafc"
                radius: 6

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Label {
                            text: "Dataset"
                            font.bold: true
                            color: "#0f172a"
                        }

                        Label {
                            text: hasImages ? `${totalImages} images loaded` : "No images loaded"
                            color: hasImages ? "#16a34a" : "#64748b"
                            font.pixelSize: 12
                        }
                    }

                    Rectangle {
                        Layout.preferredHeight: 60
                        Layout.preferredWidth: 60
                        radius: 30
                        color: hasImages ? "#22c55e" : "#e2e8f0"
                        Layout.alignment: Qt.AlignVCenter

                        Label {
                            anchors.centerIn: parent
                            text: totalImages
                            color: "#ffffff"
                            font.bold: true
                            visible: hasImages
                        }
                    }
                }
            }

            // ===== NORMALIZATION SETTINGS =====
            GroupBox {
                Layout.fillWidth: true
                title: "Normalization"
                enabled: !DatasetProcessor.isProcessing && hasImages

                ColumnLayout {
                    width: parent.width
                    spacing: 16

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Label {
                            text: "Target size:"
                            color: "#334155"
                            Layout.preferredWidth: 80
                        }

                        TextField {
                            id: sizeInput
                            Layout.fillWidth: true
                            placeholderText: "224"
                            validator: IntValidator { bottom: 16; top: 1024 }
                            text: "224"
                            horizontalAlignment: TextInput.AlignHCenter
                            enabled: !DatasetProcessor.isProcessing
                        }

                        Label {
                            text: "px"
                            color: "#64748b"
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true

                        Label {
                            text: "Color mode:"
                            color: "#334155"
                            Layout.preferredWidth: 80
                        }

                        ComboBox {
                            id: colorModeCombo
                            Layout.fillWidth: true
                            model: ["RGB", "Grayscale"]
                            enabled: !DatasetProcessor.isProcessing
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true

                        Label {
                            text: "Normalize:"
                            color: "#334155"
                            Layout.preferredWidth: 80
                        }

                        ComboBox {
                            id: normCombo
                            Layout.fillWidth: true
                            model: [
                                "None (0-255)",
                                "Scale (0-1)",
                                "Standardize (mean=0, std=1)"
                            ]
                            enabled: !DatasetProcessor.isProcessing
                        }
                    }

                    Button {
                        Layout.fillWidth: true
                        Layout.topMargin: 8
                        text: DatasetProcessor.isProcessing ? "Processing..." : "Apply to All Images"
                        enabled: hasImages && !DatasetProcessor.isProcessing

                        onClicked: {
                            var dirPath = fileController ? fileController.rootPath : ""

                            if (!dirPath) {
                                statusMessage.text = "Please select a folder first"
                                statusMessage.color = "#f44336"
                                return
                            }

                            var fileName = "normalized_" +
                                    (colorModeCombo.currentIndex === 1 ? "gray_" : "rgb_") +
                                    sizeInput.text + "px"

                            DatasetProcessor.applyNormalization(
                                        parseInt(sizeInput.text) || 224,
                                        colorModeCombo.currentIndex === 1,
                                        normCombo.currentText,
                                        dirPath,
                                        fileName
                                        )
                        }
                    }
                }
            }

            // ===== EXPORT SETTINGS =====
            GroupBox {
                Layout.fillWidth: true
                title: "Export Dataset"
                enabled: !DatasetProcessor.isProcessing && hasImages

                ColumnLayout {
                    width: parent.width
                    spacing: 16

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 30
                        color: "#f0f0f0"
                        radius: 4
                        visible: true

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 5

                            Label {
                                text: DatasetProcessor.getLastNormalizedFolderName() !== ""
                                      ? DatasetProcessor.getLastNormalizedFolderName()
                                      : "Original dataset"
                                color: "#666666"
                                font.pixelSize: 11
                            }

                            Label {
                                text: DatasetProcessor.getLastNormalizedFolderName()
                                color: "#2196F3"
                                font.bold: true
                                font.pixelSize: 11
                                elide: Text.ElideMiddle
                                Layout.fillWidth: true
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true

                        Label {
                            text: "Format:"
                            color: "#334155"
                            Layout.preferredWidth: 80
                        }

                        ComboBox {
                            id: formatCombo
                            Layout.fillWidth: true
                            model: ["CSV with paths", "CSV with metadata", "JSON"]
                            enabled: !DatasetProcessor.isProcessing
                        }
                    }

                    Button {
                        Layout.fillWidth: true
                        Layout.topMargin: 8
                        text: DatasetProcessor.isProcessing ? "Processing..." : "Export Dataset"

                        enabled: hasImages &&
                                 !DatasetProcessor.isProcessing


                        onClicked: {
                            var folderToExport = DatasetProcessor.getLastNormalizedFolder()

                            if (!folderToExport || folderToExport === "") {
                                folderToExport = fileController.rootPath
                            }

                            DatasetProcessor.exportDataset(
                                        formatCombo.currentText,
                                        folderToExport
                                        )
                        }
                    }
                }
            }

            // ===== STATUS MESSAGE =====
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 50
                color: "#f1f5f9"
                radius: 4

                Label {
                    id: statusMessage
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: 10

                    text: hasImages
                          ? "Ready to process " + totalImages + " images"
                          : "No images loaded"

                    color: hasImages ? "#334155" : "#64748b"
                    font.pixelSize: 12

                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideRight
                    wrapMode: Text.NoWrap
                }
            }

            Label {
                Layout.fillWidth: true
                text: "Default save location: " + (DatasetProcessor ? DatasetProcessor.getDefaultExportPath() : "")
                color: "#64748b"
                font.pixelSize: 10
                visible: DatasetProcessor ? true : false
            }
        }
    }

    Connections {
        target: DatasetProcessor

        function onNormalizationStarted(message) {
            console.log("Normalization started:", message)
            statusMessage.text = message
            statusMessage.color = "#334155"
        }

        function onNormalizationCompleted(message) {
            console.log("Normalization completed:", message)
            statusMessage.text = message
            statusMessage.color = "#16a34a"
        }

        function onNormalizationFailed(message) {
            console.log("Normalization failed:", message)
            statusMessage.text = "Error: " + message
            statusMessage.color = "#f44336"
        }

        function onExportStarted(format, destination) {
            console.log("Export started:", format, destination)
            statusMessage.text = `Exporting to ${format}...`
            statusMessage.color = "#334155"
        }

        function onExportCompleted(message) {
            console.log("Export completed:", message)
            // open popup
        }

        function onExportFailed(message) {
            console.log("Export failed:", message)
            statusMessage.text = "Error: " + message
            statusMessage.color = "#f44336"
        }
    }

    Binding {
        target: propertyPage
        property: "enabled"
        value: !DatasetProcessor.isProcessing
    }
}
