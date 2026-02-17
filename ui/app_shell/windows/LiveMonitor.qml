import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls

Window {
    width: 800
    height: 600
    visible: true
    title: "Live Pest Monitor"

    modality: Qt.ApplicationModal
    flags: Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint
    BusyIndicator {
        anchors.centerIn: parent
    }
}
