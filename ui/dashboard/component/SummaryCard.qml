import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    //properties
    property string title: ""
    property string icon: ""
    default property alias content: contentLoader.sourceComponent
    property color border_color: "#bae6fd"
    property color cardColor: "#ffffff"
    property real cardWidth: 200
    property real cardHeight: 200
    property real cardRadius: 14
    property string top_deseas: ""
    property string top_rigeon: ""

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
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignCenter
            sourceComponent: contentComponent
        }
    }

    // Default content component showing two metrics
    Component {
        id: contentComponent
        Column {
            anchors.centerIn: parent
            spacing: 12
            width: parent.width

            // Top Disease
            Rectangle {
                width: parent.width - 20
                height: 50
                color: "#FEF2F2"
                radius: 8
                anchors.horizontalCenter: parent.horizontalCenter

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 8

                    Column {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            text: "Top Disease"
                            font.pixelSize: 16
                            color: "#6B7280"
                        }
                        Text {
                            id: topDiseaseText
                            text: root.top_deseas
                            font.pixelSize: 13
                            font.bold: true
                            color: "#EF4444"
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }

            // Most Affected Region
            Rectangle {
                width: parent.width - 20
                height: 50
                color: "#EFF6FF"
                radius: 8
                anchors.horizontalCenter: parent.horizontalCenter

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 8

                    Column {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            text: "Most Affected Region"
                            font.pixelSize: 16
                            color: "#6B7280"
                        }
                        Text {
                            id: regionText
                            text: root.top_rigeon
                            font.pixelSize: 13
                            font.bold: true
                            color: "#333"
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }
    }

    // Functions to update the content
    function updateData(topDisease, mostAffectedRegion) {
        topDiseaseText.text = topDisease || "—"
        regionText.text = mostAffectedRegion || "—"
    }
}