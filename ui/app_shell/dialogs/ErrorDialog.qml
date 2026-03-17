import QtQuick 2.15
import QtQuick.Controls 2.15

Dialog {
    id: root
    title: qsTr("Error")
    standardButtons: Dialog.Ok
    modal: true

    Label {
        text: "Failed to process image. Please try again."
        wrapMode: Text.WordWrap
        width: 300
    }
}
