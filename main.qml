import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    width: screen.width * 0.85
    height: screen.height * 0.85
    visible: true
    title: qsTr("PlantLab")

    menuBar: MenuBar {
        Menu {
            title: qsTr("File")
            MenuItem { text: qsTr("Open") }
            MenuItem { text: qsTr("Save") }
            MenuSeparator {}
            MenuItem { text: qsTr("Exit"); onTriggered: Qt.quit() }
        }
        Menu {
            title: qsTr("Edit")
            MenuItem { text: qsTr("Preference") }

        }

        Menu {
            title: qsTr("View")
            MenuItem { text: qsTr("Dashboard") }
            MenuItem { text: qsTr("Settings") }
        }

        Menu {
            title: qsTr("Help")
            MenuItem { text: qsTr("About") }
        }
    }

    Loader {
        id: app_main_loader
        anchors.fill: parent
        source: "ui/app_shell/Mainwindow.qml"

    }
}
