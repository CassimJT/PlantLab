import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts
import QtQuick.Dialogs

Page {
    id: root
    title: "Model Training"

    // Properties
    property string datasetPath: ModelTrainer ? ModelTrainer.datasetPath : ""
    property bool training: ModelTrainer ? ModelTrainer.isTrainingInProgress : false
    property double progressValue: ModelTrainer ? ModelTrainer.trainingProgress : 0
    property string statusMessage: ModelTrainer ? ModelTrainer.statusMessage : "Ready to train model"
    property double currentLoss: ModelTrainer ? ModelTrainer.currentLoss : 0
    property double currentAccuracy: ModelTrainer ? ModelTrainer.currentAccuracy : 0

    ColumnLayout {
        spacing: 15
        anchors {
            left: parent.left
            right: parent.right
            margins: 20
        }

        // ================= DATASET =================
        GroupBox {
            title: "1. Dataset"
            Layout.fillWidth: true

            RowLayout {
                spacing: 10
                width: parent.width

                TextField {
                    id: csvPath
                    Layout.fillWidth: true
                    placeholderText: "Select normalized CSV file / a path to dataset..."
                    readOnly: true
                    text: datasetPath

                    // Update when ModelTrainer dataset changes
                    Connections {
                        target: ModelTrainer
                        function onDataSetPathChanged() {
                            csvPath.text = ModelTrainer.datasetPath
                        }
                    }
                }

                Button {
                    text: "Browse"
                    onClicked: fileDialog.open()
                }
            }
        }

        // ================= PARAMETERS =================
        GroupBox {
            title: "2. Training Parameters"
            Layout.fillWidth: true

            GridLayout {
                columns: 2
                columnSpacing: 12
                rowSpacing: 10
                Layout.fillWidth: true

                Label { text: "Model Type:" }
                ComboBox {
                    id: modelType
                    Layout.preferredWidth: parent.width * 0.7
                    model: ["MobileNetV3-Small (fastest)",
                        "MobileNetV3-Large (more accurate)",
                        "SSDLite-MobileNetV3 (for detection)"]
                    currentIndex: 0
                }

                Label { text: "Epochs:" }
                SpinBox {
                    id: epochs
                    from: 1
                    to: 100
                    value: ModelTrainer ? ModelTrainer.epoch : 15

                    onValueChanged: {
                        if (ModelTrainer) {
                            ModelTrainer.setEpoch(value)
                        }
                    }
                }

                Label { text: "Batch Size:" }
                SpinBox {
                    id: batchSize
                    from: 1
                    to: 128
                    value: ModelTrainer ? ModelTrainer.batchSize : 8

                    onValueChanged: {
                        if (ModelTrainer) {
                            ModelTrainer.setBatchSize(value)
                        }
                    }
                }

                Label { text: "Learning Rate:" }
                TextField {
                    id: lr
                    text: ModelTrainer ? ModelTrainer.learningRate : "0.0001"
                    validator: DoubleValidator { bottom: 0.000001 }

                    onTextChanged: {
                        if (ModelTrainer) {
                            ModelTrainer.setLearningRate(parseFloat(text))
                        }
                    }
                }

                Label { text: "Train/Test Split:" }
                Slider {
                    id: split
                    from: 0.5
                    to: 0.95
                    value: ModelTrainer ? ModelTrainer.trainTestSplit / 100 : 0.8

                    onValueChanged: {
                        if (ModelTrainer) {
                            ModelTrainer.setTrainTestSplit(Math.round(value * 100))
                        }
                    }
                }

                Label {
                    text: Math.round(split.value * 100) + "% train"
                }
            }
        }

        // ================= PROGRESS & STATUS =================
        GroupBox {
            title: "3. Training Status"
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
                        visible: training

                        BusyIndicator {
                            width: 20
                            height: width
                            anchors.centerIn: parent
                            visible: training
                            running: training
                            z: 10
                        }
                    }

                    Label {
                        id: percentage
                        text: progressBar.value + "%"
                        color: "green"
                        visible: training
                        font.bold: true
                    }
                }

                // Status message (same pattern as Transform page)
                Label {
                    id: statusLabel
                    text: statusMessage
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    elide: Text.ElideRight
                    maximumLineCount: 2

                    color: {
                        if (statusMessage.includes("Error") || statusMessage.includes("failed")) return "red"
                        if (statusMessage.includes("Success") || statusMessage.includes("completed")) return "green"
                        if (training) return "blue"
                        return "black"
                    }
                }

                // Metrics display
                RowLayout {
                    Layout.fillWidth: true
                    visible: training || currentLoss > 0 || currentAccuracy > 0

                    Label {
                        text: "Loss: " + (currentLoss ? currentLoss.toFixed(4) : "--")
                        color: "#555"
                        font.italic: true
                    }

                    Label {
                        text: "Accuracy: " + (currentAccuracy ? (currentAccuracy * 100).toFixed(1) + "%" : "--")
                        color: "#555"
                        font.italic: true
                    }
                }

                // Info labels
                Label {
                    text: "Dataset: " + (datasetPath ? (datasetPath.length > 40 ? "..." + datasetPath.substring(datasetPath.length - 40) : datasetPath) : "Not set")
                    visible: datasetPath !== ""
                    font.italic: true
                    color: "#555"
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }

                Label {
                    text: "Model: " + (modelType.currentText.split(" ")[0] || "Not selected")
                    font.italic: true
                    color: "#555"
                }
            }
        }

        // ================= TRAIN CONTROL =================
        GroupBox {
            title: "4. Training Control"
            Layout.fillWidth: true

            RowLayout {
                spacing: 12

                Button {
                    text: training ? "Stop Training" : "Start Training"
                    enabled: !training ? csvPath.text.length > 0 : true
                    highlighted: !training

                    onClicked: {
                        if (ModelTrainer) {
                            if (training) {
                                ModelTrainer.stopTraining()
                            } else {
                                ModelTrainer.setDatasetPath(csvPath.text)
                                ModelTrainer.startTraining(modelType.currentText)
                            }
                        }
                    }
                }

                Button {
                    text: "Pause"
                    enabled: training
                    visible: training

                    onClicked: {
                        if (ModelTrainer) {
                            ModelTrainer.pauseTraining()
                        }
                    }
                }

                Button {
                    text: "Resume"
                    enabled: training
                    visible: training

                    onClicked: {
                        if (ModelTrainer) {
                            ModelTrainer.resumeTraining()
                        }
                    }
                }

                Button {
                    text: "Clear"
                    onClicked: {
                        csvPath.text = ""
                        modelType.currentIndex = 0
                        epochs.value = 15
                        batchSize.value = 8
                        lr.text = "0.0001"
                        split.value = 0.8
                        statusMessage = "Ready to train model"
                        progressValue = 0

                        if (training && ModelTrainer) {
                            ModelTrainer.stopTraining()
                        }
                    }
                }

                Button {
                    text: "Open Dataset Folder"
                    onClicked: {
                        if (datasetPath) {
                            var folder = datasetPath.substring(0, datasetPath.lastIndexOf("/"))
                            Qt.openUrlExternally("file:///" + folder)
                        }
                    }
                    enabled: datasetPath !== ""
                }
            }
        }

        // ================= RESULTS =================
        GroupBox {
            id: resultsBox
            title: "5. Results"
            Layout.fillWidth: true
            visible: !training && progressValue >= 100

            ColumnLayout {
                spacing: 6

                Label {
                    id: accuracyResult
                    text: "Accuracy: --"
                    color: "#2e7d32"
                    font.bold: true
                }
                Label {
                    id: precisionResult
                    text: "Precision: --"
                }
                Label {
                    id: recallResult
                    text: "Recall: --"
                }
                Label {
                    id: f1Result
                    text: "F1 Score: --"
                }

                Button {
                    text: "Export Model"
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: {
                        // Handle model export
                        console.log("Export model clicked")
                    }
                }
            }
        }
    }

    FileDialog {
        id: fileDialog
        title: "Select Training CSV"
        nameFilters: ["CSV files (*.csv)"]
        onAccepted: {
            var filePath = fileDialog.selectedFile.toString()
            if (filePath.startsWith("file://")) {
                filePath = filePath.substring(7)
            }
            csvPath.text = filePath
            if (ModelTrainer) {
                ModelTrainer.setDatasetPath(filePath)
            }
        }
    }

    // ====================================================
    // Connections to ModelTrainer
    // ====================================================
    Connections {
        target: ModelTrainer
        enabled: typeof ModelTrainer !== "undefined"

        // Update properties
        function onTrainingProgressChanged() {
            root.progressValue = ModelTrainer.trainingProgress
        }

        function onStatusMessageChanged() {
            root.statusMessage = ModelTrainer.statusMessage
        }

        function onIsTrainingInProgressChanged() {
            root.training = ModelTrainer.isTrainingInProgress
            if (!root.training && root.progressValue >= 100) {
                // Training completed successfully
                root.statusMessage = "Training completed successfully!"
            }
        }

        function onLossUpdated(loss) {
            root.currentLoss = loss
        }

        function onAccuracyUpdated(accuracy) {
            root.currentAccuracy = accuracy
        }

        // Handle training completion
        function onTrainingCompleted(result) {
            if (result !== "failed") {
                parseResults(result)
            }
        }

        // Handle errors
        function onTrainingError(error) {
            root.statusMessage = "Error: " + error
        }

        // Parse results from training completion
        function parseResults(result) {
            var lines = result.split('\n')
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i]
                if (line.includes("Accuracy:")) {
                    accuracyResult.text = line
                } else if (line.includes("Precision:")) {
                    precisionResult.text = line
                } else if (line.includes("Recall:")) {
                    recallResult.text = line
                } else if (line.includes("F1 Score:")) {
                    f1Result.text = line
                }
            }
        }
    }

    // Initialize from ModelTrainer
    Component.onCompleted: {
        if (typeof ModelTrainer !== "undefined") {
            // Sync UI with current ModelTrainer state
            csvPath.text = ModelTrainer.datasetPath || ""
            epochs.value = ModelTrainer.epoch
            batchSize.value = ModelTrainer.batchSize
            lr.text = ModelTrainer.learningRate.toString()
            split.value = ModelTrainer.trainTestSplit / 100
            root.training = ModelTrainer.isTrainingInProgress
            root.progressValue = ModelTrainer.trainingProgress
            root.statusMessage = ModelTrainer.statusMessage || "Ready to train model"
            root.currentLoss = ModelTrainer.currentLoss || 0
            root.currentAccuracy = ModelTrainer.currentAccuracy || 0
        }
    }
}
