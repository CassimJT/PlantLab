import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs

Rectangle {
    id: root
    height: parent.width * .10
    Layout.fillWidth: true

    color: "#ffffff"
    border.color: "#e2e8f0"

    property string titleText: ""
    property string subtitleText: ""
    property string modelSource: ""
    property string modelFramework: "pytorch"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        /* ======================
           Model Loader Row
           ====================== */
        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            TextField {
                id: modelIdField
                Layout.fillWidth: true
                Layout.minimumWidth: 150
                placeholderText: "Load your model"
                text: modelSource

                onTextChanged: modelSource = text.trim()
            }

            Button {
                text: "Browse"
                Layout.preferredWidth: 90
                Layout.alignment: Qt.AlignVCenter
                onClicked: fileDialog.open()
            }
        }

        /* ======================
           Controls Row
           ====================== */
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            // Framework ComboBox
            ComboBox {
                id: frameworkCombo
                Layout.fillWidth: true
                Layout.minimumWidth: 120
                enabled: !InfarenceRunner.is_model_loaded

                model: [
                    { text: "Auto", value: "auto" },
                    { text: "PyTorch", value: "pytorch" },
                    { text: "TensorFlow", value: "tensorflow" },
                    { text: "OpenCV", value: "opencv" },
                    { text: "ExecuTorch", value: "executorch" }
                ]

                textRole: "text"
                valueRole: "value"

                onActivated: {
                    let selected = model[currentIndex].value
                    if (selected !== "auto") {
                        modelFramework = selected
                        InfarenceRunner.set_framework(selected)
                    }
                }
            }

            // Language ComboBox
            ComboBox {
                Layout.preferredWidth: 90
                Layout.alignment: Qt.AlignVCenter

                model: [
                    { text: "EN", value: "en" },
                    { text: "NY", value: "ny" }
                ]

                textRole: "text"
                valueRole: "value"

                Component.onCompleted: {
                    currentIndex = InfarenceRunner.current_language === "ny" ? 1 : 0
                }

                onActivated: {
                    InfarenceRunner.set_language(currentValue)
                }
            }

            // Category ComboBox
            ComboBox {
                Layout.preferredWidth: 110
                Layout.alignment: Qt.AlignVCenter

                model: [
                    { text: "Disease", value: "disease" },
                    { text: "Pest", value: "pest" }
                ]

                textRole: "text"
                valueRole: "value"

                onActivated: {
                    InfarenceRunner.set_category(currentValue)
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

            var framework = frameworkCombo.currentValue
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