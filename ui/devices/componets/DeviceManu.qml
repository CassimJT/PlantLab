import QtQuick 2.15
import QtQuick.Controls 2.15

Popup {
    id: deviceMenu
    width: 150
    height: 230
    x: parent.width - (width - 20)
    y: (parent.height + height) / 4
    padding: 8
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent

    property var  deviceModel
    property bool autoMode
    property bool onlineStatus

    readonly property string deviceId: deviceModel ? deviceModel.deviceId : ""

    background: Rectangle {
        radius: 6
        color: "#0f172a"
        border.color: "#334155"
        border.width: 1

        Image {
            id: btn
            source: "qrc:/assets/devices/close.png"
            width: 20
            height: width
            fillMode: Image.PreserveAspectFit
            anchors {
                right: parent.right
                top: parent.top
                margins: 2
            }
            MouseArea {
                anchors.fill: parent
                onClicked: deviceMenu.close()
            }
        }
    }

    contentItem: Column {
        spacing: 8
        width: parent.width

        // ── Your header, divider, sensors ── (unchanged)
        Column {
            width: parent.width
            spacing: 2
            Label {
                text: deviceModel && deviceModel.name ? deviceModel.deviceId : "PND Device"
                color: "white"
                font.pixelSize: 14
                font.bold: true
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
            }
            Label {
                text: deviceId
                color: "#94a3b8"
                font.pixelSize: 9
                font.family: "Courier"
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
            }
        }

        Rectangle { width: parent.width; height: 1; color: "#334155" }

        // Temperature + Humidity (your original)
        Row {
            width: parent.width
            spacing: 8
            Rectangle {
                width: (parent.width - 8) / 2
                height: 50
                radius: 4
                color: "#1e293b"
                Column {
                    anchors.centerIn: parent
                    spacing: 2
                    Label {
                        text: "🌡️ Temp"
                        color: "#94a3b8"
                        font.pixelSize: 10
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    Label {
                        text: deviceModel && deviceModel.temperature !== undefined
                              ? Number(deviceModel.temperature).toFixed(1) + "°C"
                              : "--°C"
                        color: "#fbbf24"
                        font.pixelSize: 14
                        font.bold: true
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
            Rectangle {
                width: (parent.width - 8) / 2
                height: 50
                radius: 4
                color: "#1e293b"
                Column {
                    anchors.centerIn: parent
                    spacing: 2
                    Label {
                        text: "💧 Humidity"
                        color: "#94a3b8"
                        font.pixelSize: 10
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    Label {
                        text: deviceModel && deviceModel.humidity !== undefined
                              ? Number(deviceModel.humidity).toFixed(1) + "%"
                              : "--%"
                        color: "#60a5fa"
                        font.pixelSize: 14
                        font.bold: true
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }
        }

        Rectangle { width: parent.width; height: 1; color: "#334155" }

        // ── Auto Mode – your original custom switch design ──
        Row {
            spacing: 8
            width: parent.width
            Label {
                text: "Auto Mode"
                color: "white"
                font.pixelSize: 12
                width: parent.width - 48
                verticalAlignment: Text.AlignVCenter
            }
            Switch {
                id: autoModeSwitch
                checked: autoMode
                onCheckedChanged: {
                    autoMode = checked
                    if (deviceModel) {
                        deviceModel.autoMode = checked
                    }
                    if (DeviceConfigurator && deviceId) {
                        DeviceConfigurator.configureDevice(deviceId, {
                            "auto_mode": checked
                        })
                    }
                }
                indicator: Rectangle {
                    implicitWidth: 40
                    implicitHeight: 20
                    x: autoModeSwitch.leftPadding
                    y: parent.height / 2 - height / 2
                    radius: 10
                    color: autoModeSwitch.checked ? "#4CAF50" : "#757575"
                    Rectangle {
                        x: autoModeSwitch.checked ? 20 : 2
                        y: 2
                        width: 16
                        height: 16
                        radius: 8
                        color: "white"
                    }
                }
            }
        }

        // ── Power switch – your original custom design ──
        Row {
            spacing: 8
            width: parent.width
            Label {
                text: "Power"
                color: "white"
                font.pixelSize: 12
                width: parent.width - 48
                verticalAlignment: Text.AlignVCenter
            }
            Switch {
                id: powerSwitch
                checked: onlineStatus
                onCheckedChanged: {
                    onlineStatus = checked
                    if (deviceModel) {
                        deviceModel.onlineStatus = checked
                    }
                    if (DeviceConfigurator && deviceId) {
                        console.log("Setting device power:", deviceId, checked)
                        DeviceConfigurator.setDevicePower(deviceId, checked)
                    }
                }
                indicator: Rectangle {
                    implicitWidth: 40
                    implicitHeight: 20
                    x: powerSwitch.leftPadding
                    y: parent.height / 2 - height / 2
                    radius: 10
                    color: powerSwitch.checked ? "#4CAF50" : "#757575"
                    Rectangle {
                        x: powerSwitch.checked ? 20 : 2
                        y: 2
                        width: 16
                        height: 16
                        radius: 8
                        color: "white"
                    }
                }
            }
        }

        // Status text + last seen (your original)
        Label {
            text: powerSwitch.checked ? "● Online" : "○ Offline"
            color: powerSwitch.checked ? "#4CAF50" : "#f44336"
            font.pixelSize: 10
            font.bold: true
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            topPadding: 4
        }

        Label {
            text: "Last seen: " + (deviceModel && deviceModel.lastUpdate
                                   ? deviceModel.lastUpdate : "Just now")
            color: "#64748b"
            font.pixelSize: 8
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            visible: deviceId !== ""
        }
    }

    Connections {
        target: DeviceConfigurator
        function onDeviceConnected(id) {
            if (id === deviceId) {
                powerSwitch.checked = true
                onlineStatus = true
            }
        }
        function onDeviceDisconnected(id) {
            if (id === deviceId) {
                powerSwitch.checked = false
                onlineStatus = false
            }
        }
    }

    onOpened: {
        if (DeviceConfigurator && deviceId && powerSwitch.checked) {
            DeviceConfigurator.requestDeviceStatus(deviceId)
            DeviceConfigurator.requestDeviceSensors(deviceId)
        }
    }
}
