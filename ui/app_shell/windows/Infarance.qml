import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import "../componets"
import "../dialogs"

Window {
    id: root
    width: 1000
    height: 700
    minimumWidth: 800
    minimumHeight: 600
    visible: true
    title: "Plant Disease Inference"

    flags: Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint

    // Properties
    property int currentPage: 0  // 0: upload, 1: results
    property string selectedImagePath: ""
    property bool isProcessing: false

    // Language strings
    readonly property var strings: {
        "en": {
            "title": "Plant Disease Detector",
            "upload_title": "Upload Plant Image",
            "results_title": "Analysis Results",
            "language": "Language",
            "english": "English",
            "chichewa": "Chichewa"
        },
        "ny": {
            "title": "Chizindikiro cha Matenda a Mmera",
            "upload_title": "Kwezani Chithunzi cha Mmera",
            "results_title": "Zotsatira Zofufuza",
            "language": "Chilankhulo",
            "english": "Chingerezi",
            "chichewa": "Chichewa"
        }
    }

    function _(key) {
        return strings[InfarenceRunner.current_language()]?.[key] || strings["en"][key] || key
    }

    // Background
    Rectangle {
        anchors.fill: parent
        color: "#f8fafc"
    }

    // Header
    Header {
        id: header
        width: parent.width
        titleText: _("title")
        subtitleText: currentPage === 0 ? _("upload_title") : _("results_title")
    }

    // Main content
    Rectangle {
        anchors.top: header.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        color: "transparent"

        // Page 0: Upload
        Loader {
            anchors.fill: parent
            sourceComponent: uploadPage
            active: currentPage === 0
        }

        // Page 1: Results
        Loader {
            anchors.fill: parent
            sourceComponent: resultsPage
            active: currentPage === 1
        }
    }

    // Upload Page Component
    Component {
        id: uploadPage
        UploadPage {
            selectedImagePath: root.selectedImagePath
            isProcessing: root.isProcessing
            onImageSelected: (path) => root.selectedImagePath = path
            onAnalyzeClicked: {
                root.isProcessing = true
                InfarenceRunner.classify_image_from_file(root.selectedImagePath)
            }
        }
    }

    // Results Page Component
    Component {
        id: resultsPage
        ResultsPage {
            selectedImagePath: root.selectedImagePath
            onNewAnalysis: {
                root.selectedImagePath = ""
                root.currentPage = 0
            }
        }
    }

    // Error Dialog
    ErrorDialog {
        id: errorDialog
    }

    // Loading Overlay
    LoadingOverlay {
        visible: root.isProcessing
        message: _("analyzing")
    }

    // Connections to C++ backend
    Connections {
        target: InfarenceRunner

        function onInferenceFinished() {
            root.isProcessing = false
            root.currentPage = 1
        }

        function onInferenceFailed(error) {
            root.isProcessing = false
            errorDialog.open()
        }
    }
}
