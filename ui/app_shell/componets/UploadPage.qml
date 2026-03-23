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
            color: InfarenceRunner.is_model_loaded ? "#64748b" : "#dc2626"

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
            opacity: enabled ? 1.0 : 0.5

            selectedImagePath: root.selectedImagePath

            // Connect the signal to update root's selectedImagePath
            onImageSelected: function(path) {
                console.log("DropZone onImageSelected called with path:", path)
                root.selectedImagePath = path
            }
        }

        /* ======================
           ANALYZE BUTTON
           ====================== */
        Button {
            id: analyzeButton
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 220
            Layout.preferredHeight: 50

            text: root.isProcessing ? "Analyzing..." : "Analyze"

            enabled: root.selectedImagePath !== "" &&
                     InfarenceRunner.is_model_loaded &&
                     !root.isProcessing

            onClicked: {
                console.log("Analyze button clicked with selectedImagePath:", root.selectedImagePath)
                root.analyzeClicked()
            }
        }

        Item { Layout.fillHeight: true }
    }
}