import QtQuick 2.15
import QtQuick.Controls 2.15

ItemDelegate {
    id: root
    padding: 10
    leftPadding: 15
    width: ListView.view.width
    height: 60
    property int indexInView: index
    highlighted: ListView.view.currentIndex === indexInView

    onClicked: {
        ListView.view.currentIndex = indexInView
    }

    icon.source: iconSource
    icon.width: 26
    icon.height: 26
    icon.color: root.highlighted ? "#0284c7"
                                 : root.hovered   ? "#0ea5e9"
                                                  : "#475569"

    text: model.title
    display: parent.width < 80
             ? AbstractButton.IconOnly
             : AbstractButton.TextUnderIcon

    // ===== Custom tooltip =====
    Popup {
        id: tip
        x: root.width + 8
        y: (root.height - height) / 2
        padding: 8
        modal: false
        focus: false
        closePolicy: Popup.NoAutoClose
        visible: root.hovered && display === AbstractButton.IconOnly

        background: Rectangle {
            radius: 6
            color: "#0f172a"
        }

        contentItem: Label {
            text: model.title
            color: "white"
            font.pixelSize: 12
        }
    }

    background: Rectangle {
        color: root.highlighted ? "#e0f2fe"
                                : root.hovered   ? "#f1f5f9"
                                                 : "transparent"
        radius: 8
    }
}
