import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true

    //propeties
    property string title
    property color backgroundColor: "#ffffff"
    property real borderRadius: 14
    property color borderColor: "#bae6fd"
    property real chartWidth: parent.width
    property real chartHeigh: 300

    //defailt values
    color: root.backgroundColor
    radius: root.borderRadius
    border.color: root.borderColor
    width: root.chartWidth
    height: root.chartHeigh


}
