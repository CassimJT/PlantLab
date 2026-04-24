import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    id: root
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
                    onClicked: {
                        FieldDataExplorer.clearFilter()
                    }
                }

                Button {
                    text: "Disease Only"
                    onClicked: {
                        // Just an example - you can filter by disease if needed
                        FieldDataExplorer.currentFilter = "Blight"
                    }
                }

                Item { Layout.fillWidth: true }

                TextField {
                    id: searchField
                    placeholderText: "Filter by field..."
                    width: 200
                    onAccepted: {
                        // You can implement filtering here if needed
                        console.log("Search:", searchField.text)
                    }
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

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 0

                    // Table Headers
                    Rectangle {
                        Layout.fillWidth: true
                        height: 45
                        color: "#f1f5f9"
                        border.color: "#e2e8f0"

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 8

                            Label {
                                Layout.preferredWidth: 120
                                text: "Location"
                                font.bold: true
                                font.pixelSize: 13
                                color: "#334155"
                            }
                            Label {
                                Layout.preferredWidth: 140
                                text: "Disease Name"
                                font.bold: true
                                font.pixelSize: 13
                                color: "#334155"
                            }
                            Label {
                                Layout.preferredWidth: 80
                                text: "Confidence"
                                font.bold: true
                                font.pixelSize: 13
                                color: "#334155"
                            }
                            Label {
                                Layout.preferredWidth: 120
                                text: "Variety"
                                font.bold: true
                                font.pixelSize: 13
                                color: "#334155"
                            }
                            Label {
                                Layout.fillWidth: true
                                text: "Timestamp"
                                font.bold: true
                                font.pixelSize: 13
                                color: "#334155"
                            }
                        }
                    }

                    // Table Data
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true

                        ListView {
                            id: recordsView
                            width: parent.width
                            model: FieldDataset.listModel
                            clip: true

                            delegate: Rectangle {
                                width: parent ? parent.width : 0
                                height: 40
                                color: index % 2 === 0 ? "#ffffff" : "#f8fafc"

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 8

                                    Text {
                                        Layout.preferredWidth: 120
                                        text: model.location || ""
                                        elide: Text.ElideRight
                                        font.pixelSize: 12
                                    }
                                    Text {
                                        Layout.preferredWidth: 140
                                        text: model.diseaseName || ""
                                        elide: Text.ElideRight
                                        font.weight: Font.Medium
                                        font.pixelSize: 12
                                    }
                                    Text {
                                        Layout.preferredWidth: 80
                                        text: (model.confidence * 100).toFixed(1) + "%"
                                        color: model.confidence > 0.8 ? "#10b981" : (model.confidence > 0.6 ? "#f59e0b" : "#ef4444")
                                        font.pixelSize: 12
                                    }
                                    Text {
                                        Layout.preferredWidth: 120
                                        text: model.variety || ""
                                        elide: Text.ElideRight
                                        font.pixelSize: 12
                                    }
                                    Text {
                                        Layout.fillWidth: true
                                        text: model.timestamp || ""
                                        elide: Text.ElideRight
                                        color: "#6b7280"
                                        font.pixelSize: 11
                                    }
                                }
                            }
                        }
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
                        onClicked: {
                            ResearcherDataService.fetchFieldData()
                        }
                    }

                    Button {
                        icon.source: "qrc:/assets/analysis/clear.svg"
                        width: parent.width * .9
                        icon.color: "#475569"
                        text: "Clear"
                        onClicked: {
                            FieldDataset.clearRecords()
                        }
                    }

                    Button {
                        icon.source: "qrc:/assets/analysis/export-pdf.svg"
                        width: parent.width * .9
                        icon.color: "#475569"
                        text: "Export CSV"
                        onClicked: {
                            FieldDataset.exportToCsv()
                        }
                    }

                    Button {
                        icon.source: "qrc:/assets/analysis/export-pdf.svg"
                        width: parent.width * .9
                        icon.color: "#475569"
                        text: "Export JSON"
                        onClicked: {
                            FieldDataset.exportToJson()
                        }
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

                Label {
                    text: "Total Records: " + (FieldDataset.count || 0)
                }

                Item { Layout.fillWidth: true }

                Button {
                    text: "Open Export Folder"
                    flat: true
                    onClicked: {
                        FieldDataExplorer.openExportDirectory()
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        ResearcherDataService.fetchFieldData()
    }

    Connections {
        target: ResearcherDataService
        function onInferencesFetched(records) {
            console.log("Fetched", records.length, "inferences")
        }
        function onErrorOccurred(error) {
            console.error("DataService error:", error)
        }
    }

    Connections {
        target: FieldDataExplorer
        function onDataLoaded(count) {
            console.log("Loaded", count, "records into dataset")
        }
        function onExportCompleted(filepath) {
            console.log("Export completed:", filepath)
        }
        function onExportFailed(error) {
            console.error("Export failed:", error)
        }
    }
}