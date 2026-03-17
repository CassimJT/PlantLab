import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    property string title: ""
    property string value: ""
    property string icon: ""

    color: "#f8fafc"
    radius: 8
    border.color: "#e2e8f0"

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 4

        RowLayout {
            spacing: 4
            Layout.alignment: Qt.AlignHCenter

            Text { text: icon; font.pixelSize: 14 }
            Text {
                text: title
                font.pixelSize: 12
                color: "#64748b"
            }
        }

        Text {
            text: value
            font.pixelSize: 18
            font.bold: true
            color: "#0284c7"
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
