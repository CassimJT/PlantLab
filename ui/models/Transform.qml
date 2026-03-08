import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs

Page {
    id: root

    // Properties
    property string modelSource: ""           // HF repo ID or local .pt path
    property string outputPath: ModelTransformer ? ModelTransformer.outputLocation : StandardPaths.writableLocation(StandardPaths.DownloadLocation) + "/plantlab/models"
    property string selectedFramework: "ONNX"
    property bool transforming: ModelTransformer ? ModelTransformer.isTransforming : false
    property double progressValue: ModelTransformer ? ModelTransformer.progressValue : 0
    property string statusMessage: ModelTransformer ? ModelTransformer.statusMessage : "Ready to transform model"

    ColumnLayout {
        spacing: 15
        anchors {
            left: parent.left
            right: parent.right
            rightMargin: 20
            leftMargin: 20
        }

        // ── Model Input Section ────────────────────────────────────────
        GroupBox {
            title: "Model Source"
            Layout.fillWidth: true

            ColumnLayout {
                width: parent.width
                spacing: 8

                Label {
                    text: "Hugging Face Repo ID or local .pt file:"
                    font.bold: true
                }

                RowLayout {
                    TextField {
                        id: modelIdField
                        Layout.fillWidth: true
                        placeholderText: "e.g. Murasan/beetle-detection-yolov8   or   /path/to/best.pt"
                        text: modelSource
                        onTextChanged: modelSource = text.trim()
                    }

                    Button {
                        text: "Browse .pt"
                        onClicked: fileDialog.open()
                    }
                }

                Label {
                    text: "Note: Most conversions start from PyTorch (.pt) → ONNX / ExecuTorch / LibTorch"
                    font.italic: true
                    color: "#666"
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
        }

        // ── Source Framework ───────────────────────────────────────────
        GroupBox {
            title: "Source Framework"
            Layout.fillWidth: true

            ComboBox {
                id: sourceFrameworkCombo
                width: parent.width * .30
                model: ["PyTorch (.pt)", "TensorFlow (.pb)", "ONNX (.onnx)"]
                currentIndex: 0
                Layout.fillWidth: true
                onCurrentIndexChanged: {
                    // Could update backend
                }
            }
        }

        // ── Target Framework Selection ─────────────────────────────────
        GroupBox {
            title: "Target Framework (Single Selection)"
            Layout.fillWidth: true

            GridLayout {
                columns: 3
                columnSpacing: 24
                rowSpacing: 8
                Layout.fillWidth: true

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
                    checked: true
                    onCheckedChanged: if (checked) updateSelectedFramework("ONNX")
                }

                RadioButton {
                    id: executorchRadio
                    text: "ExecuTorch (.pte)"
                    onCheckedChanged: if (checked) updateSelectedFramework("Executorch")
                }
            }
        }

        // ── Output Folder Selection ────────────────────────────────────
        GroupBox {
            title: "Output Folder"
            Layout.fillWidth: true

            RowLayout {
                width: parent.width
                spacing: 12

                TextField {
                    id: pathField
                    Layout.fillWidth: true
                    text: outputPath
                    readOnly: true
                    placeholderText: "Documents/plantlab/models"
                }

                Button {
                    text: "Browse"
                    onClicked: outputFolderDialog.open()
                }
            }
        }

        // ── Progress & Status ──────────────────────────────────────────
        GroupBox {
            title: "Transformation Status"
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
                        value: progressValue
                        visible: transforming

                        BusyIndicator {
                            width: 20
                            height: width
                            anchors.centerIn: parent
                            visible: transforming
                            running: transforming
                            z: 10
                        }
                    }

                    Label {
                        id: percentage
                        text: progressBar.value + "%"
                        color: "green"
                        visible: transforming
                        font.bold: true
                    }
                }

                Label {
                    id: statusLabel
                    text: statusMessage
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap

                    color: {
                        if (statusMessage.includes("Error")) return "red"
                        if (statusMessage.includes("Success") || statusMessage.includes("completed")) return "green"
                        if (transforming) return "blue"
                        return "black"
                    }
                }

                Label {
                    text: "Source: " + (modelSource || "Not set")
                    visible: modelSource !== ""
                    font.italic: true
                    color: "#555"
                }

                Label {
                    text: "Target: " + selectedFramework
                    visible: selectedFramework !== ""
                    font.italic: true
                    color: "#555"
                }
            }
        }

        // ── Action Buttons ─────────────────────────────────────────────
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 24

            Button {
                text: transforming ? "Cancel Transformation" : "Transform Model"
                enabled: !transforming ? modelSource !== "" : true

                onClicked: {
                    if (transforming) {
                        // Cancel transformation
                        if (ModelTransformer) {
                            ModelTransformer.cancelTransformation()
                        }
                    } else {
                        // Start transformation
                        if (!ModelTransformer) {
                            console.error("ModelTransformer not available")
                            return
                        }

                        // Update output path if changed
                        if (outputPath !== ModelTransformer.outputLocation) {
                            ModelTransformer.setOutputLocation(outputPath)
                        }

                        // Call transformModel with parameters
                        ModelTransformer.transformModel(
                            modelSource,
                            sourceFrameworkCombo.currentText.split(" ")[0], // Extract framework name
                            selectedFramework,
                            outputPath
                        )
                    }
                }
            }

            Button {
                text: "Clear"
                onClicked: {
                    modelIdField.text = ""
                    modelSource = ""
                    sourceFrameworkCombo.currentIndex = 0
                    onnxRadio.checked = true
                    updateSelectedFramework("ONNX")
                    outputPath = StandardPaths.writableLocation(StandardPaths.DownloadLocation) + "/plantlab/models"
                    pathField.text = outputPath
                    statusMessage = "Ready to transform model"
                    progressValue = 0

                    if (transforming && ModelTransformer) {
                        ModelTransformer.cancelTransformation()
                    }
                }
            }

            Button {
                text: "Open Output Folder"
                onClicked: Qt.openUrlExternally("file:///" + outputPath)
                enabled: outputPath !== ""
            }
        }
    }

    // ── Functions ──────────────────────────────────────────────────────
    function updateSelectedFramework(framework) {
        if (selectedFramework !== framework) {
            selectedFramework = framework
            console.log("Selected target framework changed to:", selectedFramework)
        }
    }

    // ── Dialogs ────────────────────────────────────────────────────────
    FileDialog {
        id: fileDialog
        title: "Select PyTorch model file (.pt)"
        nameFilters: ["PyTorch models (*.pt)", "All files (*)"]
        fileMode: FileDialog.OpenFile
        onAccepted: {
            var filePath = fileDialog.selectedFile.toString()
            if (filePath.startsWith("file://")) {
                filePath = filePath.substring(7)
            }
            modelSource = filePath
            modelIdField.text = modelSource
        }
    }

    FolderDialog {
        id: outputFolderDialog
        title: "Select Output Folder"
        currentFolder: outputPath
        onAccepted: {
            var folder = outputFolderDialog.currentFolder.toString()
            if (folder.startsWith("file://")) {
                folder = folder.substring(7)
            }
            outputPath = folder
            pathField.text = outputPath

            // Update ModelTransformer location
            if (ModelTransformer) {
                ModelTransformer.setOutputLocation(outputPath)
            }
        }
    }

    // Completion Dialog
    MessageDialog {
        id: transformCompleteDialog
        title: "Transformation Complete"
        text: "Model has been successfully transformed!"
        informativeText: "Source: " + modelSource + "\nTarget: " + selectedFramework + "\n\nLocation: " + outputPath
    }

    // ── Connections to ModelTransformer ─────────────────────────────────
    Connections {
        target: ModelTransformer
        enabled: typeof ModelTransformer !== "undefined"

        function onProgressChanged(progress) {
            root.progressValue = progress
        }

        function onStatusMessageChanged(message) {
            root.statusMessage = message
        }

        function onIsTransformingChanged() {
            root.transforming = ModelTransformer.isTransforming
        }

        function onTransformationFinished(outputPath) {
            transformCompleteDialog.open()
            transformCompleteDialog.informativeText = "Source: " + modelSource + "\nTarget: " + selectedFramework + "\n\nLocation: " + outputPath
        }

        function onTransformationError(error) {
            root.statusMessage = "Error: " + error
        }

        function onOutputLocationChanged(location) {
            root.outputPath = location
            pathField.text = location
        }
    }

    // ── Initialization ─────────────────────────────────────────────────
    Component.onCompleted: {
        updateSelectedFramework("ONNX")

        if (ModelTransformer) {
            pathField.text = ModelTransformer.outputLocation
            outputPath = ModelTransformer.outputLocation
            transforming = ModelTransformer.isTransforming
            progressValue = ModelTransformer.progressValue
            statusMessage = ModelTransformer.statusMessage
        }
    }
}
