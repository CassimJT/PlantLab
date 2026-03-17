import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    property string diseaseName: ""

    Layout.fillWidth: true
    Layout.preferredHeight: 100
    color: "#f0f9ff"
    radius: 12
    border.color: "#bae6fd"

    RowLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16

        Rectangle {
            width: 48
            height: 48
            radius: 24
            color: "#0284c7"

            Text {
                anchors.centerIn: parent
                text: ""
                font.pixelSize: 24
            }
        }

        Column {
            spacing: 4
            Text {
                text: qsTr("Disease")
                font.pixelSize: 12
                color: "#64748b"
            }
            Text {
                text: diseaseName || "—"
                font.pixelSize: 20
                font.bold: true
                color: "#0f172a"
                wrapMode: Text.WordWrap
                width: parent.parent.width - 100
            }
        }
    }
}

