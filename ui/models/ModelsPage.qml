import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts
import "./delagete"
import "./model"
import "./components"

Page {
    id: root
    // ====== TOP BAR ======
    Rectangle {
        id: topBar
        height: 52
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        color: "#ffffff"
        border.color: "#e5e7eb"

        RowLayout {
            anchors.fill: parent
            anchors.margins: 12

            Label {
                text: "Model Management"
                font.pixelSize: 18
                font.weight: Font.Medium
                Layout.fillWidth: true
            }

            TextField {
                placeholderText: "Search models..."
                Layout.preferredWidth: 220
            }

            Button {
                text: "New Model"
            }
        }
    }

    // ====== MAIN SPLIT VIEW ======
    SplitView {
        id: splitView
        anchors.top: topBar.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        orientation: Qt.Horizontal


        // ====== LEFT SIDEBAR ======
        Rectangle {
            implicitWidth: 140
            SplitView.minimumWidth: 60
            SplitView.maximumWidth: 180
            color: "#f8fafc"
            border.color: "#e5e7eb"

            ListView {
                id: listView
                anchors.fill: parent
                anchors.margins: 5
                clip:true
                model: ActionModel{}
                delegate: ActionDelagate{}

            }
        }

        // ====== CENTER WORKSPACE ======
        Rectangle {
            SplitView.fillWidth: true
            color: "#f5f7fb"

            StackLayout {
                anchors.fill: parent
                currentIndex: listView.currentIndex
                Library {
                    id: library
                }
                Download{}
                Transform{}
                Train{}
            }

        }

        // ====== RIGHT INSPECTOR / LOG PANEL ======
        Rectangle {
            implicitWidth: 300
            SplitView.minimumWidth: 220
            SplitView.maximumWidth: 420
            color: "#ffffff"
            border.color: "#e5e7eb"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 12

                Label {
                    text: "Model Details"
                    font.pixelSize: 16
                    font.weight: Font.Medium
                }

                // Empty state
                Rectangle {
                    visible: !library.selectedModel
                    Layout.fillWidth: true
                    height: 90
                    radius: 8
                    color: "#f8fafc"
                    border.color: "#e5e7eb"

                    Label {
                        anchors.centerIn: parent
                        text: "Select a model"
                        color: "#94a3b8"
                    }
                }

                // Details panel
                GroupBox {
                    visible: library.selectedModel
                    Layout.fillWidth: true
                    title: library.selectedModel ? library.selectedModel.name : ""

                    ColumnLayout {
                        anchors.fill: parent
                        spacing: 2
                        DetailRow {
                            label: "Framework";
                            value: library.selectedModel.framework
                        }
                        MenuSeparator {
                            Layout.fillWidth: true
                        }

                        DetailRow {
                            label: "Size";
                            value: library.selectedModel._size
                        }
                        MenuSeparator {
                            Layout.fillWidth: true
                        }
                        DetailRow {
                            label: "Accuracy"; value:
                                library.selectedModel.accuracy + "%"
                        }
                        MenuSeparator {
                            Layout.fillWidth: true
                        }
                        DetailRow {
                            label: "Learning Rate";
                            value: library.selectedModel.learningRate
                        }
                        MenuSeparator {
                            Layout.fillWidth: true
                        }
                        DetailRow { label: "Epochs"; value: library.selectedModel.epochs
                        }
                        MenuSeparator {
                            Layout.fillWidth: true
                        }
                        DetailRow {
                            label: "Status";
                            value: library.selectedModel.status
                        }
                        MenuSeparator {
                            Layout.fillWidth: true
                        }

                    }
                }

                Label {
                    text: "Logs"
                    font.pixelSize: 14
                    font.weight: Font.Medium
                }

                TextArea {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    readOnly: true
                    placeholderText: ""
                    BusyIndicator {
                        anchors.centerIn: parent
                    }
                }
            }
        }

    }
}
