import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    id: root

    property alias datasetModel: recordsView.model

    signal fetchRequested()
    signal exportRequested(string path)
    signal clearRequested()
    signal filterRequested(string field)

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // =========================
        // TOOLBAR
        // =========================
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
                    text: "Show All"
                    onClicked: root.filterRequested("")
                }

                Button {
                    text: "Disease Only"
                    onClicked: root.filterRequested("disease")
                }

                Button {
                    text: "Pest Only"
                    onClicked: root.filterRequested("pest")
                }

                Item { Layout.fillWidth: true }

                TextField {
                    id: searchField
                    placeholderText: "Filter by field..."
                    width: 200
                    onAccepted: root.filterRequested(text)
                }
            }
        }

        // =========================
        // MAIN CONTENT
        // =========================
        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Horizontal


            // -------- TABLE VIEW --------
            Rectangle {
                SplitView.fillWidth: true
                color: "white"

                ListView {
                    id: recordsView
                    anchors.fill: parent
                    clip: true

                    //
                    BusyIndicator {
                        anchors.centerIn: parent
                    }
                }
            }
            // -------- FILTER PANEL --------
            Rectangle {
                implicitWidth: 170
                SplitView.minimumWidth: 180
                SplitView.maximumWidth: 170
                color: "#f8fafc"
                border.color: "#e5e7eb"

                Column {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 8

                    Label {
                        text: "Actions"
                        font.bold: true
                        anchors {
                            horizontalCenter: parent.horizontalCenter
                        }
                    }

                    Button {
                        icon.source: "qrc:/assets/analysis/get.svg"
                        icon.color: "#475569"
                        width: parent.width * .9
                        text: "Fetch Data"
                        onClicked: root.fetchRequested()
                    }

                    Button {
                        icon.source: "qrc:/assets/analysis/clear.svg"
                        width: parent.width * .9
                        icon.color: "#475569"
                        text: "Clear"
                        onClicked: root.clearRequested()
                    }

                    Button {
                        icon.source: "qrc:/assets/analysis/export-pdf.svg"
                        width: parent.width * .9
                        icon.color: "#475569"
                        text: "Export"
                        onClicked: root.exportRequested("dataset.csv")
                    }

                }
            }
        }

        // =========================
        // FOOTER
        // =========================
        Rectangle {
            height: 32
            Layout.fillWidth: true
            color: "#ffffff"
            border.color: "#e5e7eb"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10

                Label {
                    text: "Total Records: " + (recordsView.count || 0)
                }
            }
        }
    }
}
