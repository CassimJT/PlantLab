import QtQuick 2.15
import QtQuick.Controls 2.15
import "../componets"

ItemDelegate {
    id: itemDelegate
    width: 170
    height: 170

    property bool autoMode: true
    property bool onlineStatus: true

    Component.onCompleted: {
        console.log("Delegate CREATED for device:", model?.deviceId ?? "?", "at index:", index)
    }
    Component.onDestruction: {
        console.log("Delegate DESTROYED for device:", model?.deviceId ?? "?")
    }

    // Online/offline indicator
    Rectangle {
        id: indicator
        width: 15; height: width
        radius: width / 2
        anchors { right: parent.right; top: parent.top; margins: 5 }
        color: itemDelegate.onlineStatus ? "lightGreen" : "red"
        Behavior on color { ColorAnimation { duration: 250 } }
    }

    background: Rectangle {
        radius: 6
        color: itemDelegate.pressed    ? "#e2e8f0"
              : itemDelegate.highlighted ? "#dbeafe"
              : itemDelegate.hovered     ? "#f1f5f9"
              : "#f1f1f1"
    }

    DeviceManu {
        id: deviceManu

        // ─── The important fixes ───
        deviceModel:     model
        autoMode:        itemDelegate.autoMode
        onlineStatus:    itemDelegate.onlineStatus
    }

    Image {
        id: pnd_device
        source: "qrc:/assets/devices/PND.png"
        width: parent.width
        height: parent.height
        fillMode: Image.PreserveAspectFit
        opacity: 0.8

        Text {
            id: name
            text: qsTr("PND")
            font.bold: true
            color: "lightblue"
            anchors.centerIn: parent
        }
    }

    Label {
        id: deviceName
        text: model?.deviceId ?? "???"
        anchors {
            horizontalCenter: parent.horizontalCenter
            bottom: parent.bottom
            bottomMargin: 5
        }
    }

    onClicked: {
        deviceManu.deviceModel = model
        deviceManu.open()
    }

    Connections {
        target: DeviceConfigurator
        function onDeviceConnected(_id) {
            if (model?.deviceId === _id) itemDelegate.onlineStatus = true
        }
        function onDeviceDisconnected(_id) {
            if (model?.deviceId === _id) itemDelegate.onlineStatus = false
        }
        function onDeviceSensorsUpdated(_id, temp, hum) {
            if (model?.deviceId === _id) {
                model.temperature = temp
                model.humidity = hum
            }
        }
    }
}
