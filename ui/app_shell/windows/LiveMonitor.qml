import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import RTSVideoOutput 1.0

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
        overlayText: "ESP32-CAM | Detection Ready"
        detectionEnabled: true
        onDetectionResult: {
            console.log("Detection:", result)
        }
        anchors {
            top: parent.top
            right: parent.right
            left: parent.left
            bottom: statusBar.top
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
        height: 30
        color: "#2c2c2c"

        Row {
            anchors.centerIn: parent
            spacing: 10

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
                text: videoOutput.isConnected ? "Streaming from camera" : "Connecting to camera..."
                color: "#ffffff"
                font.pixelSize: 11
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }
}