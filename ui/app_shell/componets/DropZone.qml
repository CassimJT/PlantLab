import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs

Rectangle {
    id: root

    property string selectedImagePath: ""
    property bool isDragging: false
    property alias dropEnabled: dropArea.enabled

    signal imageSelected(string path)

    radius: 16

    color: isDragging ? "#f0f9ff" : "#ffffff"
    border.color: isDragging ? "#0284c7" : "#e2e8f0"
    border.width: isDragging ? 2 : 1

    /* =========================
       Upload UI
       ========================= */
    ColumnLayout {
        anchors.centerIn: parent
        spacing: 20
        width: parent.width - 40

        visible: root.selectedImagePath === ""

        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            width: 80
            height: 80
            radius: 40
            color: "#f1f5f9"

            Text {
                anchors.centerIn: parent
                text: "📷"
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
       Image Preview - FIXED for Desktop
       ========================= */
    Image {
        id: previewImage
        anchors.fill: parent
        anchors.margins: 20
        visible: root.selectedImagePath !== ""
        fillMode: Image.PreserveAspectFit

        // For desktop, use file:// prefix with local path
        source: root.selectedImagePath !== ""
                ? "file://" + root.selectedImagePath
                : ""

        cache: false

        onStatusChanged: {
            if (status === Image.Error) {
                console.log("Failed to load image:", source)
            } else if (status === Image.Ready) {
                console.log("Image loaded successfully:", source)
            }
        }
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
        visible: root.selectedImagePath !== ""
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
       Drag & Drop - FIXED for Desktop
       ========================= */
    DropArea {
        id: dropArea
        anchors.fill: parent

        onEntered: root.isDragging = true
        onExited: root.isDragging = false

        onDropped: function(drop) {
            root.isDragging = false

            if (!drop.hasUrls || drop.urls.length === 0) {
                console.log("No URLs in drop")
                return
            }

            var url = drop.urls[0]
            console.log("Dropped URL:", url.toString())

            // Convert to local file path
            var path = ""

            // Handle different URL formats
            if (url.toString().startsWith("file://")) {
                // Use Qt.resolvedUrl to get proper path
                var qurl = Qt.resolvedUrl(url)
                path = qurl.toString()

                // Remove file:// prefix if present
                if (path.startsWith("file://")) {
                    path = path.substring(7)
                }
            } else {
                path = url.toString()
            }

            // Decode URL encoding
            path = decodeURIComponent(path)

            // Remove query parameters and fragments
            if (path.indexOf('?') !== -1) {
                path = path.substring(0, path.indexOf('?'))
            }
            if (path.indexOf('#') !== -1) {
                path = path.substring(0, path.indexOf('#'))
            }

            console.log("Extracted path:", path)

            // Make sure we have a valid path
            if (path && path.length > 0) {
                root.selectedImagePath = path
                root.imageSelected(path)  // Emit the signal with the path
            } else {
                console.log("Warning: Empty path extracted from URL:", url.toString())
            }
        }
    }

    /* =========================
       File Dialog - FIXED for Desktop
       ========================= */
    FileDialog {
        id: fileDialog
        title: qsTr("Select Image")

        nameFilters: [
            "Image files (*.png *.jpg *.jpeg *.bmp *.gif)",
            "All files (*)"
        ]

        onAccepted: {
            var url = fileDialog.selectedFile
            console.log("Selected file URL:", url)

            // Convert to local path
            var path = url.toString()

            // Remove file:// prefix if present
            if (path.startsWith("file://")) {
                path = path.substring(7)  // Remove "file://"
            }

            console.log("Extracted path:", path)

            root.selectedImagePath = path
            root.imageSelected(path)
        }
    }
}