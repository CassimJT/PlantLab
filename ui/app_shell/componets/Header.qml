import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs

Rectangle {
    id: root
    height: mainLayout.implicitHeight + 24
    Layout.fillWidth: true

    color: "#1a1f2e"
    border.color: "#2d3550"

    property string titleText: ""
    property string subtitleText: ""
    property string modelSource: ""
    property string modelFramework: "pytorch"

    ColumnLayout {
        id: mainLayout
        anchors.fill: parent
        anchors.margins: 12
        spacing: 10

        /* ======================
           Model Loader Row
           ====================== */
        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            // Status indicator icon
            Rectangle {
                width: 36; height: 36; radius: 6
                color: "#252b3d"
                border.color: "#3a4160"; border.width: 1
                Text {
                    anchors.centerIn: parent
                    text: "⬡"; font.pixelSize: 16
                    color: modelSource !== "" ? "#4ade80" : "#6b7280"
                }
            }

            // Path input field
            Rectangle {
                Layout.fillWidth: true; height: 36; radius: 6
                color: "#252b3d"
                border.color: modelIdField.activeFocus ? "#4f6ef7" : "#3a4160"
                border.width: modelIdField.activeFocus ? 1.5 : 1
                Behavior on border.color { ColorAnimation { duration: 150 } }

                TextInput {
                    id: modelIdField
                    anchors.fill: parent
                    anchors.leftMargin: 12; anchors.rightMargin: 12
                    verticalAlignment: TextInput.AlignVCenter
                    color: text === "" ? "#4b5563" : "#e2e8f0"
                    font.pixelSize: 13; font.family: "Monospace"
                    clip: true; text: modelSource

                    Text {
                        visible: parent.text === ""
                        text: "Enter model path or HuggingFace ID…"
                        color: "#4b5563"; font: parent.font
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    onTextChanged: modelSource = text.trim()
                }
            }

            // Browse button
            Rectangle {
                width: 90; height: 36; radius: 6
                Layout.alignment: Qt.AlignVCenter
                color: browseHover.containsMouse ? "#3d4fd6" : "#4f6ef7"
                Behavior on color { ColorAnimation { duration: 120 } }
                Text {
                    anchors.centerIn: parent; text: "Browse"
                    color: "#ffffff"; font.pixelSize: 13; font.weight: Font.Medium
                }
                HoverHandler { id: browseHover }
                TapHandler { onTapped: fileDialog.open() }
            }
        }

        /* ======================
           Controls Row
           ====================== */
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            // Framework ComboBox
            StyledComboBox {
                id: frameworkCombo
                Layout.fillWidth: true
                Layout.minimumWidth: 120
                comboEnabled: !InfarenceRunner.is_model_loaded
                iconChar: "⚙"

                comboModel: [
                    { text: "Auto",       value: "auto"       },
                    { text: "PyTorch",    value: "pytorch"    },
                    { text: "TensorFlow", value: "tensorflow" },
                    { text: "OpenCV",     value: "opencv"     },
                    { text: "ExecuTorch", value: "executorch" }
                ]

                onSelectionChanged: function(value) {
                    if (value !== "auto") {
                        modelFramework = value
                        InfarenceRunner.set_framework(value)
                    }
                }
            }

            // Language ComboBox
            StyledComboBox {
                Layout.preferredWidth: 90
                Layout.alignment: Qt.AlignVCenter
                iconChar: "⌘"

                comboModel: [
                    { text: "EN", value: "en" },
                    { text: "NY", value: "ny" }
                ]

                Component.onCompleted: {
                    currentIdx = InfarenceRunner.current_language === "ny" ? 1 : 0
                }

                onSelectionChanged: function(value) {
                    InfarenceRunner.set_language(value)
                }
            }

            // Category ComboBox
            StyledComboBox {
                Layout.preferredWidth: 110
                Layout.alignment: Qt.AlignVCenter
                iconChar: "◈"

                comboModel: [
                    { text: "Disease", value: "disease" },
                    { text: "Pest",    value: "pest"    }
                ]

                onSelectionChanged: function(value) {
                    InfarenceRunner.set_category(value)
                }
            }
        }
    }

    /* ======================
       Reusable Styled ComboBox
       ====================== */
    component StyledComboBox: Rectangle {
        id: comboRoot
        height: 36; radius: 6
        color: "#252b3d"
        border.color: comboPopup.visible ? "#4f6ef7" : "#3a4160"
        border.width: comboPopup.visible ? 1.5 : 1
        opacity: comboEnabled ? 1.0 : 0.45

        property var    comboModel:   []
        property int    currentIdx:   0
        property bool   comboEnabled: true
        property string iconChar:     ""
        signal selectionChanged(string value)

        Behavior on border.color { ColorAnimation { duration: 150 } }
        Behavior on color        { ColorAnimation { duration: 120 } }

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: 10; anchors.rightMargin: 8
            spacing: 6

            Text {
                visible: comboRoot.iconChar !== ""
                text: comboRoot.iconChar; color: "#6b7da8"; font.pixelSize: 12
            }
            Text {
                Layout.fillWidth: true
                text: comboRoot.comboModel.length > 0 ? comboRoot.comboModel[comboRoot.currentIdx].text : ""
                color: "#cbd5e1"; font.pixelSize: 13; elide: Text.ElideRight
            }
            Text {
                text: comboPopup.visible ? "▲" : "▼"
                color: "#4b5880"; font.pixelSize: 8
            }
        }

        HoverHandler {
            id: comboHover
            onHoveredChanged: comboRoot.color = hovered ? "#2d3450" : "#252b3d"
        }

        TapHandler {
            enabled: comboRoot.comboEnabled
            onTapped: comboPopup.visible ? comboPopup.close() : comboPopup.open()
        }

        Popup {
            id: comboPopup
            y: comboRoot.height + 4
            width: comboRoot.width
            padding: 4
            background: Rectangle {
                radius: 8; color: "#1e2436"
                border.color: "#3a4160"; border.width: 1
            }
            contentItem: Column {
                spacing: 2
                Repeater {
                    model: comboRoot.comboModel
                    delegate: Rectangle {
                        width: comboPopup.width - 8; height: 30; radius: 5
                        color: itemHover.containsMouse ? "#2d3a5c"
                             : (comboRoot.currentIdx === index ? "#252f4a" : "transparent")
                        Behavior on color { ColorAnimation { duration: 80 } }

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left; anchors.leftMargin: 10
                            text: comboRoot.comboModel[index].text
                            color: comboRoot.currentIdx === index ? "#93c5fd" : "#cbd5e1"
                            font.pixelSize: 13
                        }
                        Text {
                            visible: comboRoot.currentIdx === index
                            anchors.right: parent.right; anchors.rightMargin: 10
                            anchors.verticalCenter: parent.verticalCenter
                            text: "✓"; color: "#4f6ef7"; font.pixelSize: 11
                        }
                        HoverHandler { id: itemHover }
                        TapHandler {
                            onTapped: {
                                comboRoot.currentIdx = index
                                comboRoot.selectionChanged(comboRoot.comboModel[index].value)
                                comboPopup.close()
                            }
                        }
                    }
                }
            }
        }
    }

    FileDialog {
        id: fileDialog
        title: "Select Model File"

        nameFilters: [
            "Model files (*.pt *.pth *.h5 *.pb *.tflite *.onnx *.caffemodel *.weights *.pte)",
            "All files (*)"
        ]

        onAccepted: {
            var filePath = selectedFile.toString()
            if (filePath.startsWith("file://"))
                filePath = filePath.substring(7)

            modelSource = filePath
            modelIdField.text = modelSource

            var framework = frameworkCombo.comboModel[frameworkCombo.currentIdx].value
            if (framework === "auto")
                InfarenceRunner.load_model(modelSource)
            else
                InfarenceRunner.load_model(modelSource, framework)
        }
    }

    Component.onCompleted: {
        root.modelSource = InfarenceRunner.model_loaded_path
    }
}