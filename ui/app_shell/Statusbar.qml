import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15

Rectangle {
    id: progressBarComponent
    height: 32
    color: "#f5f5f5"

    anchors {
        left: parent.left
        right: parent.right
    }

    property var datasetProcessor: null
    property string operationType: "normalization"
    property bool isProcessing: datasetProcessor ? datasetProcessor.isProcessing : false
    property int exportProgressValue: 0  // Track export progress separately

    onIsProcessingChanged: {
        console.log("ProgressBar - isProcessing changed to:", isProcessing)
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        spacing: 8

        visible: progressBarComponent.isProcessing

        ProgressBar {
            id: progressBar
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            implicitHeight: 18

            from: 0
            to: 100  // Always use 100 as max for percentage display
            value: {
                if (progressBarComponent.operationType === "export") {
                    // For export, progressValue is already a percentage (0-100)
                    return datasetProcessor ? datasetProcessor.progressValue : 0
                } else {
                    // For normalization, convert count to percentage
                    if (!datasetProcessor || datasetProcessor.totalImagesToProcess === 0) return 0
                    return (datasetProcessor.progressValue / datasetProcessor.totalImagesToProcess) * 100
                }
            }
        }

        Label {
            text: {
                if (!datasetProcessor) return "0%"

                var percent
                if (progressBarComponent.operationType === "export") {
                    // For export, progressValue is already a percentage
                    percent = datasetProcessor.progressValue
                } else {
                    // For normalization, calculate percentage from count
                    if (datasetProcessor.totalImagesToProcess === 0) return "0%"
                    percent = Math.round((datasetProcessor.progressValue / datasetProcessor.totalImagesToProcess) * 100)
                }
                // Ensure percent is between 0-100
                percent = Math.min(100, Math.max(0, percent))
                return percent + "%"
            }

            font.bold: true
            color: "#333333"
            Layout.preferredWidth: 50
            Layout.alignment: Qt.AlignVCenter
            horizontalAlignment: Text.AlignRight
            verticalAlignment: Text.AlignVCenter
        }

        Button {
            text: "✕"
            flat: true
            Layout.preferredWidth: 26
            Layout.preferredHeight: 26
            Layout.alignment: Qt.AlignVCenter

            visible: progressBarComponent.isProcessing

            onClicked: {
                console.log("Cancel button clicked")
                if (datasetProcessor) {
                    datasetProcessor.cancelProcessing()
                }
            }

            background: Rectangle {
                color: parent.hovered ? "#ffebee" : "transparent"
                radius: 13
            }

            contentItem: Text {
                text: parent.text
                color: parent.hovered ? "#f44336" : "#757575"
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    Label {
        id: statusText
        anchors.top: parent.bottom
        anchors.topMargin: 4
        anchors.left: parent.left
        anchors.right: parent.right

        text: datasetProcessor ? getStatusMessage() : ""
        color: "#666666"
        font.pixelSize: 11
        elide: Text.ElideRight

        visible: progressBarComponent.isProcessing

        function getStatusMessage() {
            if (!datasetProcessor) return ""

            var processed = datasetProcessor.progressValue
            var total = datasetProcessor.totalImagesToProcess

            if (total === 0) return "Processing..."

            if (progressBarComponent.operationType === "export") {
                // For export, show percentage
                return `Exporting: ${processed}% complete`
            } else {
                // For normalization, show count
                return `Processing: ${processed} of ${total} images`
            }
        }
    }

    Connections {
        target: datasetProcessor
        enabled: datasetProcessor !== null

        function onIsProcessingChanged() {
            console.log("Signal: isProcessing changed to:", datasetProcessor.isProcessing)
            progressBarComponent.isProcessing = datasetProcessor.isProcessing
        }

        function onExportStatus(message) {
            statusText.text = message
            statusText.color = "#666666"

            if (message.includes("Export") || message.includes("export")) {
                progressBarComponent.operationType = "export"
            }
            console.log("Export status:", message)
        }

        function onExportProgress(value) {
            // Just update the property - the binding will handle it
            console.log("Export progress:", value + "%")
        }

        function onNormalizationStarted(message) {
            statusText.text = message
            statusText.color = "#666666"
            progressBarComponent.operationType = "normalization"
            console.log("Normalization started")
        }

        function onExportStarted(format, destination) {
            statusText.text = `Exporting to ${format}...`
            statusText.color = "#666666"
            progressBarComponent.operationType = "export"
            console.log("Export started to:", destination)
        }

        function onNormalizationCompleted(message) {
            statusText.text = message
            statusText.color = "#4CAF50"
            console.log("Normalization completed")
            hideTimer.start()
        }

        function onExportCompleted(message) {
            statusText.text = message
            statusText.color = "#4CAF50"
            console.log("Export completed")
            hideTimer.start()
        }

        function onNormalizationFailed(message) {
            statusText.text = "Error: " + message
            statusText.color = "#f44336"
            console.log("Normalization failed:", message)
            hideTimer.start()
        }

        function onExportFailed(message) {
            statusText.text = "Error: " + message
            statusText.color = "#f44336"
            console.log("Export failed:", message)
            hideTimer.start()
        }

        function onNormalizationCanceled() {
            statusText.text = "Operation canceled"
            statusText.color = "#f44336"
            console.log("Normalization canceled")
            hideTimer.start()
        }
    }

    Timer {
        id: hideTimer
        interval: 3000
        onTriggered: {
            console.log("Timer triggered, isProcessing:", progressBarComponent.isProcessing)
            if (!progressBarComponent.isProcessing) {
                statusText.text = ""
            }
        }
    }

    Behavior on height {
        NumberAnimation { duration: 200 }
    }
}
