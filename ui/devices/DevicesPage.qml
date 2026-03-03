import QtQuick 2.15
import QtQuick.Controls 2.15
import "./delegate"
import "./model"

Page {
    id: devicesPage
    background: Rectangle {
      color: "#f5f7fb"

    }
    padding: 20
    GridView {
        id: gridView
        cellWidth: 200
        cellHeight: 200
        anchors {
            right: parent.right
            left: parent.left
            bottom: parent.bottom
            top: parent.top
            margins: 15
            leftMargin: 30
        }

        model: DeviceModel{}
        delegate: DeviceDelegate{}
    }

}
