import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import RTSVideoOutput

Window {
    width: 800
    height: 600
    visible: true
    title: "Live Pest Monitor"

    flags: Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint
    Rectangle {
        anchors.fill: parent
        color: "#1a1a1a"
    }

    RTSVideoOutput {
        id: videoOutput
        width: 640
        height: 480
        rtsUrl: "http://192.168.8.117/mjpeg"
        detectionEnabled: false  // Start with detection disabled

        onDetectionResult: {
            console.log("Detection:", result)
            // You can add visual feedback here
        }

        onIsConnectedChanged: {
            if (isConnected) {
                console.log("Camera connected - will enable detection in 5 seconds")
                connectionStatusText.text = "Camera CONNECTED - Stabilizing..."
                connectionStatusText.color = "#ff9800"
                enableDetectionTimer.start()
            } else {
                console.log("Camera disconnected - detection disabled")
                videoOutput.detectionEnabled = false
                detectionStatusText.text = "Pest Detection: DISABLED (Camera Offline)"
                detectionStatusText.color = "#f44336"
                connectionStatusText.text = "Camera OFFLINE - Waiting for connection..."
                connectionStatusText.color = "#f44336"
                // Try reconnection detection after delay
                reconnectionTimer.start()
            }
        }

        onModelloaded: {
            console.log("Pest detection model loaded successfully")
            modelStatusText.text = "Model: LOADED ✓"
            modelStatusText.color = "#4caf50"
        }

        onModelLoadingFailed: {
            console.log("Model loading failed:", arguments[0])
            modelStatusText.text = "Model: FAILED ✗"
            modelStatusText.color = "#f44336"
        }

        anchors {
            top: parent.top
            right: parent.right
            left: parent.left
            bottom: statusBar.top
        }
    }

    // Overlay text showing detection status
    Rectangle {
        id: detectionOverlay
        anchors.top: parent.top
        anchors.right: parent.right
        width: 250
        height: 90
        color: "#80000000"
        radius: 5
        anchors.margins: 10

        Column {
            anchors.centerIn: parent
            spacing: 5

            Text {
                id: detectionStatusText
                text: "Pest Detection: DISABLED (Starting soon)"
                color: "#ff9800"
                font.pixelSize: 11
                font.bold: true
            }

            Text {
                id: modelStatusText
                text: "Model: LOADING..."
                color: "#ff9800"
                font.pixelSize: 10
            }

            Text {
                id: connectionStatusText
                text: "Connecting to camera..."
                color: "#ff9800"
                font.pixelSize: 10
            }
        }
    }

    // Busy indicator when not connected
    BusyIndicator {
        anchors.centerIn: parent
        running: !videoOutput.isConnected
        visible: running
        width: 80
        height: 80

        Text {
            text: "Connecting to camera..."
            color: "#ffffff"
            font.pixelSize: 14
            anchors.top: parent.bottom
            anchors.topMargin: 10
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }

    // Status bar at bottom
    Rectangle {
        id: statusBar
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 40
        color: "#2c2c2c"

        Row {
            anchors.centerIn: parent
            spacing: 15

            Rectangle {
                width: 10
                height: 10
                radius: 5
                color: videoOutput.isConnected ? "#4caf50" : "#f44336"
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: videoOutput.isConnected ? "LIVE" : "OFFLINE"
                color: videoOutput.isConnected ? "#4caf50" : "#f44336"
                font.pixelSize: 12
                font.bold: true
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: videoOutput.isConnected ?
                      (videoOutput.detectionEnabled ? "Detection: ACTIVE" : "Detection: STARTING...") :
                      "Camera offline"
                color: videoOutput.isConnected ?
                       (videoOutput.detectionEnabled ? "#4caf50" : "#ff9800") :
                       "#f44336"
                font.pixelSize: 11
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: videoOutput.isConnected ?
                      (videoOutput.fps > 0 ? `FPS: ${Math.round(videoOutput.fps)}` : "FPS: --") :
                      ""
                color: "#ffffff"
                font.pixelSize: 11
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    // Optional: Manual control button
    Button {
        text: "Toggle Detection"
        anchors.bottom: statusBar.top
        anchors.right: parent.right
        anchors.margins: 10
        width: 120
        height: 30
        visible: videoOutput.isConnected

        background: Rectangle {
            color: parent.pressed ? "#4caf50" : "#2c2c2c"
            radius: 3
        }

        contentItem: Text {
            text: videoOutput.detectionEnabled ? "Disable Detection" : "Enable Detection"
            color: "#ffffff"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            if (videoOutput.detectionEnabled) {
                videoOutput.detectionEnabled = false
                detectionStatusText.text = "Pest Detection: MANUALLY DISABLED"
                detectionStatusText.color = "#f44336"
                console.log("Detection manually disabled")
            } else {
                videoOutput.detectionEnabled = true
                detectionStatusText.text = "Pest Detection: MANUALLY ENABLED"
                detectionStatusText.color = "#4caf50"
                console.log("Detection manually enabled")
            }
        }
    }
}