import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    width: screen.width * 0.85
    height: screen.height * 0.85
    visible: true
    title: qsTr("PlantLab")
    property var aboutWindow: null
    property var settingsWindow: null

    menuBar: MenuBar {
        Menu {
            title: qsTr("PLantLab")
            MenuSeparator {}
            MenuItem { text: qsTr("Exit"); onTriggered: Qt.quit() }
        }
        Menu {
            title: qsTr("Edit")
            MenuItem {
                text: qsTr("Preference")
                onClicked: {
                    if (!settingsWindow) {
                        settingsWindow = Qt.createComponent("./ui/app_shell/windows/Settings.qml").createObject()
                        settingsWindow.closing.connect(function() {
                            settingsWindow = null
                        })
                    } else {
                        settingsWindow.show()
                        settingsWindow.raise()
                    }
                }
            }

        }


        Menu {
            title: qsTr("Help")
            MenuItem {
                text: qsTr("About")
                onClicked: {
                    if (!aboutWindow) {
                        aboutWindow = Qt.createComponent("./ui/app_shell/windows/About.qml").createObject()
                        aboutWindow.closing.connect(function() {
                            aboutWindow = null
                        })
                    } else {
                        aboutWindow.show()
                        aboutWindow.raise()
                    }
                }
            }
        }
    }

    Loader {
        id: app_main_loader
        anchors.fill: parent
        source: "ui/app_shell/Mainwindow.qml"

    }

}
