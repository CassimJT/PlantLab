import QtQuick 2.15
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    property string label
    property string value

    Layout.fillWidth: true
    spacing: 8

    Label {
        text: label
        color: "#64748b"
        Layout.preferredWidth: 110
        elide: Text.ElideRight
    }

    Label {
        text: value
        font.weight: Font.Medium
        Layout.fillWidth: true
        horizontalAlignment: Text.AlignRight
        elide: Text.ElideRight
    }
}
