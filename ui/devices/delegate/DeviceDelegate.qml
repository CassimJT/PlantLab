import QtQuick 2.15
import QtQuick.Controls 2.15

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

    // ===== Custom popup menu =====
    Popup {
        id: menu
        width: 130
        height: 150
        x: parent.width - 25
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

    Image {
        id: pnd_device
        source: "qrc:/assets/devices/PND.png"
        width: parent.width
        height: parent.height
        fillMode: Image.PreserveAspectFit

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
        menu.open()
    }
}
