import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs
import "./componets"

Page {
    id: rootPage

    // =============================
    // GLOBAL IMAGE STATE
    // =============================
    property string selectedImagePath: ""
    property bool hasImage: selectedImagePath.length > 0

    SplitView {
        anchors.fill: parent
        orientation: Qt.Horizontal
        anchors.margins: 10

        // =============================
        // SPLIT HANDLE
        // =============================
        handle: Rectangle {
            implicitWidth: 4
            height: parent.height
            color: "transparent"

            Row {
                anchors.centerIn: parent
                spacing: 3
                Repeater {
                    model: 1
                    Rectangle {
                        width: 3
                        height: 20
                        radius: 1.5
                        color: "#64748b"
                    }
                }
            }
        }

        // =============================
        // CENTRAL AREA
        // =============================
        Rectangle {
            SplitView.minimumWidth: 50
            SplitView.fillWidth: true
            color: "#f5f7fb"

            // -----------------------------
            // DROP AREA
            // -----------------------------
            Rectangle {
                id: dropBx
                anchors.fill: parent
                visible: !rootPage.hasImage
                z: 1

                radius: 8
                border.color: dropArea.containsDrag ? "#3b82f6" : "#cbd5e1"
                border.width: 1
                color: "transparent"

                DropArea {
                    id: dropArea
                    anchors.fill: parent

                    onDropped: (drop) => {
                                   if (drop.urls.length > 0) {
                                       let localPath = drop.urls[0]
                                       .toString()
                                       .replace(/^file:\/\//, "")

                                       fileController.setRootFolder(localPath)
                                       fileView.setFolder(localPath)
                                   }
                               }
                }

                ColumnLayout {
                    anchors.centerIn: parent
                    spacing: 12

                    Label {
                        text: dropArea.containsDrag
                              ? "Release to load folder"
                              : "Drag & drop a folder here"
                        font.pixelSize: 16
                        color: "#475569"
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Label {
                        text: "or"
                        color: "#94a3b8"
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Button {
                        text: "Browse folder"
                        display: AbstractButton.TextUnderIcon
                        Layout.alignment: Qt.AlignHCenter
                        onClicked: fileDialog.open()
                    }
                }
            }

            // -----------------------------
            // IMAGE PREVIEW AREA
            // -----------------------------
            RowLayout {
                id: previewArea
                anchors.fill: parent
                anchors.margins: 5
                spacing: 12
                visible: rootPage.hasImage
                z: 2

                // PREVIEW PANEL
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 8

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.alignment: Qt.AlignCenter
                        color: "#e2e8f0"
                        radius: 6

                        Image {
                            id: previewImage
                            anchors.fill: parent
                            anchors.margins: 12
                            fillMode: Image.PreserveAspectFit
                            asynchronous: true
                            cache: false
                            source: rootPage.selectedImagePath

                            // This triggers when image is loaded
                            onStatusChanged: {
                                if (status === Image.Ready) {
                                    console.log("Image loaded:", source, sourceSize.width, "x", sourceSize.height)
                                }
                            }
                        }
                    }

                    // Image info panel
                    RowLayout {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 30
                        Layout.leftMargin: 8
                        Layout.rightMargin: 8
                        spacing: 16

                        // Filename
                        Label {
                            text: {
                                if (!rootPage.selectedImagePath) return ""
                                var parts = rootPage.selectedImagePath.split("/")
                                return parts[parts.length - 1]
                            }
                            font.pixelSize: 12
                            color: "#475569"
                            elide: Text.ElideLeft
                            Layout.fillWidth: true
                        }

                        // Image dimensions
                        Label {
                            id: imageSizeLabel
                            text: {
                                if (previewImage.status === Image.Ready && previewImage.sourceSize.width > 0) {
                                    return previewImage.sourceSize.width + " × " + previewImage.sourceSize.height
                                }
                                return "Loading..."
                            }
                            font.pixelSize: 12
                            color: "#475569"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                        }

                        // File size
                        Label {
                            text: fileController?.currentImageSize || ""
                            font.pixelSize: 12
                            color: "#64748b"
                            horizontalAlignment: Text.AlignRight
                        }
                    }
                }

                // NAVIGATION
                ColumnLayout {
                    Layout.alignment: Qt.AlignVCenter
                    spacing: 10

                    RoundButton {
                        text: "↑"
                        enabled: fileController?.imageCount > 0
                        onClicked: fileController?.previousImage()
                    }

                    RoundButton {
                        text: "↓"
                        enabled: fileController?.imageCount > 0
                        onClicked: fileController?.nextImage()
                    }

                    Label {
                        text: fileController?.imageCount > 0
                              ? (fileController.currentIndex + 1) + " / " + fileController.imageCount
                              : ""
                        font.pixelSize: 12
                        color: "#475569"
                        Layout.alignment: Qt.AlignHCenter
                    }

                    // CLOSE FOLDER BUTTON
                    RoundButton {
                        text: "✕"
                        ToolTip.visible: hovered
                        ToolTip.text: "Close folder and return to drop area"
                        onClicked: clearFolder()
                        Layout.topMargin: 20

                        contentItem: Text {
                            text: parent.text
                            color: "#ef4444"
                            font.pixelSize: 16
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }
        }

        // =============================
        // SIDE PANEL
        // =============================
        Rectangle {
            implicitWidth: 280
            SplitView.maximumWidth: 400
            SplitView.minimumWidth: 270
            clip: true
            color: "#ffffff"

            TabBar {
                id: tabbar
                width: parent.width
                TabButton { text: qsTr("View") }
                TabButton { text: qsTr("Property") }
            }

            StackLayout {
                currentIndex: tabbar.currentIndex
                anchors {
                    top: tabbar.bottom
                    right: parent.right
                    left: parent.left
                    bottom: parent.bottom
                }

                FileView {
                    id: fileView

                    onImageSelected: function(path) {
                        console.log("Image selected from FileView:", path)
                    }
                }
                PropertySideBar {

                }

            }
        }
    }

    // =============================
    // FILE DIALOG
    // =============================
    FileDialog {
        id: fileDialog
        title: "Select folder"
        fileMode: FileDialog.Folder

        onAccepted: {
            if (selectedFolder) {
                let localPath = selectedFolder
                .toString()
                .replace("file://", "")

                fileController.setRootFolder(localPath)
                fileView.setFolder(localPath)
            }
        }
    }

    // =============================
    // CLEAR FOLDER FUNCTION
    // =============================
    function clearFolder() {
        console.log("Clearing folder...")
        selectedImagePath = ""
        if (fileController) {
            fileController.clearImageList()
        }
        console.log("Folder cleared, returning to drop area")
    }

    // =============================
    // CONTROLLER CONNECTION
    // =============================
    Connections {
        target: fileController

        function onImageSelected(path) {
            console.log("Controller image selected:", path)
            if (path && path.length > 0) {
                rootPage.selectedImagePath = "file://" + path
            } else {
                rootPage.selectedImagePath = ""
            }
        }
    }
}
