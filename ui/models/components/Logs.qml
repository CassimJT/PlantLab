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

    function log(message) {
        var timestamp = new Date().toLocaleTimeString()
        logTextArea.text += "[" + timestamp + "] " + message + "\n"
        logTextArea.cursorPosition = logTextArea.length
    }

    function clear() {
        logTextArea.text = ""
        log("Logs ready")
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
            color: "#00ff00"
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
            log("Download started")
        }

        function onDownloadFinished(path) {
            log("Download completed: " + path)
        }

        function onDownloadErrorOccurred(error) {
            log("Error: " + error)
        }

        function onStatusMessageChanged() {
            if (ModelDownloader.statusMessage) {
                log("ℹ " + ModelDownloader.statusMessage)
            }
        }

        function onDownloadProgressChanged() {
            // Log at 25%, 50%, 75%, 100%
            var progress = ModelDownloader.downloadProgress
            if (progress === 25 || progress === 50 || progress === 75 || progress === 100) {
                log("Download progress: " + progress + "%")
            }
        }

        function onDownloadLocationChanged(location) {
            log("Download location: " + location)
        }

        function onModelVersionChanged(version) {
            log("Model version: " + version)
        }

        function onFileDownloadProgress(filename, current, total) {
            // Only log occasionally to avoid spam
            if (current === total) {
                log("Downloaded: " + filename)
            }
        }
    }

    // Connections to ModelTransformer (context property)
    Connections {
        target: ModelTransformer
        enabled: typeof ModelTransformer !== "undefined"

        function onTransformationStarted() {
            log("Transformation started")
        }

        function onTransformationFinished(outputPath) {
            log("Transformation completed: " + outputPath)
        }

        function onTransformationError(error) {
            log("Transformation error: " + error)
        }

        function onStatusMessageChanged() {
            if (ModelTransformer.statusMessage) {
                log("ℹ" + ModelTransformer.statusMessage)
            }
        }

        function onProgressChanged() {
            var progress = ModelTransformer.progressValue
            if (progress === 25 || progress === 50 || progress === 75 || progress === 100) {
                log("Transformation progress: " + progress + "%")
            }
        }

        function onOutputLocationChanged(location) {
            log("Output location: " + location)
        }

        function onSourceFrameworkChanged(framework) {
            log("Source framework: " + framework)
        }

        function onTargetFrameworkChanged(framework) {
            log("Target framework: " + framework)
        }

        function onExportFormatChanged(format) {
            log("Export format: " + format)
        }

        function onConversionStep(step) {
            log("⚙Step: " + step)
        }

        function onModelLoaded(path) {
            log("Model loaded: " + path)
        }

        function onOptimizationStarted() {
            log("Model optimization started")
        }

        function onOptimizationCompleted() {
            log("Model optimization completed")
        }

        function onQuantizationStarted(type) {
            log("Quantization started: " + type)
        }

        function onQuantizationCompleted() {
            log("Quantization completed")
        }
    }

    // Log when component is ready
    Component.onCompleted: {
        var connected = false

        if (typeof ModelDownloader !== "undefined") {
            log("Connected to ModelDownloader")
            if (ModelDownloader.downloadLocation) {
                log("Default download location: " + ModelDownloader.downloadLocation)
            }
            connected = true
        }

        if (typeof ModelTransformer !== "undefined") {
            log("Connected to ModelTransformer")
            if (ModelTransformer.outputLocation) {
                log("Default output location: " + ModelTransformer.outputLocation)
            }
            connected = true
        }

        if (!connected) {
            log("⚠No model backend found")
        }
    }
}
