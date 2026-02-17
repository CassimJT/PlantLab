import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    id: propertyPage

    // Input properties
    property int totalImages: fileController?.imageCount || 0
    property bool hasImages: totalImages > 0

    // Output signals
    signal applyNormalization(int targetSize, bool grayscale, string normalization)
    signal exportDataset(string format, string destination)

    background: Rectangle {
        color: "#ffffff"
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
                        width: 40
                        height: 40
                        radius: 20
                        color: hasImages ? "#22c55e" : "#e2e8f0"

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

                ColumnLayout {
                    width: parent.width
                    spacing: 16

                    // Target size
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
                        }

                        Label {
                            text: "px"
                            color: "#64748b"
                        }
                    }

                    // Color mode
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
                        }
                    }

                    // Normalization type
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
                                "Standardize (mean=0, std=1)",
                                "Custom range"
                            ]
                        }
                    }

                    // Apply button
                    Button {
                        Layout.fillWidth: true
                        Layout.topMargin: 8
                        text: "Apply to All Images"
                        enabled: hasImages


                        contentItem: Text {
                            text: parent.text
                            color: "#ffffff"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.bold: true
                        }

                        onClicked: {
                            applyNormalization(
                                parseInt(sizeInput.text) || 224,
                                colorModeCombo.currentIndex === 1,  // true for grayscale
                                normCombo.currentText
                            )
                        }
                    }
                }
            }

            // ===== EXPORT SETTINGS =====
            GroupBox {
                Layout.fillWidth: true
                title: "Export Dataset"

                ColumnLayout {
                    width: parent.width
                    spacing: 16

                    // Export format
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
                            model: ["CSV with paths", "CSV with metadata", "JSON", "HDF5"]
                        }
                    }

                    // Destination
                    RowLayout {
                        Layout.fillWidth: true

                        Label {
                            text: "Save to:"
                            color: "#334155"
                            Layout.preferredWidth: 80
                        }

                        TextField {
                            id: destInput
                            Layout.fillWidth: true
                            placeholderText: "./dataset/"
                            text: "./normalized_dataset/"
                        }
                    }

                    // Export button
                    Button {
                        Layout.fillWidth: true
                        Layout.topMargin: 8
                        text: "Export Dataset"
                        enabled: hasImages

                        contentItem: Text {
                            text: parent.text
                            color: "#ffffff"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.bold: true
                        }

                        onClicked: {
                            exportDataset(
                                formatCombo.currentText,
                                destInput.text
                            )
                        }
                    }
                }
            }

            // ===== STATUS MESSAGE =====
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 40
                color: "#f1f5f9"
                radius: 4
                visible: hasImages

                Label {
                    anchors.centerIn: parent
                    text: "Ready to process " + totalImages + " images"
                    color: "#334155"
                    font.pixelSize: 12
                }
            }
        }
    }
}
