import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    id:signInScreen
    width: 360
    height: 800
    background: Rectangle { color: "#edf2e0" }

    Flickable {
        anchors.fill: parent
        contentHeight: mainColumn.implicitHeight + 60
        clip: true

        ColumnLayout {
            id: mainColumn
            width: parent.width
            spacing: 0

            Item { Layout.preferredHeight: 100 }

            // App Logo
            Image {
                id: appLogo
                source: "qrc:/assets/app_icon/PlantDocutor.png"
                fillMode: Image.PreserveAspectFit

                Layout.preferredWidth: 40
                Layout.preferredHeight: 40
                Layout.alignment: Qt.AlignHCenter
            }
            // ── Heading ─────────────────────────────────────────────────────
                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "Sign in to PlantDoctor"
                            font.family: "Georgia"
                            font.pixelSize: 26
                            font.bold: true
                            color: "#1A2E1F"
                            font.letterSpacing: 0.3
                        }

                        Item { Layout.preferredHeight: 70 }
                        // ── Card ─────────────────────────────────────────────────────────
                                    Rectangle {
                                        Layout.leftMargin: 20
                                        Layout.rightMargin: 20
                                        Layout.fillWidth: true
                                        implicitHeight: cardColumn.implicitHeight + 36
                                        radius: 20
                                        color: "#FFFFFF"
                                        border.color: "#000000"
                                        border.width: 1


                                        ColumnLayout {
                                            id: cardColumn
                                            anchors {
                                                top: parent.top; left: parent.left; right: parent.right
                                                topMargin: 28; leftMargin: 20; rightMargin: 20
                                            }
                                            spacing: 16
        }
}

}
}
}
