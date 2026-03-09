import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts
import QtQuick.Dialogs

Page {
    id: root
    // Properties for model download
    property string modelId: ""
    property string downloadPath: ModelDownloader ? ModelDownloader.downloadLocation : StandardPaths.writableLocation(StandardPaths.DownloadLocation)
    property string selectedFramework: "PyTorch"  // Changed to string, not array
    property bool downloading: ModelDownloader ? ModelDownloader.isDownloading : false
    property double downloadProgress: ModelDownloader ? ModelDownloader.downloadProgress : 0
    property string statusMessage: ModelDownloader ? ModelDownloader.statusMessage : "Ready"

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
                spacing: 5

                Label {
                    text: "Hugging Face Model ID:"
                    font.bold: true
                }

                TextField {
                    id: modelIdField
                    Layout.fillWidth: true
                    placeholderText: "e.g., google/flan-t5-base, openai/whisper-large-v3"
                    onTextChanged: {
                        root.modelId = text
                    }
                }
            }
        }

        // Framework Selection - Single selection with RadioButton in GridLayout
        GroupBox {
            title: "Select Framework "
            Layout.fillWidth: true

            GridLayout {
                //width: parent.width
                columns: 3
                columnSpacing: 24
                rowSpacing: 8
                Layout.fillWidth: true

                RadioButton {
                    id: pytorchRadio
                    text: "PyTorch (.pt)"
                    checked: true
                    onCheckedChanged: if (checked) updateSelectedFramework("PyTorch")
                }

                RadioButton {
                    id: libtorchRadio
                    text: "LibTorch (C++)"
                    onCheckedChanged: if (checked) updateSelectedFramework("LibTorch")
                }

                RadioButton {
                    id: opencvRadio
                    text: "OpenCV (DNN)"
                    onCheckedChanged: if (checked) updateSelectedFramework("OpenCV")
                }

                RadioButton {
                    id: tensorflowRadio
                    text: "TensorFlow"
                    onCheckedChanged: if (checked) updateSelectedFramework("TensorFlow")
                }

                RadioButton {
                    id: onnxRadio
                    text: "ONNX"
                    onCheckedChanged: if (checked) updateSelectedFramework("ONNX")
                }

                RadioButton {
                    id: executorchRadio
                    text: "Executorch (.pte)"
                    onCheckedChanged: if (checked) updateSelectedFramework("Executorch")
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
                            placeholderText: "Document/plantlab/models"
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
                                commitHashField.text = ""
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
                spacing: 5

                RowLayout {
                    Layout.preferredWidth: parent.width
                    spacing: 2
                    ProgressBar {
                        id: progressBar
                        Layout.fillWidth: true
                        from: 0
                        to: 100
                        value: downloadProgress
                        visible: downloading
                        BusyIndicator {
                            width: 20
                            height: width
                            anchors.centerIn: parent
                            visible: downloading
                            running: downloading
                            z: 10
                        }
                    }
                    Label {
                        id: percentage
                        text: progressBar.value + "%"
                        color: "green"
                        visible: downloading
                        font.bold: true
                    }
                }
                Label {
                    id: statusLabel
                    text: statusMessage
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    elide: Text.ElideRight
                    maximumLineCount: 2

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
                    text: "Selected Framework: " + selectedFramework
                    visible: selectedFramework !== ""
                    font.italic: true
                }
            }
        }

        // Action Buttons
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 20

            Button {
                text: downloading ? "Cancel Download" : "Download Model"
                enabled: !downloading ? modelIdField.text.trim() !== "" : true

                onClicked: {
                    if (downloading) {
                        // Cancel download
                        if (ModelDownloader) {
                            ModelDownloader.cancelDownload()
                        }
                    } else {
                        // Start download
                        if (!ModelDownloader) {
                            console.error("ModelDownloader not available")
                            return
                        }

                        // Get the branch/version
                        var branch = "Latest"
                        var commitHash = ""

                        if (versionCombo.currentIndex === 1) {
                            branch = "Main"
                        } else if (versionCombo.currentIndex === 2) {
                            branch = "Specific Commit"
                            commitHash = commitHashField.text.trim()
                        }

                        // Update download location if changed
                        if (downloadPath !== ModelDownloader.downloadLocation) {
                            ModelDownloader.setDownloadLocation(downloadPath)
                        }

                        // Call downloadModel with the parameters (single framework as list with one item)
                        ModelDownloader.downloadModel(
                                    modelIdField.text.trim(),
                                    [selectedFramework],  // Convert to list with single item
                                    branch,
                                    commitHash
                                    )
                    }
                }
            }

            Button {
                text: "Clear"
                onClicked: {
                    modelIdField.text = ""
                    pytorchRadio.checked = true  // Reset to default
                    updateSelectedFramework("PyTorch")
                    versionCombo.currentIndex = 0
                    commitHashField.visible = false
                    commitHashField.text = ""
                    statusMessage = "Ready"
                    downloadProgress = 0

                    if (downloading && ModelDownloader) {
                        ModelDownloader.cancelDownload()
                    }
                }
            }

            Button {
                text: "Open Download Folder"
                onClicked: Qt.openUrlExternally("file:///" + downloadPath)
                enabled: downloadPath !== ""
            }
        }
    }

    // Update selected framework (single selection)
    function updateSelectedFramework(framework) {
        if (selectedFramework !== framework) {
            selectedFramework = framework
            console.log("Selected framework changed to:", selectedFramework)

            // Optional: You could emit a signal to backend if needed
            // frameworksChanged(selectedFramework)
        }
    }

    // Folder Dialog
    FolderDialog {
        id: folderDialog
        title: "Select Download Folder"
        currentFolder: downloadPath
        onAccepted: {
            downloadPath = folderDialog.currentFolder.toString()
            // Remove file:// prefix if present
            if (downloadPath.startsWith("file://")) {
                downloadPath = downloadPath.substring(7)
            }
            pathField.text = downloadPath

            // Update ModelDownloader location
            if (ModelDownloader) {
                ModelDownloader.setDownloadLocation(downloadPath)
            }
        }
    }

    // Completion Dialog
    MessageDialog {
        id: downloadCompleteDialog
        title: "Download Complete"
        text: "Model '" + modelId + "' has been successfully downloaded!"
        informativeText: "Framework: " + selectedFramework +
                         "\n\nLocation: " + downloadPath
    }

    // Connections to ModelDownloader
    Connections {
        target: ModelDownloader
        enabled: typeof ModelDownloader !== "undefined"

        function onDownloadProgressChanged(progress) {
            root.downloadProgress = progress
        }

        function onStatusMessageChanged(message) {
            root.statusMessage = message
        }

        function onIsDownloadingChanged() {
            root.downloading = ModelDownloader.isDownloading
        }

        function onDownloadFinished(path) {
            //downloadCompleteDialog.open()
            downloadCompleteDialog.text = "Model '" + modelIdField.text + "' has been successfully downloaded!"
            downloadCompleteDialog.informativeText = "Framework: " + selectedFramework +
                    "\n\nLocation: " + path
        }

        function onDownloadErrorOccurred(error) {
            root.statusMessage = "Error: " + error
        }

        function onDownloadLocationChanged(location) {
            root.downloadPath = location
            pathField.text = location
        }
    }

    // Initialize
    Component.onCompleted: {
        // Set default framework
        updateSelectedFramework("PyTorch")

        if (ModelDownloader) {
            pathField.text = ModelDownloader.downloadLocation
            downloadPath = ModelDownloader.downloadLocation
            downloading = ModelDownloader.isDownloading
            downloadProgress = ModelDownloader.downloadProgress
            statusMessage = ModelDownloader.statusMessage
        }
    }
}
