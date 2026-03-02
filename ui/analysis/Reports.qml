import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    id: root

    signal exportPdfRequested(string reportId)
    signal exportCsvRequested(string reportId)
    signal deleteReportRequested(string reportId)

    property string selectedReportId: ""

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ============================
        // TOP TOOLBAR
        // ============================
        Rectangle {
            height: 50
            Layout.fillWidth: true
            color: "#ffffff"
            border.color: "#e5e7eb"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Button {
                    text: "Export PDF"
                    enabled: root.selectedReportId !== ""
                    onClicked: root.exportPdfRequested(root.selectedReportId)
                }

                Button {
                    text: "Export CSV"
                    enabled: root.selectedReportId !== ""
                    onClicked: root.exportCsvRequested(root.selectedReportId)
                }

                Button {
                    text: "Delete"
                    enabled: root.selectedReportId !== ""
                    onClicked: root.deleteReportRequested(root.selectedReportId)
                }

                Item { Layout.fillWidth: true }

                Label {
                    text: root.selectedReportId === "" ?
                              "No report selected" :
                              "Selected: " + root.selectedReportId
                    color: "#6b7280"
                }
            }
        }

        // ============================
        // MAIN SPLIT VIEW
        // ============================
        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Horizontal



            // -------- REPORT VIEWER --------
            Rectangle {
                SplitView.fillWidth: true
                color: "white"
                border.color: "#e5e7eb"

                ScrollView {
                    anchors.fill: parent
                    anchors.margins: 12

                    Column {
                        width: parent.width
                        spacing: 12

                        Label {
                            text: "Report Title"
                            font.pixelSize: 20
                            font.bold: true
                        }

                        Label {
                            text: "Summary section will appear here..."
                            wrapMode: Text.WordWrap
                        }

                        Label {
                            text: "Detailed Results:"
                            font.bold: true
                        }

                        Repeater {
                            model: [] // bind to structured report sections
                            delegate: Rectangle {
                                width: parent.width
                                height: 60
                                border.color: "#e5e7eb"
                                radius: 4

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8

                                    Label { text: model.section }
                                    Item { Layout.fillWidth: true }
                                    Label { text: model.value }
                                }
                            }
                        }
                    }
                }
            }

            // -------- REPORT LIST --------
            Rectangle {
                implicitWidth: 200
                SplitView.maximumWidth: 300
                SplitView.minimumWidth: 100
                color: "#f8fafc"
                border.color: "#e5e7eb"

                ListView {
                    id: reportList
                    anchors.fill: parent
                    anchors.margins: 6
                    clip: true

                    // bind this to report model from backend
                    model: []

                    delegate: Rectangle {
                        width: ListView.view.width
                        height: 60
                        radius: 4
                        color: ListView.isCurrentItem ? "#e0f2fe" : "white"
                        border.color: "#e5e7eb"

                        Column {
                            anchors.fill: parent
                            anchors.margins: 8

                            Label {
                                text: model.title || "Report"
                                font.bold: true
                            }

                            Label {
                                text: model.createdAt || ""
                                font.pixelSize: 12
                                color: "#6b7280"
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                reportList.currentIndex = index
                                root.selectedReportId = model.id
                            }
                        }
                    }
                }
            }
        }
    }
}
