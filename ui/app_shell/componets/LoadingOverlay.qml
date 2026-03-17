import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    property string message: ""

    anchors.fill: parent
    color: "#80000000"
    visible: false

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 24

        BusyIndicator {
            running: parent.parent.visible
            width: 60
            height: 60
            Layout.alignment: Qt.AlignHCenter
        }

        Text {
            text: message
            font.pixelSize: 18
            font.bold: true
            color: "white"
            Layout.alignment: Qt.AlignHCenter
        }

        Text {
            text: qsTr("Please wait")
            color: "#e2e8f0"
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
