import QtQuick 2.15
import QtQuick.Controls 2.15
import "./delegate"
//import "./model"

Page {
    id: devicesPage

    background: Rectangle {
        color: "#f5f7fb"
    }
    padding: 20

    // Message when no devices are connected
    Item {
        anchors.centerIn: parent
        visible: DeviceModel && DeviceModel.count === 0 &&
                 DeviceConfigurator && !DeviceConfigurator.isScanning

        Column {
            spacing: 15
            anchors.centerIn: parent

            Text {
                text: "No Devices Connected"
                font.pixelSize: 18
                font.bold: true
                color: "#999"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: DeviceConfigurator && !DeviceConfigurator.isBrokerConnected
                      ? "Connect to MQTT broker to discover devices"
                      : "Click below to scan for devices"
                font.pixelSize: 14
                color: "#aaa"
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }

    GridView {
        id: gridView
        cellWidth: 200
        cellHeight: 200

        anchors {
            fill: parent
            margins: 15
        }

        model: DeviceModel
        delegate: DeviceDelegate{}

        // Only show when there are devices
        visible: DeviceModel && DeviceModel.count > 0
    }

    Button {
        id: centerButton
        anchors.centerIn: parent
        visible: DeviceModel && DeviceModel.count === 0 &&
                 DeviceConfigurator && !DeviceConfigurator.isScanning

        text: {
            if (!DeviceConfigurator) return "Loading..."
            if (!DeviceConfigurator.isBrokerConnected)
                return "Connect to Broker"
            else if (DeviceConfigurator.isScanning)
                return "Scanning..."
            else
                return "Scan for Devices"
        }

        enabled: DeviceConfigurator &&
                 !DeviceConfigurator.isScanning &&
                 DeviceConfigurator.isBrokerConnected

        onClicked: {
            if (!DeviceConfigurator) return
            if (!DeviceConfigurator.isBrokerConnected) {
                DeviceConfigurator.connectToBroker()
            } else {
                DeviceConfigurator.scanForDevices(10)
            }
        }

        width: 200
        height: 50
        anchors.bottomMargin: -40

    }

    // Loading indicator while scanning
    BusyIndicator {
        id: scanningIndicator
        anchors.centerIn: parent
        running: DeviceConfigurator &&
                 DeviceConfigurator.isScanning &&
                 DeviceModel && DeviceModel.count === 0
        visible: running
    }

    // Auto-scan when broker connects
    Connections {
        target: DeviceConfigurator

        function onBrokerConnectionChanged() {
            if (DeviceConfigurator && DeviceConfigurator.isBrokerConnected) {
                console.log("Broker connected - auto-scanning for devices")
                DeviceConfigurator.scanForDevices(10)
            }
        }

        function onDeviceDiscovered(deviceId) {
            console.log("Device discovered:", deviceId)
            if (DeviceConfigurator) {
                DeviceConfigurator.connectToDevice(deviceId)
            }
        }

        function onDeviceConnected(deviceId) {
            console.log("Device connected:", deviceId)
        }

        function onDeviceDisconnected(deviceId) {
            console.log("Device disconnected:", deviceId)
        }

        function onErrorOccurred(error) {
            console.error("Device error:", error)
        }
    }

    // Auto-connect to broker on startup
    Component.onCompleted: {
        if (DeviceConfigurator) {
            DeviceConfigurator.connectToBroker()
        }
    }
}
