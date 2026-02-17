import QtQuick 2.15
import QtQuick.Controls 2.15
import "./model"
import "./delegate"
import QtQuick.Layouts

Page {
    id: sidebar
    width: parent.width * 0.15
    clip: true
    background: Rectangle {
        color: "#ffffff"
    }

    anchors {
        top: parent.top
        left: parent.left
        bottom: parent.bottom
    }

    ItemDelegate {
        id: logo
        padding: 10
        spacing: 2
        width: parent.width
        height: parent.height * .10
        background: Rectangle {
            color: logo.highlighted ? "#e0f2fe"
                 : logo.hovered   ? "#f1f5f9"
                                  : "transparent"
            radius: 8
        }
        icon.source: "qrc:/assets/app_icon/PlantDocutor.png"
        icon.width: 42
        icon.height: 42
        icon.color: Qt.rgba(0,0,0,0)
        text: "PlantDoctor"
        display: AbstractButton.TextBesideIcon

        anchors {
            top: parent.top
        }
    }
    MenuSeparator {
        id: menuseparator
        width: parent.width
        anchors {
            top: logo.bottom
        }
    }
    Label {
        id: menu
        padding: 10
        text: qsTr("Menu")
        anchors {
            top: menuseparator.bottom
        }
    }

    ListView {
        id: sidebar_listview
        model: SideBarModel{}
        delegate: SideBarDelegate{}
        clip: true
        spacing: 3

        anchors {
            top: menu.bottom
            topMargin: 12
            right: parent.right
            left: parent.left
            bottom: user_id.top
            rightMargin: 3
            leftMargin: 3
        }
    }


    ItemDelegate {
        id: user_id
        width: parent.width
        height: 70
        background: Rectangle {
            color: user_id.highlighted ? "#e0f2fe"
                 : user_id.hovered   ? "#f1f5f9"
                                  : "transparent"
            radius: 8
        }
        Row {
            height: parent.height
            spacing: 5
            padding: 10
            Rectangle {
                id: circle
                width: 40
                height: width
                radius: width / 2
                color: "lightblue"
                Text {
                    id: latter
                    text: qsTr("C")
                    font.bold: true
                    color: "grey"
                    anchors.centerIn: parent
                }
                anchors {
                    verticalCenter: parent.verticalCenter
                }
            }
            Text {
                id: user_email
                text: qsTr("CassimJt@gmail.com")
                color: "#333"
                anchors {
                    verticalCenter: parent.verticalCenter
                }
            }

        }
        anchors {
            bottom: parent.bottom
        }
    }
    
}
