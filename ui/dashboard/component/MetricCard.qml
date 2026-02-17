import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    //propeties
    property string title
    property string value
    property string icon
    default property alias content: contentLoader.sourceComponent
    property color border_color: "#bae6fd"
    property color cardColor: "#ffffff"
    property real cardWidth: 200
    property real cardHight: 200
    property real cardRadius: 14

    //defalt values
    width: root.cardWidth
    height: root.cardHight
    color: root.cardColor
    radius: root.cardRadius
    border.color: root.border_color

    ColumnLayout {
        anchors.fill: parent
        spacing: 6

        RowLayout {
            Layout.fillWidth: true

            Text {
                text: root.icon
                font.pixelSize: 20
            }

            Text {
                text: root.title
                font.pixelSize: 14
                font.bold: true
                color: "#334155"
            }

            Item { Layout.fillWidth: true }

            Text {
                text: root.value
                font.pixelSize: 16
                font.bold: true
                color: "#0284c7"
            }
        }

        Loader {
            id: contentLoader
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}
