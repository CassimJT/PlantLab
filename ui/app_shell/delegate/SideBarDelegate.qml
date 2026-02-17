import QtQuick 2.15
import QtQuick.Controls 2.15

ItemDelegate {
    padding: 10
    leftPadding: 15
    id: root
    width: ListView.view.width
    height: 48
    property int indexInView: index
    //signal clicked(var pageStack)
    highlighted: ListView.view.currentIndex === indexInView
    onClicked: {
        ListView.view.currentIndex = indexInView
        pageStack.currentIndex = indexInView
    }

    icon.source: iconSource
    icon.width: 24
    icon.height: 24
    icon.color: root.highlighted ? "#0284c7"
               : root.hovered   ? "#0ea5e9"
                                : "#475569"

    text: label

    background: Rectangle {
        color: root.highlighted ? "#e0f2fe"
             : root.hovered   ? "#f1f5f9"
                              : "transparent"
        radius: 8
    }
}
