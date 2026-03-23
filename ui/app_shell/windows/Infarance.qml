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

    /* ======================
       STATE
       ====================== */
    property int currentPage: 0   // 0: upload, 1: results
    property string selectedImagePath: ""
    property bool isProcessing: false

    /* ======================
       TRANSLATIONS
       ====================== */
    readonly property var strings: {
        "en": {
            "title": "Plant Disease Detector",
            "upload_title": "Upload Plant Image",
            "results_title": "Analysis Results",
            "analyzing": "Analyzing..."
        },
        "ny": {
            "title": "Chizindikiro cha Matenda a Mmera",
            "upload_title": "Kwezani Chithunzi cha Mmera",
            "results_title": "Zotsatira Zofufuza",
            "analyzing": "Kufufuza..."
        }
    }

    function _(key) {
        return strings[InfarenceRunner.current_language]?.[key]
               || strings["en"][key]
               || key
    }

    /* ======================
       DEBUG: Monitor property changes
       ====================== */
    onCurrentPageChanged: {
        console.log("Main window currentPage changed to:", currentPage)
    }

    onSelectedImagePathChanged: {
        console.log("Main window selectedImagePath changed to:", selectedImagePath)
    }

    onIsProcessingChanged: {
        console.log("Main window isProcessing changed to:", isProcessing)
    }

    /* ======================
       BACKGROUND
       ====================== */
    Rectangle {
        anchors.fill: parent
        color: "#f8fafc"
    }

    /* ======================
       HEADER (FIXED)
       ====================== */
    Header {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right

        titleText: _("title")
        subtitleText: currentPage === 0
                        ? _("upload_title")
                        : _("results_title")
    }

    /* ======================
       CONTENT (FIXED)
       ====================== */
    Loader {
        id: pageLoader
        anchors.top: header.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        sourceComponent: currentPage === 0 ? uploadPage : resultsPage

        onSourceComponentChanged: {
            console.log("PageLoader sourceComponent changed to:",
                        sourceComponent === uploadPage ? "uploadPage" : "resultsPage")
        }
    }

    /* ======================
       UPLOAD PAGE
       ====================== */
    Component {
        id: uploadPage

        UploadPage {
            id: uploadPageInstance

            // Two-way binding for selectedImagePath
            selectedImagePath: root.selectedImagePath
            isProcessing: root.isProcessing

            onSelectedImagePathChanged: {
                console.log("UploadPage.selectedImagePath changed to:", selectedImagePath)
                if (root.selectedImagePath !== selectedImagePath) {
                    root.selectedImagePath = selectedImagePath
                }
            }

            onAnalyzeClicked: {
                console.log("UploadPage analyzeClicked - selectedImagePath:", selectedImagePath)
                if (selectedImagePath && selectedImagePath.length > 0) {
                    root.isProcessing = true
                    InfarenceRunner.classify_image_from_file(selectedImagePath)
                } else {
                    console.log("No image selected for analysis")
                    errorDialog.message = "Please select an image first"
                    errorDialog.open()
                }
            }
        }
    }

    /* ======================
       RESULTS PAGE
       ====================== */
    Component {
        id: resultsPage

        Rectangle {
            id: resultsContainer
            anchors.fill: parent
            anchors.margins: 40
            color: "white"
            radius: 16
            border.color: "#e2e8f0"

            // Debug: When this component is created
            Component.onCompleted: {
                console.log("ResultsPage component created")
                console.log("Disease name at creation:", InfarenceRunner.disease_name)
                console.log("Confidence at creation:", InfarenceRunner.confidence)
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 30
                spacing: 20

                // Image preview
                Rectangle {
                    Layout.preferredHeight: 200
                    Layout.fillWidth: true
                    color: "#f8fafc"
                    radius: 12

                    Image {
                        anchors.fill: parent
                        anchors.margins: 10
                        source: root.selectedImagePath ? "file://" + root.selectedImagePath : ""
                        fillMode: Image.PreserveAspectFit
                        cache: false
                    }
                }

                // Disease name
                Text {
                    text: InfarenceRunner.disease_name || "Unknown Disease"
                    font.pixelSize: 24
                    font.bold: true
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                    color: "#1e293b"
                }

                // Confidence
                Rectangle {
                    Layout.fillWidth: true
                    height: 40
                    color: "#f1f5f9"
                    radius: 8

                    Text {
                        anchors.centerIn: parent
                        text: "Confidence: " + (InfarenceRunner.confidence ? InfarenceRunner.confidence.toFixed(2) + "%" : "0%")
                        font.pixelSize: 16
                        color: InfarenceRunner.confidence > 70 ? "#10b981" : (InfarenceRunner.confidence > 40 ? "#f59e0b" : "#ef4444")
                    }
                }

                // Description
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Text {
                        text: "Description"
                        font.pixelSize: 18
                        font.bold: true
                        color: "#334155"
                    }

                    Text {
                        text: InfarenceRunner.description || "No description available"
                        font.pixelSize: 14
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                        color: "#475569"
                    }
                }

                // Cure / Treatment
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Text {
                        text: InfarenceRunner.current_category === "disease" ? "Treatment" : "Control Methods"
                        font.pixelSize: 18
                        font.bold: true
                        color: "#334155"
                    }

                    Text {
                        text: InfarenceRunner.cure || "No treatment information available"
                        font.pixelSize: 14
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                        color: "#475569"
                    }
                }

                // New Analysis button
                Button {
                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: 40

                    text: "New Analysis"

                    onClicked: {
                        console.log("New Analysis clicked")
                        root.selectedImagePath = ""
                        root.currentPage = 0
                    }
                }
            }
        }
    }

    /* ======================
       OVERLAY
       ====================== */
    LoadingOverlay {
        id: loadingOverlay
        anchors.fill: parent
        visible: root.isProcessing
        message: _("analyzing")

        onVisibleChanged: {
            console.log("LoadingOverlay visible changed to:", visible)
        }
    }

    /* ======================
       ERROR DIALOG
       ====================== */
    ErrorDialog {
        id: errorDialog
    }

    /* ======================
       BACKEND CONNECTION
       ====================== */
    Connections {
        target: InfarenceRunner

        function onInferenceFinished() {
            console.log("=== QML: onInferenceFinished received ===")
            root.isProcessing = false
            root.currentPage = 1
        }

        function onInferenceFailed(error) {
            console.log("=== QML: onInferenceFailed received ===")
            root.isProcessing = false
            errorDialog.message = error
            errorDialog.open()
        }

        // WORKAROUND: Change page when confidence is updated
        function onConfidenceChanged() {
            console.log("Confidence changed to:", InfarenceRunner.confidence)
            // If we have confidence and we're processing, switch to results
            if (root.isProcessing && InfarenceRunner.confidence > 0) {
                console.log("Confidence updated, switching to results page")
                root.isProcessing = false
                root.currentPage = 1
            }
        }

        function onDiseaseNameChanged() {
            console.log("Disease name changed to:", InfarenceRunner.disease_name)
        }

        function onDescriptionChanged() {
            console.log("Description changed")
        }

        function onCureChanged() {
            console.log("Cure changed")
        }
    }
}