import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts
import QtQuick.Dialogs

Page {
    id: root
    title: "Model Training"

    property bool training: false
    property real progress: 0.0

    ColumnLayout {
        spacing: 15
        anchors {
            left: parent.left
            right: parent.right
            rightMargin: 20
            leftMargin: 20
        }

        // ================= DATASET =================
        GroupBox {
            title: "1. Dataset"
            Layout.fillWidth: true

            RowLayout {
                spacing: 10
                width: parent.width

                TextField {
                    id: csvPath
                    Layout.fillWidth: true
                    Layout.preferredWidth: parent.width * 0.5
                    placeholderText: "Select normalized CSV file..."
                    readOnly: true
                }

                Button {
                    text: "Browse"
                    onClicked: fileDialog.open()
                }
            }
        }

        // ================= PARAMETERS =================
        GroupBox {
            title: "2. Training Parameters"
            Layout.fillWidth: true

            GridLayout {
                columns: 2
                columnSpacing: 12
                rowSpacing: 10
                Layout.fillWidth: true

                Label { text: "Model Type:" }
                ComboBox {
                    id: modelType
                    Layout.preferredWidth: parent.width * 0.7
                    model: ["Logistic Regression", "Random Forest", "SVM", "Neural Network"]
                    currentIndex: 0
                }

                Label { text: "Epochs:" }
                SpinBox {
                    id: epochs
                    editable: true
                    from: 1
                    to: 500
                    value: 50
                }

                Label { text: "Batch Size:" }
                SpinBox {
                    id: batchSize
                    editable: true
                    from: 1
                    to: 1024
                    value: 32
                }

                Label { text: "Learning Rate:" }
                TextField {
                    id: lr
                    text: "0.001"
                    validator: DoubleValidator { bottom: 0.000001 }
                }

                Label { text: "Train/Test Split:" }
                Slider {
                    id: split
                    Layout.preferredWidth: parent.width * 0.7
                    from: 0.5
                    to: 0.95
                    value: 0.8
                    stepSize: 0.05
                }

                Label {
                    text: Math.round(split.value * 100) + "% train"
                }
            }
        }

        // ================= TRAIN CONTROL =================
        GroupBox {
            title: "3. Training Control"
            Layout.fillWidth: true

            RowLayout {
                spacing: 12

                Button {
                    text: training ? "Stop Training" : "Start Training"
                    enabled: csvPath.text.length > 0
                    onClicked: {
                        training = !training
                        progress = 0
                        // backend.startTraining(...)
                    }
                }

                BusyIndicator {
                    running: training
                    visible: training
                }
            }
        }

        // ================= PROGRESS =================
        GroupBox {
            title: "4. Training Progress"
            Layout.fillWidth: true
            visible: training || progress > 0

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                ProgressBar {
                    value: progress
                    Layout.fillWidth: true
                }

                Label {
                    text: Math.round(progress * 100) + "% completed"
                }

                Label {
                    text: "Loss: 0.34   Accuracy: 91%"
                    font.pixelSize: 12
                    opacity: 0.7
                }
            }
        }

        // ================= RESULTS =================
        GroupBox {
            title: "5. Results"
            Layout.fillWidth: true
            visible: progress >= 1.0

            ColumnLayout {
                spacing: 6

                Label { text: "Accuracy: 91.3%" }
                Label { text: "Precision: 89.7%" }
                Label { text: "Recall: 92.1%" }
                Label { text: "F1 Score: 90.9%" }

                Button {
                    text: "Export Model"
                }
            }
        }
    }

    FileDialog {
        id: fileDialog
        title: "Select Training CSV"
        nameFilters: ["CSV files (*.csv)"]
        onAccepted: csvPath.text = fileUrl.toLocalFile()
    }
}
