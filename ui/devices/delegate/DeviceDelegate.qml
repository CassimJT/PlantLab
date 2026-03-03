import QtQuick 2.15
import QtQuick.Controls 2.15
import "../componets"
ItemDelegate {
    id: itemDelegate
    width: 170
    height: 170

    // Properties for switch states
    property bool autoMode: true
    property bool onlineStatus: true

    Rectangle {
        id: indicator
        width: 15
        height: width
        radius: width / 2
        color: onlineStatus ? "lightGreen" : "red"
        anchors {
            right: parent.right
            top: parent.top
            margins: 5
        }
    }

    background: Rectangle {
        radius: 6
        color: itemDelegate.pressed
               ? "#e2e8f0"
               : itemDelegate.highlighted
                 ? "#dbeafe"
                 : itemDelegate.hovered
                   ? "#f1f5f9"
                   : "#f1f1f1"
    }

    DeviceManu {
        id: deviceManu
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
        text: model.name
        anchors {
            horizontalCenter: parent.horizontalCenter
            bottom: parent.bottom
            bottomMargin: 5
        }
    }

    onClicked: {
        deviceManu.open()
    }
}
