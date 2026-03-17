import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs

Rectangle {
    id: root

    property string selectedImagePath: ""
    property alias dropEnabled: dropArea.enabled

    signal imageSelected(string path)

    radius: 16

    color: dropArea.containsDrag ? "#f0f9ff" : "#ffffff"
    border.color: dropArea.containsDrag ? "#0284c7" : "#e2e8f0"
    border.width: dropArea.containsDrag ? 2 : 1

    /* =========================
       Upload UI
       ========================= */
    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20
        width: parent.width - 40
        visible: root.selectedImagePath.length === 0

        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            width: 80
            height: 80
            radius: 40
            color: "#f1f5f9"

            Text {
                anchors.centerIn: parent
                text: "📷" //to be replaced with an acture image
                font.pixelSize: 40
            }
        }

        Text {
            text: qsTr("Drag & Drop Image Here")
            font.pixelSize: 16
            color: "#64748b"

            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true

            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
        }

        Button {
            text: qsTr("Browse Files")
            Layout.alignment: Qt.AlignHCenter
            flat: true

            contentItem: Text {
                text: parent.text
                color: "#0284c7"
                font.underline: true
            }

            background: Rectangle { color: "transparent" }

            onClicked: fileDialog.open()
        }
    }

    /* =========================
       Image Preview
       ========================= */
    Image {
        anchors.fill: parent
        anchors.margins: 20

        visible: root.selectedImagePath.length > 0
        fillMode: Image.PreserveAspectFit

        source: root.selectedImagePath.length > 0
                ? Qt.resolvedUrl("file://" + root.selectedImagePath)
                : ""
    }

    /* =========================
       Remove Button
       ========================= */
    Button {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 10

        width: 36
        height: 36

        visible: root.selectedImagePath.length > 0
        flat: true
        text: "✕"

        background: Rectangle {
            radius: 18
            color: parent.hovered ? "#fee2e2" : "#ffffff"
            border.color: "#fecaca"
        }

        onClicked: {
            root.selectedImagePath = ""
            root.imageSelected("")
        }
    }

    /* =========================
       Drag & Drop
       ========================= */
    DropArea {
        id: dropArea
        anchors.fill: parent

        onDropped: function(drop) {

            if (!drop.hasUrls || drop.urls.length === 0)
                return

            var url = drop.urls[0]

            if (url.scheme === "file") {
                var path = url.toString().replace("file://", "")
                root.selectedImagePath = path
                root.imageSelected(path)
            }
        }
    }

    /* =========================
       File Dialog
       ========================= */
    FileDialog {
        id: fileDialog
        title: qsTr("Select Image")

        nameFilters: [
            "Image files (*.png *.jpg *.jpeg *.bmp)",
            "All files (*)"
        ]

        onAccepted: {
            var path = fileDialog.fileUrl.toString().replace("file://", "")
            root.selectedImagePath = path
            root.imageSelected(path)
        }
    }
}
