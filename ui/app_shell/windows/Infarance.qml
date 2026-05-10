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
    readonly property color bgColor: "#f1f5f9"
    readonly property color cardColor: "#ffffff"
    readonly property color primary: "#2563eb"
    readonly property color textMain: "#0f172a"
    readonly property color textMuted: "#64748b"
    readonly property color borderColor: "#e2e8f0"

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
       CONTENT
       ====================== */
    Loader {
        id: pageLoader
        anchors.top: header.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        sourceComponent: currentPage === 0 ? uploadPage : resultsPage
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