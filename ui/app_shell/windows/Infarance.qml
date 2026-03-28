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

        Item {
            anchors.fill: parent

            Rectangle {
                anchors.centerIn: parent
                width: parent.width * 0.75
                height: parent.height * 0.85

                color: root.cardColor
                radius: 20
                border.color: root.borderColor

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 30
                    spacing: 20

                    /* IMAGE PREVIEW */
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 220
                        radius: 12
                        color: "#f8fafc"

                        Image {
                            anchors.fill: parent
                            anchors.margins: 12
                            source: root.selectedImagePath ? "file://" + root.selectedImagePath : ""
                            fillMode: Image.PreserveAspectFit
                            cache: false
                        }
                    }

                    /* TITLE */
                    Text {
                        text: InfarenceRunner.disease_name || "Unknown Disease"
                        font.pixelSize: 26
                        font.bold: true
                        color: root.textMain
                        Layout.fillWidth: true
                    }

                    /* CONFIDENCE BADGE */
                    Rectangle {
                        Layout.fillWidth: true
                        height: 45
                        radius: 10

                        color: "#f1f5f9"

                        Text {
                            anchors.centerIn: parent
                            text: "Confidence: " +
                                  (InfarenceRunner.confidence
                                   ? InfarenceRunner.confidence.toFixed(2) + "%"
                                   : "0%")

                            font.pixelSize: 16
                            font.bold: true

                            color: InfarenceRunner.confidence > 70
                                   ? "#16a34a"
                                   : (InfarenceRunner.confidence > 40
                                      ? "#f59e0b"
                                      : "#dc2626")
                        }
                    }

                    /* DESCRIPTION CARD */
                    Rectangle {
                        Layout.fillWidth: true
                        radius: 12
                        color: "#f8fafc"
                        border.color: root.borderColor

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 15
                            spacing: 8

                            Text {
                                text: "Description"
                                font.pixelSize: 18
                                font.bold: true
                                color: root.textMain
                            }

                            Text {
                                text: InfarenceRunner.description || "No description available"
                                wrapMode: Text.WordWrap
                                color: root.textMuted
                                font.pixelSize: 14
                            }
                        }
                    }

                    /* TREATMENT CARD */
                    Rectangle {
                        Layout.fillWidth: true
                        radius: 12
                        color: "#f8fafc"
                        border.color: root.borderColor

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 15
                            spacing: 8

                            Text {
                                text: InfarenceRunner.current_category === "disease"
                                      ? "Treatment"
                                      : "Control Methods"
                                font.pixelSize: 18
                                font.bold: true
                                color: root.textMain
                            }

                            Text {
                                text: InfarenceRunner.cure || "No treatment information available"
                                wrapMode: Text.WordWrap
                                color: root.textMuted
                                font.pixelSize: 14
                            }
                        }
                    }

                    /* BUTTON */
                    Button {
                        Layout.alignment: Qt.AlignHCenter
                        Layout.preferredWidth: 220
                        Layout.preferredHeight: 45

                        text: "New Analysis"

                        background: Rectangle {
                            radius: 10
                            color: root.primary
                        }

                        contentItem: Text {
                            text: parent.text
                            color: "white"
                            anchors.centerIn: parent
                            font.bold: true
                        }

                        onClicked: {
                            root.selectedImagePath = ""
                            root.currentPage = 0
                        }
                    }
                }
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

        function onInferenceFinished() {
            root.isProcessing = false
            root.currentPage = 1
        }

        function onInferenceFailed(error) {
            root.isProcessing = false
            errorDialog.message = error
            errorDialog.open()
        }
    }
}