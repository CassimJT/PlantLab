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
        visible: listView.count > 0

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 15
            anchors.rightMargin: 10
            spacing: 8

            Label {
                text: "Models";
                Layout.fillWidth: true;
                font.bold: true
            }

            // Refresh button
            Button {
                text: "⟳"  // Using a refresh symbol
                flat: true
                implicitWidth: 30
                implicitHeight: 30
                ToolTip.visible: hovered
                ToolTip.text: "Refresh model list"

                onClicked: {
                    if (ModelScanner) {
                        ModelScanner.refresh()
                    } else if (ModelList && ModelList.refresh) {
                        ModelList.refresh()
                    }
                }
            }
        }
    }

    MenuSeparator {
        id: menuSeparator
        width: parent.width
        anchors.top: heading.bottom
        visible: listView.count > 0
    }

    // Simple empty state
    Label {
        anchors.centerIn: parent
        text: "No models available"
        color: "#94a3b8"
        font.pixelSize: 14
        visible: listView.count === 0
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
        visible: listView.count > 0
        clip: true
        model: ModelList
        delegate: AvailableModelDelegate {
            highlighted: ListView.isCurrentItem
        }
    }
}
