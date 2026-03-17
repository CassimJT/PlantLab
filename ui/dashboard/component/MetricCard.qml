import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    //properties
    property string title
    property string value
    property string icon
    default property alias content: contentLoader.sourceComponent
    property color border_color: "#bae6fd"
    property color cardColor: "#ffffff"
    property real cardWidth: 200
    property real cardHeight: 200
    property real cardRadius: 14

    //default values
    width: root.cardWidth
    height: root.cardHeight
    color: root.cardColor
    radius: root.cardRadius
    border.color: root.border_color

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 6

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 20

            Text {
                text: root.title
                font.pixelSize: 14
                font.bold: true
                color: "#334155"
                Layout.fillWidth: true
                elide: Text.ElideRight
            }

        }

        Loader {
            id: contentLoader
            Layout.preferredWidth: parent.width * 0.35
            Layout.preferredHeight: parent.width * 0.35
            Layout.alignment: Qt.AlignCenter
        }
    }
}
