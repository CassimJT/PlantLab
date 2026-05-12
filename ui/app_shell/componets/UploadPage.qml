import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    property string selectedImagePath: ""
    property bool isProcessing: false
    signal analyzeClicked()

    // Debug: Monitor path changes
    onSelectedImagePathChanged: {
        console.log("UploadPage.root.selectedImagePath changed to:", selectedImagePath)
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 40
        spacing: 30

        /* ======================
           TITLE / STATE MESSAGE
           ====================== */
        Text {
            text: InfarenceRunner.is_model_loaded
                  ? "Upload plant image"
                  : "Load a model first"
            font.pixelSize: 18
            color: InfarenceRunner.is_model_loaded ? "#94a3b8" : "#f87171"
            Layout.alignment: Qt.AlignHCenter
        }

        /* ======================
           DROP ZONE
           ====================== */
        DropZone {
            id: dropZone
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 500
            Layout.preferredHeight: 300
            enabled: InfarenceRunner.is_model_loaded
            opacity: enabled ? 1.0 : 0.4
            selectedImagePath: root.selectedImagePath
            onImageSelected: function(path) {
                console.log("DropZone onImageSelected called with path:", path)
                root.selectedImagePath = path
            }
        }

        /* ======================
           ANALYZE BUTTON
           ====================== */
        Rectangle {
            id: analyzeButton
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 220
            height: 44
            radius: 10

            // Mirrors enabled logic from original Button
            property bool isEnabled: root.selectedImagePath !== "" &&
                                     InfarenceRunner.is_model_loaded &&
                                     !root.isProcessing

            color: {
                if (!isEnabled)       return "#1e2741"
                if (analyzeHover.containsMouse) return "#3d4fd6"
                return "#4f6ef7"
            }

            border.color: {
                if (!isEnabled) return "#2d3550"
                if (analyzeHover.containsMouse) return "#6b84f9"
                return "transparent"
            }
            border.width: 1

            opacity: isEnabled ? 1.0 : 0.5

            Behavior on color   { ColorAnimation { duration: 150 } }
            Behavior on opacity { NumberAnimation { duration: 150 } }

            // Spinning dot when processing
            Row {
                anchors.centerIn: parent
                spacing: 8

                Rectangle {
                    visible: root.isProcessing
                    width: 8; height: 8; radius: 4
                    color: "#93c5fd"
                    anchors.verticalCenter: parent.verticalCenter

                    SequentialAnimation on opacity {
                        running: root.isProcessing
                        loops: Animation.Infinite
                        NumberAnimation { to: 0.2; duration: 500 }
                        NumberAnimation { to: 1.0; duration: 500 }
                    }
                }

                Text {
                    text: root.isProcessing ? "Analyzing..." : "Analyze"
                    color: analyzeButton.isEnabled ? "#ffffff" : "#4b5880"
                    font.pixelSize: 14
                    font.weight: Font.Medium
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            HoverHandler {
                id: analyzeHover
                enabled: analyzeButton.isEnabled
            }

            TapHandler {
                enabled: analyzeButton.isEnabled
                onTapped: {
                    console.log("Analyze button clicked with selectedImagePath:", root.selectedImagePath)
                    root.analyzeClicked()
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}