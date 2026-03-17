import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root

    property string selectedImagePath: ""
    property bool isProcessing: false

    signal imageSelected(string path)
    signal analyzeClicked()

    ColumnLayout {
        anchors.centerIn: parent
        width: Math.min(parent.width * 0.8, 600)
        spacing: 32

        /* ======================
           Instruction text
           ====================== */
        Text {
            text: qsTr("Select an image to begin")
            font.pixelSize: 16
            color: "#64748b"
            Layout.alignment: Qt.AlignHCenter
        }

        /* ======================
           Image Drop Zone
           ====================== */
        DropZone {
            id: dropZone

            Layout.preferredWidth: 500
            Layout.preferredHeight: 350
            Layout.alignment: Qt.AlignHCenter

            selectedImagePath: root.selectedImagePath

            onImageSelected: function(path) {
                root.imageSelected(path)
            }
        }

        /* ======================
           Analyze Button
           ====================== */
        Button {
            id: analyzeButton

            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 250
            Layout.preferredHeight: 56

            enabled: root.selectedImagePath.length > 0 && !root.isProcessing

            background: Rectangle {
                radius: 28
                color: analyzeButton.enabled ? "#0284c7" : "#94a3b8"
            }

            contentItem: RowLayout {
                anchors.centerIn: parent
                spacing: 12

                BusyIndicator {
                    running: root.isProcessing
                    visible: root.isProcessing
                    width: 24
                    height: 24
                }

                Text {
                    text: root.isProcessing
                          ? qsTr("Analyzing...")
                          : qsTr("Analyze Plant")

                    font.pixelSize: 16
                    font.bold: true
                    color: "white"
                    Layout.alignment: Qt.AlignCenter
                }

                Text {
                    text: "→"
                    font.pixelSize: 20
                    color: "white"
                    visible: !root.isProcessing
                }
            }

            onClicked: root.analyzeClicked()
        }

        /* ======================
           Framework Selector
           ====================== */
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 16

            visible: InfarenceRunner.available_frameworks.length > 0

            Text {
                text: qsTr("Framework") + ":"
                color: "#64748b"
                font.pixelSize: 14
            }

            ComboBox {
                id: frameworkCombo
                width: 180

                model: InfarenceRunner.available_frameworks

                currentIndex: {
                    if (!model || model.length === 0)
                        return -1

                    var idx = model.indexOf(InfarenceRunner.current_framework)
                    return idx >= 0 ? idx : 0
                }

                onActivated: function(index) {
                    if (index >= 0)
                        InfarenceRunner.set_framework(currentText)
                }
            }
        }
    }
}
