import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    property string title: ""
    property string icon: ""
    property string content: ""

    Layout.fillWidth: true
    Layout.preferredHeight: 150
    color: "#fafafa"
    radius: 12
    border.color: "#e2e8f0"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 8

        RowLayout {
            spacing: 8
            Text { text: icon; font.pixelSize: 16 }
            Text {
                text: title
                font.bold: true
                color: "#334155"
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            TextArea {
                text: content
                wrapMode: Text.WordWrap
                readOnly: true
                background: null
                font.pixelSize: 14
                color: "#475569"
                selectByMouse: true
            }
        }
    }
}
