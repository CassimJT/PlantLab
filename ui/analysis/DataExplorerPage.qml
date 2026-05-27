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
                    text: "Tomato"
                    enabled: !root.isLoading
                    onClicked: {
                        applyFilter("crop", "Tomato")
                    }
                }

                Button {
                    text: "Maize"
                    enabled: !root.isLoading
                    onClicked: {
                        applyFilter("crop", "Maize")
                    }
                }

                Button {
                    text: "Potato"
                    enabled: !root.isLoading
                    onClicked: {
                        applyFilter("crop", "Potato")
                    }
                }

                Button {
                    text: "Soybean"
                    enabled: !root.isLoading
                    onClicked: {
                        applyFilter("crop", "Soybean")
                    }
                }

                Item { Layout.fillWidth: true }

                TextField {
                    id: searchField
                    placeholderText: "Search by location, disease, or variety..."
                    Layout.preferredWidth: 320
                    enabled: !root.isLoading
                    onTextChanged: {
                        if (text.length > 0) {
                            applyGeneralFilter(text)
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
                                Layout.preferredWidth: 100
                                text: "Location"
                                font.bold: true
                                font.pixelSize: 13
                                color: "#334155"
                            }
                            Label {
                                Layout.preferredWidth: 80
                                text: "Crop"
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
                            model: tempFilteredModel

                            delegate: Rectangle {
                                width: parent ? parent.width : 0
                                height: 40
                                color: index % 2 === 0 ? "#ffffff" : "#f8fafc"

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    spacing: 8

                                    Text {
                                        Layout.preferredWidth: 100
                                        text: model.location || ""
                                        elide: Text.ElideRight
                                        font.pixelSize: root.textSize
                                    }
                                    Text {
                                        Layout.preferredWidth: 80
                                        text: model.crop || ""
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

                            // Empty state
                            Rectangle {
                                anchors.fill: parent
                                visible: tempFilteredModel.count === 0 && !root.isLoading
                                color: "transparent"

                                Column {
                                    anchors.centerIn: parent
                                    spacing: 10

                                    Label {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: searchField.text ? "No matching records found" : "No data available"
                                        color: "#6b7280"
                                        font.pixelSize: 14
                                    }

                                    Button {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: "Fetch Data"
                                        visible: getRecordCount() === 0
                                        onClicked: {
                                            root.isLoading = true
                                            root.statusMessage = "Fetching data from server..."
                                            ResearcherDataService.fetchFieldData()
                                        }
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
                        id: cropFilter
                        width: parent.width * 0.9
                        model: FieldDataExplorer.getUniqueCrops()
                        displayText: currentText || "Filter by crop"
                        onActivated: {
                            if (currentText) {
                                applyFilter("crop", currentText)
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
        recordsView.model = tempFilteredModel
        // Reload all records into filtered model
        if (allRecords.length > 0) {
            tempFilteredModel.clear()
            for (var i = 0; i < allRecords.length; i++) {
                tempFilteredModel.append(allRecords[i])
            }
        } else {
            // Try to get from dataset
            var records = FieldDataset.getRecords()
            tempFilteredModel.clear()
            for (var i = 0; i < records.length; i++) {
                var mappedRecord = mapRecord(records[i])
                tempFilteredModel.append(mappedRecord)
            }
        }
    }

    // Function to map record to proper field names for display
    function mapRecord(record) {
        return {
            "location": record.location || "",
            "crop": record.crop || "",
            "diseaseName": record.diseasname || record.diseaseName || "",
            "confidence": record.confidence || 0,
            "variety": record.variaty || record.variety || "",
            "timestamp": record.timestamp || ""
        }
    }

    // NEW: General search filter that searches across location, disease, and variety
    function applyGeneralFilter(searchText) {
        if (!searchText || searchText === "") {
            clearFilter()
            return
        }

        var searchLower = searchText.toLowerCase()
        var filtered = []
        var allData = FieldDataset.getRecords()

        for (var i = 0; i < allData.length; i++) {
            var record = allData[i]
            var location = (record.location || "").toLowerCase()
            var disease = (record.diseasname || record.diseaseName || "").toLowerCase()
            var variety = (record.variaty || record.variety || "").toLowerCase()

            // Check if search text matches any field
            if (location.indexOf(searchLower) !== -1 ||
                disease.indexOf(searchLower) !== -1 ||
                variety.indexOf(searchLower) !== -1) {
                filtered.push(mapRecord(record))
            }
        }

        root.statusMessage = "Search: '" + searchText + "' - " + filtered.length + " records found"
        console.log("General filter - Found:", filtered.length, "records")

        tempFilteredModel.clear()
        for (var j = 0; j < filtered.length; j++) {
            tempFilteredModel.append(filtered[j])
        }

        // Clear combo box selections when using general search
        if (locationFilter) locationFilter.currentIndex = -1
        if (cropFilter) cropFilter.currentIndex = -1
    }

    // Function to apply specific field filter
    function applyFilter(fieldName, filterValue) {
        if (!filterValue || filterValue === "") {
            clearFilter()
        } else {
            // Clear search field
            if (searchField) searchField.text = ""

            // Use Python-side filtering
            var filtered = FieldDataset.filterByValue(fieldName, filterValue)
            root.statusMessage = "Filtered by " + fieldName + ": " + filterValue + " (" + filtered.length + " records)"
            console.log("Filter applied - Found:", filtered.length, "records")

            tempFilteredModel.clear()
            for (var i = 0; i < filtered.length; i++) {
                var mappedRecord = mapRecord(filtered[i])
                tempFilteredModel.append(mappedRecord)
            }
        }
    }

    // Function to clear all filters
    function clearFilter() {
        if (locationFilter) locationFilter.currentIndex = -1
        if (cropFilter) cropFilter.currentIndex = -1
        if (searchField) searchField.text = ""
        root.statusMessage = "Showing all records"

        // Reset to all records
        var allData = FieldDataset.getRecords()
        tempFilteredModel.clear()
        for (var i = 0; i < allData.length; i++) {
            tempFilteredModel.append(mapRecord(allData[i]))
        }
    }

    // Function to handle export
    function handleExport(format) {
        if (FieldDataset.count === 0) {
            root.statusMessage = "No data to export"
            return
        }

        root.isLoading = true
        root.statusMessage = "Exporting to " + format + "..."

        var exportTimer = Qt.createQmlObject("import QtQuick 2.0; Timer { interval: 100; repeat: false }", root)
        exportTimer.triggered.connect(function() {
            var result
            if (format === "CSV") {
                result = FieldDataset.exportToCsv()
            } else {
                result = FieldDataset.exportToJson()
            }

            if (result && result.toString().indexOf("Error") === -1) {
                root.statusMessage = format + " exported to: " + result.toString().split('/').pop()
            } else {
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

            // Store all records with proper field mapping
            allRecords = []
            for (var i = 0; i < records.length; i++) {
                allRecords.push(mapRecord(records[i]))
            }

            root.isLoading = false
            root.statusMessage = "Loaded " + records.length + " records"
            refreshView()

            // Update combo box models after data is loaded
            locationFilter.model = FieldDataExplorer.getUniqueLocations()
            cropFilter.model = FieldDataExplorer.getUniqueCrops()
            if (StatisticalAnalyzer) {
                StatisticalAnalyzer.runAllAnalyses()
            }
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
            // Refresh the view with new data
            var records = FieldDataset.getRecords()
            allRecords = []
            for (var i = 0; i < records.length; i++) {
                allRecords.push(mapRecord(records[i]))
            }
            refreshView()
        }
    }
}