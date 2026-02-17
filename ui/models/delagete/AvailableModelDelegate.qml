import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ItemDelegate {
    id: itemDelegate
    width: ListView.view.width
    height: 44
    hoverEnabled: true

    highlighted: ListView.isCurrentItem
    onClicked: ListView.view.currentIndex = index

    background: Rectangle {
        radius: 6
        color: itemDelegate.pressed
               ? "#e2e8f0"
               : itemDelegate.highlighted
                 ? "#dbeafe"
                 : itemDelegate.hovered
                   ? "#f1f5f9"
                   : index % 2 === 0
                     ? "#f8fafc"
                     : "#ffffff"
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 6
        spacing: 8

        Label {
            text: model.name
            Layout.fillWidth: true
            elide: Text.ElideRight
            font.weight: itemDelegate.highlighted ? Font.Medium : Font.Normal
            color: itemDelegate.highlighted ? "#1e3a8a" : "#334155"
        }

        Label {
            text: model.framework
            Layout.preferredWidth: 100
            horizontalAlignment: Text.AlignLeft
            color: "#475569"
        }

        Label {
            text: model._size
            Layout.preferredWidth: 60
            horizontalAlignment: Text.AlignLeft
            color: "#64748b"
        }
    }
}
