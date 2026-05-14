import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    objectName: "SignUp"
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

            Item { Layout.preferredHeight: 85 }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 72
                text: "Sign Up To PlantDoctor"
                font.family: "Georgia"
                font.pixelSize: 26
                color: "#1A2E1F"
                font.bold: true
                font.letterSpacing: 0.3
            }

            Item { Layout.preferredHeight: 60 }
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
