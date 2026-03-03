import QtQuick 2.15
import QtQuick.Controls
// ===== Custom popup menu =====
Popup {
    id: deviceMenu
    width: 130
    height: 150
    x: parent.width - (width - 20)
    y: (parent.height + height) / 4
    padding: 8
    //modal: true
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent

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
                onClicked :{
                    deviceManu.close()
                }
            }

        }
    }


    contentItem: Column {
        spacing: 8
        width: parent.width

        // Device name header
        Label {
            text: model.name
            color: "white"
            font.pixelSize: 14
            font.bold: true
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            bottomPadding: 4
        }

        Rectangle {
            width: parent.width
            height: 1
            color: "#334155"
        }

        // Auto Mode switch
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
                checked: itemDelegate.autoMode
                onCheckedChanged: itemDelegate.autoMode = checked

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

        // Online/Offline switch
        Row {
            spacing: 8
            width: parent.width

            Label {
                text: "Status"
                color: "white"
                font.pixelSize: 12
                width: parent.width - 48
                verticalAlignment: Text.AlignVCenter
            }

            Switch {
                id: statusSwitch
                checked: itemDelegate.onlineStatus
                onCheckedChanged: {
                    itemDelegate.onlineStatus = checked
                    indicator.color = checked ? "lightGreen" : "red"
                }

                indicator: Rectangle {
                    implicitWidth: 40
                    implicitHeight: 20
                    x: statusSwitch.leftPadding
                    y: parent.height / 2 - height / 2
                    radius: 10
                    color: statusSwitch.checked ? "#4CAF50" : "#757575"

                    Rectangle {
                        x: statusSwitch.checked ? 20 : 2
                        y: 2
                        width: 16
                        height: 16
                        radius: 8
                        color: "white"
                    }
                }
            }
        }

        // Status text indicator
        Label {
            text: statusSwitch.checked ? "Online" : "Offline"
            color: statusSwitch.checked ? "#4CAF50" : "#f44336"
            font.pixelSize: 10
            font.bold: true
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            topPadding: 4
        }
    }
}
