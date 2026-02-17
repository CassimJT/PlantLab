import QtQuick
import QtQuick.Controls 2.15
import QtQuick.Layouts

Page {
    id: root
    property string currentPath: fileController?.rootPath || ""
    signal itemClicked()
    signal imageSelected(string path)

    // ===== SIMPLE PATH HEADER =====
    Rectangle {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 48
        color: "#f5f5f5"
        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 16
            anchors.rightMargin: 16
            spacing: 12

            Button {
                text: "←"
                // Only enable if we're not at home
                enabled: fileController?.rootPath &&
                         fileController.rootPath !== fileController?.homePath
                onClicked: fileController?.goUp()
                flat: true
            }

            Text {
                text: fileController?.rootPath || "Home"
                elide: Text.ElideLeft
                font.pixelSize: 14
                color: "#333333"
                Layout.fillWidth: true
                verticalAlignment: Text.AlignVCenter
            }

            Button {
                text: "↻"
                onClicked: fileController?.refresh()
                flat: true
            }
        }
    }

    // ===== STANDARD TREEVIEW =====
    TreeView {
        id: treeView
        anchors {
            top: header.bottom
            right: parent.right
            left: parent.left
            bottom: parent.bottom
        }

        clip: true
        model: fileController?.model || null
        rootIndex: fileController?.rootIndex || null

        selectionModel: ItemSelectionModel {
            model: treeView.model
        }

        delegate: TreeViewDelegate {
            id: delegate
            text: model.fileName || model.display || "Unknown"
            leftMargin: 8

            // Helper to check if file is an image
            function isImageFile(filename) {
                if (!filename) return false
                var imageExtensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"]
                var lower = filename.toLowerCase()
                for (var i = 0; i < imageExtensions.length; i++) {
                    if (lower.endsWith(imageExtensions[i])) return true
                }
                return false
            }

            // Get full file path
            function getFilePath() {
                var idx = treeView.model.index(row, 0, treeView.rootIndex)
                return fileController?.filePath(idx) || ""
            }

            background: Rectangle {
                color: delegate.pressed
                       ? "#e2e8f0"
                       : delegate.highlighted
                         ? "#dbeafe"
                         : delegate.hovered
                           ? "#f1f5f9"
                           : (delegate.row % 2 === 0 ? "#f8fafc" : "#ffffff")
            }

            contentItem: Item {
                implicitHeight: 40

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    spacing: 8

                    Text {
                        text: delegate.text
                        font: delegate.font
                        color: "#333333"
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                        verticalAlignment: Text.AlignVCenter
                    }
                    //icon (optional)
                    //..
                }
            }

            // Handle clicks
            onClicked: {
                var path = getFilePath()
                if (!path) return

                // Check if it's a directory
                var idx = treeView.model.index(row, 0, treeView.rootIndex)
                var isDir = fileController?.isDir(idx) || false

                if (isDir) {
                    // Navigate into directory
                    fileController?.setRootFolder(path)
                } else if (delegate.isImageFile(delegate.text)) {
                    // Preview image
                    console.log("Previewing image:", path)
                    fileController?.setCurrentImage(path)
                    root.imageSelected(path)
                } else {
                    // Non-image file - maybe show properties or do nothing
                    console.log("Clicked non-image file:", path)
                }
            }
        }

        columnWidthProvider: function(column) {
            return column === 0 ? treeView.width : 0
        }
    }

    // Show message when no folder is selected
    Rectangle {
        width: parent.width
        height: parent.height * 0.5
        anchors.centerIn: parent
        visible: !fileController?.rootPath || fileController?.rootPath === ""
        color: "#ffffff"

        Text {
            anchors.centerIn: parent
            text: "No folder selected"
            font.pixelSize: 16
            color: "#666666"
        }
    }

    // ===== NAVIGATION FUNCTIONS =====
    function setFolder(path) {
        if (fileController) fileController.setRootFolder(path)
    }

    function goUp() {
        if (fileController) fileController.goUp()
    }

    function refresh() {
        if (fileController) fileController.refresh()
    }

    // ===== MODEL CONNECTIONS =====
    Connections {
        target: fileController
        function onRootPathChanged(path) {
            currentPath = path
            console.log("Path changed:", path)
        }

        function onDirectoryLoaded(path) {
            console.log("Loaded:", path)
        }
    }

    Component.onCompleted: {
        console.log("FileView ready")
        if (fileController) {
            console.log("Root path:", fileController.rootPath)
        }
    }
}
