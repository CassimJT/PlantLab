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
    property int currentPage: 0
    property string selectedImagePath: ""
    property bool isProcessing: false

    /* ======================
       COLORS (CLEAN SYSTEM)
       ====================== */
    readonly property color bgColor:     "#0f1623"
    readonly property color cardColor:   "#1a2035"
    readonly property color primary:     "#4f6ef7"
    readonly property color textMain:    "#e2e8f0"
    readonly property color textMuted:   "#64748b"
    readonly property color borderColor: "#2d3550"

    /* ======================
       BACKGROUND
       ====================== */
    Rectangle {
        anchors.fill: parent
        color: root.bgColor
    }

    /* ======================
       HEADER
       ====================== */
    Header {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        titleText: "Plant Disease Detector"
        subtitleText: currentPage === 0 ? "Upload Image" : "Results"
    }

    /* ======================
       PAGE INDICATOR STRIP
       ====================== */
    Row {
        id: pageIndicator
        anchors.top: header.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 14
        spacing: 8

        Repeater {
            model: ["Upload", "Results"]
            delegate: Row {
                spacing: 6

                Rectangle {
                    width: currentPage === index ? 24 : 8
                    height: 8; radius: 4
                    color: currentPage === index ? root.primary : root.borderColor
                    Behavior on width { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                    Behavior on color { ColorAnimation { duration: 200 } }
                }

                Text {
                    text: modelData
                    font.pixelSize: 11
                    color: currentPage === index ? root.textMain : root.textMuted
                    anchors.verticalCenter: parent.verticalCenter
                    Behavior on color { ColorAnimation { duration: 200 } }
                }
            }
        }
    }

    /* ======================
       CONTENT
       ====================== */
    Loader {
        id: pageLoader
        anchors.top: pageIndicator.bottom
        anchors.topMargin: 10
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        sourceComponent: currentPage === 0 ? uploadPage : resultsPage

        // Fade transition between pages
        opacity: 0
        NumberAnimation on opacity {
            id: fadeIn
            to: 1; duration: 250; easing.type: Easing.OutCubic
        }
        onSourceComponentChanged: {
            opacity = 0
            fadeIn.restart()
        }
    }

    /* ======================
       UPLOAD PAGE
       ====================== */
    Component {
        id: uploadPage
        UploadPage {
            selectedImagePath: root.selectedImagePath
            isProcessing: root.isProcessing
            onSelectedImagePathChanged: {
                root.selectedImagePath = selectedImagePath
            }
            onAnalyzeClicked: {
                if (selectedImagePath && selectedImagePath.length > 0) {
                    root.isProcessing = true
                    InfarenceRunner.classify_image_from_file(selectedImagePath)
                } else {
                    errorDialog.message = "Please select an image first"
                    errorDialog.open()
                }
            }
        }
    }

    /* ======================
       RESULTS PAGE (CLEANED)
       ====================== */
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

    /* ======================
       LOADING
       ====================== */
    LoadingOverlay {
        anchors.fill: parent
        visible: root.isProcessing
        message: "Analyzing..."
    }

    /* ======================
       ERROR
       ====================== */
    ErrorDialog {
        id: errorDialog
    }

    /* ======================
       BACKEND CONNECTION
       ====================== */
    Connections {
        target: InfarenceRunner
        function onInference_finished() {
            root.isProcessing = false
            root.currentPage = 1
        }
        function onInference_failed(error) {
            root.isProcessing = false
            errorDialog.message = error
            errorDialog.open()
        }
    }
}