import QtQuick 2.15
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    property string label
    property string value
    property int labelWidth: 110
    property int valueWidth: 0

    Layout.fillWidth: true
    spacing: 8

    Label {
        text: label
        color: "#64748b"
        Layout.preferredWidth: labelWidth
        elide: Text.ElideRight
    }

    Label {
        text: value
        font.weight: Font.Medium
        Layout.fillWidth: true
        Layout.preferredWidth: valueWidth > 0 ? valueWidth : -1
        horizontalAlignment: Text.AlignRight
        elide: Text.ElideRight
        color: value === "N/A" ? "#94a3b8" : "#1e293b"
    }
}
