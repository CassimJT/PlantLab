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
            font.pixelSize: 11
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

        if (!connected) {
            log("No model backend found", "warning")
        }
    }
}
