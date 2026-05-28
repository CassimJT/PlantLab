import QtQuick 2.15
import QtQuick.Controls 2.15

Popup {
    id: messageBox
    width: 300
    height: 150
    modal: true
    focus: true
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    property string title: "Message"
    property string message: ""
    property string type: "info" // info, error, warning, success

    // Colors based on type
    property color titleColor: {
        switch(type) {
            case "error": return "#f44336"
            case "warning": return "#ff9800"
            case "success": return "#4caf50"
            default: return "#2196f3"
        }
    }

    // Function to show message
    function show(msg, msgType) {
        message = msg
        type = msgType || "info"
        open()
    }

    function showError(msg) {
        show(msg, "error")
    }

    function showSuccess(msg) {
        show(msg, "success")
    }

    function showWarning(msg) {
        show(msg, "warning")
    }

    function showInfo(msg) {
        show(msg, "info")
    }

    background: Rectangle {
        color: "white"
        radius: 8
        border.color: "#ccc"
        border.width: 1
    }

    contentItem: Column {
        spacing: 15
        anchors.fill: parent
        anchors.margins: 15

        // Header
        Rectangle {
            width: parent.width
            height: 30
            color: "transparent"

            Row {
                spacing: 10

                Rectangle {
                    width: 24
                    height: 24
                    radius: 12
                    color: messageBox.titleColor

                    Text {
                        anchors.centerIn: parent
                        text: {
                            if (type === "error") return "!"
                            if (type === "success") return "✓"
                            if (type === "warning") return "⚠"
                            return "i"
                        }
                        color: "white"
                        font.bold: true
                        font.pixelSize: 14
                    }
                }

                Text {
                    text: {
                        if (type === "error") return "Error"
                        if (type === "success") return "Success"
                        if (type === "warning") return "Warning"
                        return "Information"
                    }
                    font.bold: true
                    font.pixelSize: 14
                    color: messageBox.titleColor
                }
            }
        }

        // Message
        Text {
            width: parent.width
            text: message
            wrapMode: Text.WordWrap
            font.pixelSize: 12
            color: "#333"
        }

        // OK Button
        Rectangle {
            width: parent.width
            height: 35
            radius: 5
            color: messageBox.titleColor

            Text {
                anchors.centerIn: parent
                text: "OK"
                color: "white"
                font.bold: true
                font.pixelSize: 12
            }

            MouseArea {
                anchors.fill: parent
                onClicked: messageBox.close()
            }
        }
    }
}