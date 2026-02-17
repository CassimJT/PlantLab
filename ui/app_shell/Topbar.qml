import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material
import QtQuick.Window 2.15

Rectangle {
    id: topBar
    height: 45
    color: "#f5f5f5"
    clip: true
    z:10

    // Window references
    property var liveMonitorWindow: null
    property var inferenceWindow: null
    property var settingsWindow: null

    ToolBar {
        anchors.fill: parent
        Material.background: "Transparent"

        RowLayout {
            anchors.fill: parent
            Layout.margins: 8

            Item { Layout.fillWidth: true }

            ToolButton {
                id: menuButton
                icon.source: "qrc:/assets/topBar/menu.svg"
                display: AbstractButton.IconOnly
                icon.width: 36
                icon.height: 36
                Layout.alignment: Qt.AlignVCenter
                Layout.rightMargin: 10
                onClicked: appMenu.open()

                Menu {
                    id: appMenu
                    onAboutToShow: {
                        x = menuButton.width - width
                        y = menuButton.height
                    }

                    MenuItem {
                        icon.source: "qrc:/assets/topBar/pest.svg"
                        text: qsTr("Live Pest Monitor")
                        onClicked: {
                            if (!liveMonitorWindow) {
                                liveMonitorWindow = Qt.createComponent("./windows/LiveMonitor.qml").createObject()
                                liveMonitorWindow.closing.connect(function() {
                                    liveMonitorWindow = null
                                })
                            } else {
                                liveMonitorWindow.show()
                                liveMonitorWindow.raise()
                            }
                        }
                    }

                    MenuSeparator{}

                    MenuItem {
                        icon.source: "qrc:/assets/topBar/infarence.svg"
                        text: qsTr("Run infarences")
                        onClicked: {
                            if (!inferenceWindow) {
                                inferenceWindow = Qt.createComponent("./windows/Infarance.qml").createObject()
                                inferenceWindow.closing.connect(function() {
                                    inferenceWindow = null
                                })
                            } else {
                                inferenceWindow.show()
                                inferenceWindow.raise()
                            }
                        }
                    }

                    MenuSeparator{}

                    MenuItem {
                        icon.source: "qrc:/assets/sidebar_icon/settings.svg"
                        text: qsTr("Settings")
                        onClicked: {
                            if (!settingsWindow) {
                                settingsWindow = Qt.createComponent("./windows/Settings.qml").createObject()
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
            }
        }
    }
}
