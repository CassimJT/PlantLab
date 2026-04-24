import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    id: root
    property bool isLoading: false
    property string statusMessage: ""
    property int textSize: 13
    property var filteredModel: ListModel { id: tempFilteredModel }
    property var allRecords: []

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // =========================
        // LOADING OVERLAY
        // =========================
        Rectangle {
            anchors.fill: parent
            color: Qt.rgba(0, 0, 0, 0.5)
            visible: root.isLoading
            z: 10

            Column {
                anchors.centerIn: parent
                spacing: 20

                BusyIndicator {
                    anchors.horizontalCenter: parent.horizontalCenter
                    running: root.isLoading
                    width: 50
                    height: 50
                }

                Label {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: root.statusMessage || "Loading data from server..."
                    color: "white"
                    font.pixelSize: 14
                }
            }
        }

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
                    enabled: !root.isLoading
                    onClicked: {
                        clearFilter()
                    }
                }

                Button {
                    text: "Maize/Corn"
                    enabled: !root.isLoading
                    onClicked: {
                        applyFilter("variaty", "Corn_777")
                    }
                }

                Button {
                    text: "High breed Maize"
                    enabled: !root.isLoading
                    onClicked: {
                        applyFilter("variaty", "Hybrid maize")
                    }
                }

                Button {
                    text: "Local Tommato"
                    enabled: !root.isLoading
                    onClicked: {
                        applyFilter("variaty", "Local tomato")
                    }
                }

                Button {
                    text: "Beens"
                    enabled: !root.isLoading
                    onClicked: {
                        applyFilter("variaty", "Boma beans")
                    }
                }

                Button {
                    text: "Cassava"
                    enabled: !root.isLoading
                    onClicked: {
                        applyFilter("variaty", "Chalimbana")
                    }
                }

                Item { Layout.fillWidth: true }

                TextField {
                    id: searchField
                    placeholderText: "Filter by location..."
                    Layout.preferredWidth: 320
                    enabled: !root.isLoading
                    onAccepted: {
                        if (searchField.text.length > 0) {
                            applyFilter("location", searchField.text)
                        } else {
                            clearFilter()
                        }
                    }
                }

                BusyIndicator {
                    visible: root.isLoading
                    width: 30
                    height: 30
                    running: root.isLoading
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
                            clip: true

                            // Show placeholder when no data
                            property bool hasData: model && model.count > 0

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                visible: root.isLoading
                                color: "transparent"
                                z: 1

                                Column {
                                    anchors.centerIn: parent
                                    spacing: 10

                                    Label {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: "No data available"
                                        color: "#6b7280"
                                        font.pixelSize: 14
                                    }

                                    Button {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: "Fetch Data"
                                        visible: FieldDataset.count === 0
                                        onClicked: {
                                            root.isLoading = true
                                            root.statusMessage = "Fetching data from server..."
                                            ResearcherDataService.fetchFieldData()
                                        }
                                    }
                                }
                            }

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
                                        font.pixelSize: root.textSize
                                    }
                                    Text {
                                        Layout.preferredWidth: 140
                                        text: model.diseaseName || ""
                                        elide: Text.ElideRight
                                        font.weight: Font.Medium
                                        font.pixelSize: root.textSize
                                    }
                                    Text {
                                        Layout.preferredWidth: 80
                                        text: (model.confidence * 100).toFixed(1) + "%"
                                        color: model.confidence > 0.8 ? "#10b981" : (model.confidence > 0.6 ? "#f59e0b" : "#ef4444")
                                        font.pixelSize: root.textSize
                                    }
                                    Text {
                                        Layout.preferredWidth: 120
                                        text: model.variety || ""
                                        elide: Text.ElideRight
                                        font.pixelSize: root.textSize
                                    }
                                    Text {
                                        Layout.fillWidth: true
                                        text: model.timestamp || ""
                                        elide: Text.ElideRight
                                        color: "#6b7280"
                                        font.pixelSize: root.textSize
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // -------- FILTER PANEL --------
            Rectangle {
                implicitWidth: 200
                SplitView.minimumWidth: 190
                SplitView.maximumWidth: 200
                color: "#f8fafc"
                border.color: "#e5e7eb"

                Column {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 8

                    Label {
                        text: "Actions"
                        font.bold: true
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Button {
                        width: parent.width * 0.9
                        text: "Fetch Data"
                        enabled: !root.isLoading
                        onClicked: {
                            root.isLoading = true
                            root.statusMessage = "Fetching data from server..."
                            ResearcherDataService.fetchFieldData()
                        }
                    }

                    Button {
                        width: parent.width * 0.9
                        text: "Clear All"
                        enabled: !root.isLoading
                        onClicked: {
                            FieldDataset.clearRecords()
                            clearFilter()
                            root.statusMessage = "Cleared all records"
                        }
                    }

                    Button {
                        width: parent.width * 0.9
                        text: "Export CSV"
                        enabled: !root.isLoading && FieldDataset.count > 0
                        onClicked: {
                            handleExport("CSV")
                        }
                    }

                    Button {
                        width: parent.width * 0.9
                        text: "Export JSON"
                        enabled: !root.isLoading && FieldDataset.count > 0
                        onClicked: {
                            handleExport("JSON")
                        }
                    }

                    Rectangle {
                        width: parent.width
                        height: 1
                        color: "#e5e7eb"
                    }

                    Label {
                        text: "Quick Filters"
                        font.bold: true
                        font.pixelSize: 12
                    }

                    Button {
                        text: "Show All"
                        flat: true
                        width: parent.width * 0.9
                        onClicked: {
                            clearFilter()
                        }
                    }

                    ComboBox {
                        id: locationFilter
                        width: parent.width * 0.9
                        model: FieldDataExplorer.getUniqueLocations()
                        displayText: currentText || "Filter by location"
                        onActivated: {
                            if (currentText) {
                                applyFilter("location", currentText)
                            }
                        }
                    }

                    ComboBox {
                        id: diseaseFilter
                        width: parent.width * 0.9
                        model: FieldDataExplorer.getUniqueDiseases()
                        displayText: currentText || "Filter by disease"
                        onActivated: {
                            if (currentText) {
                                applyFilter("diseasname", currentText)
                            }
                        }
                    }

                    Button {
                        width: parent.width * 0.9
                        text: "Open Export Folder"
                        flat: true
                        enabled: !root.isLoading
                        onClicked: {
                            FieldDataExplorer.openExportDirectory()
                        }
                    }
                }
            }
        }

        // =========================
        // STATUS BAR / FOOTER
        // =========================
        Rectangle {
            height: 32
            Layout.fillWidth: true
            color: "#ffffff"
            border.color: "#e5e7eb"

            RowLayout {
                anchors.verticalCenter: parent.verticalCenter
                Label {
                    text: "Total Records: " + (FieldDataset.count || 0)
                    font.pixelSize: 12
                }

                Label {
                    text: root.statusMessage
                    color: "#6b7280"
                    font.pixelSize: 11
                    visible: root.statusMessage.length > 0
                    Layout.fillWidth: true
                }
            }
        }
    }

    Component.onCompleted: {
        root.isLoading = true
        root.statusMessage = "Loading initial data..."
        ResearcherDataService.fetchFieldData()
    }
    // Function to refresh the view with proper data mapping
    function refreshView() {
        recordsView.model = FieldDataset.listModel
        tempFilteredModel.clear()
        allRecords = []
    }

    // Function to map record to proper field names for display
    function mapRecord(record) {
        return {
            "location": record.location || "",
            "diseaseName": record.diseasname || record.diseaseName || "",
            "confidence": record.confidence || 0,
            "variety": record.variaty || record.variety || "",
            "timestamp": record.timestamp || ""
        }
    }

    // Function to apply filter
    function applyFilter(fieldName, filterValue) {
        if (!filterValue || filterValue === "") {
            clearFilter()
        } else {
            // Use Python-side filtering
            var filtered = FieldDataset.filterByValue(fieldName, filterValue)
            root.statusMessage = "Filtered by " + fieldName + ": " + filterValue + " (" + filtered.length + " records)"
            console.log("Filter applied - Found:", filtered.length, "records")

            // Clear and repopulate the filtered model with mapped records
            tempFilteredModel.clear()
            for (var i = 0; i < filtered.length; i++) {
                var mappedRecord = mapRecord(filtered[i])
                tempFilteredModel.append(mappedRecord)
            }
            recordsView.model = tempFilteredModel
        }
    }

    // Function to clear filter
    function clearFilter() {
        if (locationFilter) locationFilter.currentIndex = -1
        if (diseaseFilter) diseaseFilter.currentIndex = -1
        if (searchField) searchField.text = ""
        root.statusMessage = "Showing all records"
        refreshView()
    }

    // Function to handle export - Fixed to handle direct return value
    function handleExport(format) {
        if (FieldDataset.count === 0) {
            root.statusMessage = "No data to export"
            return
        }

        root.isLoading = true
        root.statusMessage = "Exporting to " + format + "..."

        console.log("Export started for format:", format)
        console.log("Total records to export:", FieldDataset.count)

        // Use a timer to give UI time to update, then perform export
        var exportTimer = Qt.createQmlObject("import QtQuick 2.0; Timer { interval: 100; repeat: false }", root)
        exportTimer.triggered.connect(function() {
            var result
            if (format === "CSV") {
                result = FieldDataset.exportToCsv()
            } else {
                result = FieldDataset.exportToJson()
            }

            console.log("Export result:", result)

            // Process result
            if (result && result.toString().indexOf("Error") === -1) {
                console.log(format + " exported to:", result)
                root.statusMessage = format + " exported to: " + result.toString().split('/').pop()
            } else {
                console.error("Export failed:", result)
                root.statusMessage = "Export failed: " + result
            }
            root.isLoading = false
            exportTimer.destroy()
        })
        exportTimer.start()
    }

    Connections {
        target: ResearcherDataService
        function onInferencesFetched(records) {
            console.log("Fetched", records.length, "inferences")
            root.isLoading = false
            root.statusMessage = "Loaded " + records.length + " records"

            // Store all records with proper field mapping
            allRecords = records
            refreshView()

            // Update combo box models after data is loaded
            locationFilter.model = FieldDataExplorer.getUniqueLocations()
            diseaseFilter.model = FieldDataExplorer.getUniqueDiseases()
        }
        function onErrorOccurred(error) {
            console.error("DataService error:", error)
            root.isLoading = false
            root.statusMessage = "Error: " + error
        }
    }

    Connections {
        target: FieldDataExplorer
        function onDataLoaded(count) {
            console.log("Loaded", count, "records into dataset")
            root.statusMessage = "Loaded " + count + " records"
            refreshView()
        }
        // Keep these for potential future use but not required for direct export
        function onExportCompleted(filepath) {
            console.log("Export completed signal:", filepath)
        }
        function onExportFailed(error) {
            console.error("Export failed signal:", error)
        }
    }
}