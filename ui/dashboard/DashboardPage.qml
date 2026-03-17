import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "./component"

Page {
    id: dashboard

    property real metricCardheight: dashboard.height * 0.30
    property real chartHeight: dashboard.height * 0.32
    //property string deviceStateText: "OFF"

    // Use a function + delayed assignment to avoid QObject wrapper issues
    property var firstDevice: null

    background: Rectangle {
        color: Qt.rgba(0, 0, 0, 0)
        radius: 10
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16

            MetricCard {
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.metricCardheight

                DHTMeter {
                    id: dhtMeter

                    t_value: dashboard.firstDevice ? dashboard.firstDevice.temperature : 0.0
                    h_value: dashboard.firstDevice ? dashboard.firstDevice.humidity : 0.0
                    stateLabel: dashboard.firstDevice && dashboard.firstDevice.state === 2 ? "ON" : "OFF"

                    // Very important debug logs
                    onT_valueChanged: console.log("=== DHTMeter Temp →", t_value)
                    onH_valueChanged: console.log("=== DHTMeter Hum  →", h_value)
                }
            }

            MetricCard { Layout.fillWidth: true; Layout.preferredHeight: dashboard.metricCardheight }
            MetricCard {
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.metricCardheight
                CircularProgressBar { rawValue: 45 }
            }
        }

        // Your chart sections (unchanged)
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16
            ChartCard {
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.height * 0.40
                BusyIndicator { anchors.centerIn: parent }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 16
            Layout.fillHeight: true
            ChartCard { Layout.fillWidth: true; Layout.preferredHeight: dashboard.chartHeight }
            ChartCard { Layout.fillWidth: true; Layout.preferredHeight: dashboard.chartHeight }
        }
    }

    // ==================== Safe Device Selection ====================
    Connections {
        target: DeviceModel

        function onDeviceAdded(id) {
            console.log("QML: Device added:", id)
            Qt.callLater(updateFirstDevice)
        }

        function onCountChanged() {
            console.log("QML: Device count changed to", DeviceModel.count)
            Qt.callLater(updateFirstDevice)
        }
    }

    function updateFirstDevice() {
        if (DeviceModel.count > 0) {
            var dev = DeviceModel.getDeviceByIndex(0)
            if (dev) {
                dashboard.firstDevice = dev
                console.log("QML: firstDevice successfully set to", dev.deviceId)
            }
        } else {
            dashboard.firstDevice = null
        }
    }

    Component.onCompleted: {
        console.log("Dashboard loaded - count:", DeviceModel.count)
        Qt.callLater(updateFirstDevice)
    }
}
