import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts
import QtQuick.Dialogs

Page {
    id: root
    // Properties for model download
    property string modelId: ""
    property string downloadPath: StandardPaths.writableLocation(StandardPaths.DownloadLocation)
    property var selectedFrameworks: []
    property bool downloading: false
    property double downloadProgress: 0
    property string statusMessage: "Ready"

    ColumnLayout {
        spacing: 15
        anchors {
            left: parent.left
            right: parent.right
            rightMargin: 20
            leftMargin: 20
        }

        // Model ID Input Section
        GroupBox {
            title: "Model Information"
            Layout.fillWidth: true

            ColumnLayout {
                width: parent.width
                spacing: 10

                Label {
                    text: "Hugging Face Model ID:"
                    font.bold: true
                }

                TextField {
                    id: modelIdField
                    Layout.fillWidth: true
                    placeholderText: "e.g., google/flan-t5-base, openai/whisper-large-v3"
                    onTextChanged: {
                       //..
                    }
                }

            }
        }

        // Framework Selection
        GroupBox {
            title: "Select Frameworks"
            Layout.fillWidth: true

            GridLayout {
                width: parent.width
                columns: 3
                columnSpacing: 20
                rowSpacing: 10

                CheckBox {
                    id: pytorchCheck
                    text: "PyTorch"
                    checked: true
                    onCheckedChanged: updateSelectedFrameworks()
                }

                CheckBox {
                    id: libtorchCheck
                    text: "LibTorch"
                    onCheckedChanged: updateSelectedFrameworks()
                }

                CheckBox {
                    id: opencvCheck
                    text: "OpenCV"
                    onCheckedChanged: updateSelectedFrameworks()
                }

                CheckBox {
                    id: tensorflowCheck
                    text: "TensorFlow"
                    onCheckedChanged: updateSelectedFrameworks()
                }

                CheckBox {
                    id: onnxCheck
                    text: "ONNX"
                    onCheckedChanged: updateSelectedFrameworks()
                }

                CheckBox {
                    id: allFrameworksCheck
                    text: "All Frameworks"
                    onCheckedChanged: {
                        if (checked) {
                            pytorchCheck.checked = true
                            libtorchCheck.checked = true
                            opencvCheck.checked = true
                            tensorflowCheck.checked = true
                            onnxCheck.checked = true
                        }
                    }
                }
            }
        }

        // Download Options
        GroupBox {
            title: "Download Options"
            Layout.fillWidth: true

            RowLayout {
                width: parent.width
                spacing: 20

                // Download Path Selection
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5

                    Label {
                        text: "Download Location:"
                        font.bold: true
                    }

                    RowLayout {
                        TextField {
                            id: pathField
                            Layout.fillWidth: true
                            text: downloadPath
                            readOnly: true
                        }

                        Button {
                            text: "Browse"
                            onClicked: folderDialog.open()
                        }
                    }
                }

                // Version Selection
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 5

                    Label {
                        text: "Model Version:"
                        font.bold: true
                    }

                    ComboBox {
                        id: versionCombo
                        Layout.fillWidth: true
                        Layout.preferredHeight: pathField.height
                        model: ["Latest", "Main", "Specific Commit..."]
                        onCurrentIndexChanged: {
                            if (currentIndex === 2) {
                                commitHashField.visible = true
                            } else {
                                commitHashField.visible = false
                            }
                        }
                    }

                    TextField {
                        id: commitHashField
                        Layout.fillWidth: true
                        placeholderText: "Enter commit hash"
                        visible: false
                    }
                }
            }
        }

        // Progress and Status
        GroupBox {
            title: "Download Progress"
            Layout.fillWidth: true

            ColumnLayout {
                width: parent.width
                spacing: 10

                ProgressBar {
                    id: progressBar
                    Layout.fillWidth: true
                    value: downloadProgress
                    visible: downloading
                }

                Label {
                    id: statusLabel
                    text: statusMessage
                    Layout.fillWidth: true
                    wrapMode: Text.Wrap

                    // Color based on status
                    color: {
                        if (statusMessage.includes("Error")) return "red"
                        if (statusMessage.includes("completed")) return "green"
                        if (downloading) return "blue"
                        return "black"
                    }
                }

                // Additional Info
                Label {
                    text: "Model ID: " + (modelId || "Not specified")
                    visible: modelId
                    font.italic: true
                }

                Label {
                    text: "Selected Frameworks: " + selectedFrameworks.join(", ")
                    visible: selectedFrameworks.length > 0
                    font.italic: true
                }
            }
        }

        // Action Buttons
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 20

            Button {
                text: downloading ? "Downloading..." : "Download Model"
                enabled: !downloading && modelIdField.text.trim() !== ""

                contentItem: Row {
                    spacing: 10
                    Text { text: parent.parent.text; color: parent.parent.enabled ? "white" : "gray" }
                    BusyIndicator {
                        width: 20
                        height: 20
                        running: downloading
                        visible: downloading
                    }
                }

                onClicked: {
                    //
                }

            }

            Button {
                text: "Clear"
                onClicked: {
                    modelIdField.text = ""
                    selectedFrameworks = []
                    pytorchCheck.checked = false
                    libtorchCheck.checked = false
                    opencvCheck.checked = false
                    tensorflowCheck.checked = false
                    onnxCheck.checked = false
                    allFrameworksCheck.checked = false
                    statusMessage = "Ready"
                    downloadProgress = 0
                }
            }

            Button {
                text: "Open Download Folder"
                onClicked: Qt.openUrlExternally("file:///" + downloadPath)
                enabled: downloadPath !== ""
            }
        }
    }

    function updateSelectedFrameworks() {
        selectedFrameworks = []
        if (pytorchCheck.checked) selectedFrameworks.push("PyTorch")
        if (libtorchCheck.checked) selectedFrameworks.push("LibTorch")
        if (opencvCheck.checked) selectedFrameworks.push("OpenCV")
        if (tensorflowCheck.checked) selectedFrameworks.push("TensorFlow")
        if (onnxCheck.checked) selectedFrameworks.push("ONNX")
    }

    // Folder Dialog
    FolderDialog {
        id: folderDialog
        title: "Select Download Folder"
        currentFolder: downloadPath
        onAccepted: {
            downloadPath = folderDialog.folder
            pathField.text = downloadPath
        }
    }

    // Completion Dialog
    MessageDialog {
        id: downloadCompleteDialog
        title: "Download Complete"
        text: "Model '" + modelId + "' has been successfully downloaded!"
        informativeText: "Frameworks: " + selectedFrameworks.join(", ") +
                        "\n\nLocation: " + downloadPath
    }

    // Initialize
    Component.onCompleted: {
        updateSelectedFrameworks()
    }
}
