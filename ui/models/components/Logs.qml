import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: logsContainer
    color: "#1e1e1e"
    radius: 4
    border.color: "#333333"

    Layout.fillWidth: true
    Layout.fillHeight: true
    Layout.minimumHeight: 150

    function log(message, type) {
        var timestamp = new Date().toLocaleTimeString()
        var color = "#00ff00" // Default green

        // Set color based on message type
        if (type === "error") color = "#ff5555"      // Red for errors
        else if (type === "success") color = "#55ff55" // Bright green for success
        else if (type === "progress") color = "#ffff55" // Yellow for progress
        else if (type === "info") color = "#55aaff"     // Blue for info
        else if (type === "warning") color = "#ffaa00"  // Orange for warnings

        // Insert colored text using HTML
        logTextArea.insert(logTextArea.length,
            `<font color="${color}">[${timestamp}] ${message}</font><br>`)
        logTextArea.cursorPosition = logTextArea.length
    }

    function clear() {
        logTextArea.text = ""
        log("Logs ready", "info")
    }

    ScrollView {
        anchors.fill: parent
        anchors.margins: 4
        clip: true

        TextArea {
            id: logTextArea
            font.family: "Courier New"
            font.pixelSize: 14
            readOnly: true
            wrapMode: TextArea.Wrap
            textFormat: TextEdit.RichText  // Enable rich text
            background: Rectangle {
                color: "#1e1e1e"
            }

            Component.onCompleted: clear()
        }
    }

    // Direct connections to ModelDownloader (context property)
    Connections {
        target: ModelDownloader
        enabled: typeof ModelDownloader !== "undefined"

        function onDownloadStarted() {
            log("Download started", "info")
        }

        function onDownloadFinished(path) {
            log("Download completed: " + path, "success")
        }

        function onDownloadErrorOccurred(error) {
            log("Error: " + error, "error")
        }

        function onStatusMessageChanged() {
            if (ModelDownloader.statusMessage) {
                log(ModelDownloader.statusMessage, "info")
            }
        }

        function onDownloadProgressChanged() {
            var progress = ModelDownloader.downloadProgress
            if (progress === 25 || progress === 50 || progress === 75 || progress === 100) {
                log("Download progress: " + progress + "%", "progress")
            }
        }

        function onDownloadLocationChanged(location) {
            log("Download location: " + location, "info")
        }

        function onModelVersionChanged(version) {
            log("Model version: " + version, "info")
        }

        function onFileDownloadProgress(filename, current, total) {
            if (current === total) {
                log("Downloaded: " + filename, "success")
            }
        }
    }

    // Connections to ModelTransformer (which is actually ModelConverter)
    Connections {
        target: ModelTransformer
        enabled: typeof ModelTransformer !== "undefined"

        function onConversionStarted() {
            log("Conversion started", "info")
        }

        function onConversionCompleted(outputPath) {
            log("Conversion completed: " + outputPath, "success")
        }

        function onConversionError(error) {
            log("Conversion error: " + error, "error")
        }

        function onConversionStatusChanged() {
            if (ModelTransformer.conversionStatus) {
                var status = ModelTransformer.conversionStatus
                if (status.includes("Error") || status.includes("Failed")) {
                    log(status, "error")
                } else {
                    log(status, "info")
                }
            }
        }

        function onConversionProgressChanged() {
            var progress = ModelTransformer.conversionProgress
            if (progress === 25 || progress === 50 || progress === 75 || progress === 100) {
                log("Conversion progress: " + progress + "%", "progress")
            }
        }

        function onConversionStepChanged(step) {
            log(step, "info")
        }

        function onOutputLocationChanged(location) {
            log("Output location: " + location, "info")
        }

        function onModelNameChanged(name) {
            log("Model: " + name, "info")
        }

        function onIsConvertingChanged() {
            if (!ModelTransformer.isConverting) {
                log("Conversion stopped", "warning")
            }
        }
    }
    // Add this after the ModelTransformer Connections block and before Component.onCompleted

    // Connections to ModelTrainer
    Connections {
        target: ModelTrainer
        enabled: typeof ModelTrainer !== "undefined"

        function onTrainingStarted() {
            log("Training started", "info")
        }

        function onTrainingCompleted(result) {
            if (result === "failed") {
                log("Training failed", "error")
            } else {
                // Split multi-line result into separate log entries
                var lines = result.split('\n')
                for (var i = 0; i < lines.length; i++) {
                    if (lines[i].trim() !== "") {
                        log(lines[i], "success")
                    }
                }
            }
        }

        function onTrainingProgressChanged() {
            var progress = ModelTrainer.trainingProgress
            if (progress === 25 || progress === 50 || progress === 75 || progress === 100) {
                log("Training progress: " + progress + "%", "progress")
            }
        }

        function onTrainingPaused() {
            log("Training paused", "warning")
        }

        function onTrainingResumed() {
            log("Training resumed", "info")
        }

        function onIsTrainingInProgressChanged() {
            if (!ModelTrainer.isTrainingInProgress) {
                log("Training stopped", "warning")
            }
        }

        function onStatusMessageChanged() {
            if (ModelTrainer.statusMessage) {
                var msg = ModelTrainer.statusMessage
                if (msg.includes("Error") || msg.includes("failed") || msg.includes("invalid")) {
                    log(msg, "error")
                } else if (msg.includes("paused") || msg.includes("stopped") || msg.includes("canceled")) {
                    log(msg, "warning")
                } else if (msg.includes("completed") || msg.includes("success")) {
                    log(msg, "success")
                } else if (msg.includes("progress") || msg.includes("Step") || msg.includes("Epoch")) {
                    log(msg, "progress")
                } else {
                    log(msg, "info")
                }
            }
        }

        function onLossUpdated(loss) {
            // Log loss at certain intervals or significant changes
            var lossPercent = Math.round(loss * 100)
            if (lossPercent % 10 === 0 || loss < 0.2) {  // Log every ~10% change or when loss is low
                log("Current loss: " + loss.toFixed(4), "info")
            }
        }

        function onAccuracyUpdated(accuracy) {
            // Log accuracy at certain intervals
            var accuracyPercent = Math.round(accuracy * 100)
            if (accuracyPercent % 10 === 0 || accuracyPercent > 90) {  // Log every ~10% change or high accuracy
                log("Current accuracy: " + (accuracy * 100).toFixed(1) + "%", "info")
            }
        }

        function onDataSetPathChanged() {
            log("Dataset path: " + ModelTrainer.datasetPath, "info")
        }

        function onEpochChanged() {
            log("Epochs set to: " + ModelTrainer.epoch, "info")
        }

        function onBatchSizeChanged() {
            log("Batch size set to: " + ModelTrainer.batchSize, "info")
        }

        function onLearningRateChanged() {
            log("Learning rate set to: " + ModelTrainer.learningRate, "info")
        }

        function onTrainTestSplitChanged() {
            log("Train/Test split: " + ModelTrainer.trainTestSplit + "% train", "info")
        }
    }

    // Log when component is ready
    Component.onCompleted: {
        var connected = false

        if (typeof ModelDownloader !== "undefined") {
            log("Connected to ModelDownloader", "success")
            if (ModelDownloader.downloadLocation) {
                log("Default download location: " + ModelDownloader.downloadLocation, "info")
            }
            connected = true
        }

        if (typeof ModelTransformer !== "undefined") {
            log("Connected to ModelTransformer", "success")
            if (ModelTransformer.outputLocation) {
                log("Default output location: " + ModelTransformer.outputLocation, "info")
            }
            log("isConverting: " + ModelTransformer.isConverting, "info")
            log("conversionProgress: " + ModelTransformer.conversionProgress, "info")
            log("conversionStatus: " + ModelTransformer.conversionStatus, "info")
            connected = true
        }

        if (typeof ModelTrainer !== "undefined") {
            log("Connected to ModelTrainer", "success")
            log("Default dataset: " + (ModelTrainer.datasetPath || "none"), "info")
            log("Epochs: " + ModelTrainer.epoch, "info")
            log("Batch size: " + ModelTrainer.batchSize, "info")
            log("Learning rate: " + ModelTrainer.learningRate, "info")
            log("Train/Test split: " + ModelTrainer.trainTestSplit + "% train", "info")
            log("isTrainingInProgress: " + ModelTrainer.isTrainingInProgress, "info")
            log("trainingProgress: " + ModelTrainer.trainingProgress + "%", "info")
            connected = true
        }

        if (!connected) {
            log("No model backend found", "warning")
        }
    }
}
