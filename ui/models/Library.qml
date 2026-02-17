import QtQuick 2.15
import QtQuick.Controls
import QtQuick.Layouts
import "./delagete"
import "./model"
Page {
    id: root
     property var selectedModel: listView.currentIndex >= 0 ? listView.model.get(listView.currentIndex) : null

    Rectangle {
        id: heading
        width: parent.width
        height: 40
        color: "#f1f5f9"

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 15
            anchors.rightMargin: 10
            spacing: 8

            Label { text: "Model"; Layout.fillWidth: true; font.bold: true }
            Label { text: "Frameworks"; Layout.preferredWidth: 105; font.bold: true }
            Label { text: "Size"; Layout.preferredWidth: 65; font.bold: true }
        }
    }

    MenuSeparator {
        id: menuSeparator
        width: parent.width
        anchors {
            top: heading.bottom
        }
    }

    ListView {
        id: listView
        anchors {
            top: menuSeparator.bottom
            left: parent.left
            right: parent.right
            bottom: parent.bottom
            topMargin: 5
            margins: 10
        }

        clip: true
        model: AvailableModel {}
        delegate: AvailableModelDelegate {
            highlighted: ListView.isCurrentItem
        }
    }
}
