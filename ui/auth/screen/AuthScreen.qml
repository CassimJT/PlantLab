import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls
import QtQuick.Layouts

Window {
    id: authWindow
    width: 450
    height: 750
    visible: true
    title: "Auth"

    modality: Qt.ApplicationModal
    flags: Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint
    color: "#edf2e0"

    Loader {
        id: authLoader
        anchors.centerIn: parent
        source: "../componets/SignIn.qml"  // Path from screen to componets

        onLoaded: {
            if (item) {
                // Pass reference to the component
                item.authLoader = authLoader
            }
        }
    }
}