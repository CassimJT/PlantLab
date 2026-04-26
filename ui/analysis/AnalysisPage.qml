import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphs

Page {
    id: root

    signal generateReport()
    signal varietySelected(string name)

    property string currentAnalysis: ""
    property bool isRunning: false
    property int currentGraphType: 0  // 0=Bar, 1=Scatter, 2=Surface
    property int surfaceRowCount: 0

    // Track current analysis results
    property var currentResult: ({})

    // Helper function to call Python analysis
    function callAnalysis(analysisType) {
        console.log("QML: Calling analysis:", analysisType)
        if (StatisticalAnalyzer) {
            StatisticalAnalyzer.runAnalysis(analysisType)
        } else {
            console.error("QML: StatisticalAnalyzer not available!")
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // =============================
        // TOP CONTROL BAR
        // =============================
        Rectangle {
            height: 60
            Layout.fillWidth: true
            color: "#ffffff"
            border.color: "#e5e7eb"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                ComboBox {
                    id: analysisSelector
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: run.height
                    model: [
                        "Disease Frequency",
                        "Variety Susceptibility",
                        "Infection Rate Comparison",
                        "Disease By Region"
                    ]
                }

                // Graph Type Selector
                ComboBox {
                    id: graphTypeSelector
                    Layout.preferredWidth: 150
                    Layout.preferredHeight: run.height
                    model: ["Bar Chart", "Scatter Plot", "Surface Plot"]
                    currentIndex: root.currentGraphType
                    onCurrentIndexChanged: {
                        root.currentGraphType = currentIndex
                        if (root.currentAnalysis !== "")
                            root.callAnalysis(root.currentAnalysis)
                    }
                }

                TextField {
                    id: varietyField
                    placeholderText: "Variety (if required)"
                    visible: analysisSelector.currentIndex === 2
                    Layout.preferredWidth: 180
                    onAccepted: {
                        if (varietyField.text.length > 0) {
                            root.varietySelected(varietyField.text)
                        }
                    }
                }

                Button {
                    id: run
                    text: "Run"
                    enabled: !root.isRunning
                    onClicked: {
                        root.currentAnalysis = analysisSelector.currentText
                        root.isRunning = true
                        root.callAnalysis(root.currentAnalysis)
                    }
                }

                Button {
                    text: "Generate Report"
                    onClicked: root.generateReport()
                }

                Item { Layout.fillWidth: true }

                Label {
                    text: root.isRunning ? "Running..." : "Idle"
                    color: root.isRunning ? "orange" : "green"
                }
            }
        }

        // =============================
        // METRIC CARDS AREA
        // =============================
        Rectangle {
            Layout.fillWidth: true
            height: 110
            color: "#f8fafc"
            border.color: "#e5e7eb"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 20

                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    radius: 6
                    color: "white"
                    border.color: "#e5e7eb"

                    Column {
                        anchors.centerIn: parent
                        spacing: 5
                        Label { text: "Total Records"; font.pixelSize: 12; color: "#6b7280" }
                        Label {
                            id: totalRecordsLabel
                            text: currentResult.total_records ? currentResult.total_records : "—"
                            font.pixelSize: 20
                            font.bold: true
                            color: "#1f2937"
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    radius: 6
                    color: "white"
                    border.color: "#e5e7eb"

                    Column {
                        anchors.centerIn: parent
                        spacing: 5
                        Label { text: "Top Category"; font.pixelSize: 12; color: "#6b7280" }
                        Label {
                            id: topCategoryLabel
                            text: currentResult.top_category ? currentResult.top_category : "—"
                            font.pixelSize: 16
                            font.bold: true
                            color: "#1f2937"
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    radius: 6
                    color: "white"
                    border.color: "#e5e7eb"

                    Column {
                        anchors.centerIn: parent
                        spacing: 5
                        Label { text: "Region Impact"; font.pixelSize: 12; color: "#6b7280" }
                        Label {
                            id: regionImpactLabel
                            text: currentResult.top_region ? currentResult.top_region : "—"
                            font.pixelSize: 16
                            font.bold: true
                            color: "#1f2937"
                        }
                    }
                }
            }
        }

        // =============================
        // VISUALIZATION AREA
        // =============================
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "white"
            border.color: "#e5e7eb"

            StackLayout {
                anchors.fill: parent
                anchors.margins: 10
                currentIndex: root.currentGraphType

                // 0: Bar Chart View
                Item {
                    Bars3D {
                        id: barGraph
                        anchors.fill: parent
                        theme: Theme3D.ThemeQt
                        shadowQuality: AbstractGraph3D.ShadowQualityMedium
                        barThickness: 0.8
                        selectionMode: Graphs3D.SelectionItem

                        valueAxis: Value3DAxis {
                            title: "Number of Infections"
                            titleVisible: true
                            segmentCount: 5
                        }

                        rowAxis: Category3DAxis {
                            title: "Category"
                            titleVisible: true
                            labelAutoAngle: 30
                        }

                        columnAxis: Category3DAxis {
                            title: "Value"
                            titleVisible: true
                        }

                        Bar3DSeries {
                            id: barSeries
                            itemLabelFormat: "@colLabel: @valueLabel"
                            mesh: AbstractBar3DSeries.MeshCylinder
                            colorStyle: Theme3D.ColorStyleRangeGradient

                            ItemModelBarDataProxy {
                                id: barProxy
                                itemModel: StatisticalAnalyzer.plotModel.barModel
                                rowRole: "row"
                                columnRole: "column"
                                valueRole: "value"
                            }
                        }
                    }
                }

                // 1: Scatter Plot View
                Item {
                    Scatter3D {
                        id: scatterGraph
                        anchors.fill: parent
                        theme: Theme3D.ThemeQt
                        shadowQuality: AbstractGraph3D.ShadowQualityMedium
                        selectionMode: Graphs3D.SelectionItem

                        axisX: Value3DAxis {
                            title: "Total Infections per Variety"
                            titleVisible: true
                            segmentCount: 5
                        }

                        axisY: Value3DAxis {
                            title: "Disease Percentage (%)"
                            titleVisible: true
                            segmentCount: 5
                        }

                        axisZ: Value3DAxis {
                            title: "Count"
                            titleVisible: true
                            segmentCount: 5
                        }

                        Scatter3DSeries {
                            id: scatterSeries
                            itemLabelFormat: "@xLabel, @yLabel: @zLabel"
                            mesh: AbstractScatter3DSeries.MeshSphere

                            ItemModelScatterDataProxy {
                                id: scatterProxy
                                itemModel: StatisticalAnalyzer.plotModel.scatterModel
                                xPosRole: "x"
                                yPosRole: "y"
                                zPosRole: "z"
                            }
                        }
                    }
                }

                // 2: Surface Plot View
                Item {
                    Surface3D {
                        id: surfaceGraph
                        anchors.fill: parent
                        theme: Theme3D.ThemeQt
                        shadowQuality: AbstractGraph3D.ShadowQualityMedium
                        flipHorizontalGrid: false
                        selectionMode: Graphs3D.SelectionItem

                        axisX: Value3DAxis {
                            title: "Regions (20 districts)"
                            titleVisible: true
                            labelAutoAngle: 45
                            segmentCount: 5
                            min: 0
                            max: 19
                            labelFormat: "%.0f"
                        }

                        axisY: Value3DAxis {
                            title: "Number of Infections"
                            titleVisible: true
                            segmentCount: 5
                            min: 0
                            labelFormat: "%.0f"
                        }

                        axisZ: Value3DAxis {
                            title: "Diseases (10 types)"
                            titleVisible: true
                            labelAutoAngle: 30
                            segmentCount: 5
                            min: 0
                            max: 9
                            labelFormat: "%.0f"
                        }

                        Surface3DSeries {
                            id: surfaceSeries
                            itemLabelFormat: "Region: @xLabel, Disease: @zLabel, Infections: @yLabel"
                            mesh: AbstractSurface3DSeries.MeshSphere
                            drawMode: AbstractSurface3DSeries.DrawSurface

                            ItemModelSurfaceDataProxy {
                                id: surfaceProxy
                                itemModel: StatisticalAnalyzer.plotModel.surfaceModel
                                rowRole: "row"
                                columnRole: "column"
                                yPosRole: "value"
                            }
                        }
                    }

                    // Info overlay when no data
                    Rectangle {
                        anchors.centerIn: parent
                        width: 300
                        height: 100
                        color: "#f0f0f0"
                        radius: 10
                        visible: (StatisticalAnalyzer && StatisticalAnalyzer.plotModel &&
                                 StatisticalAnalyzer.plotModel.surfaceModel &&
                                 StatisticalAnalyzer.plotModel.surfaceModel.rowCount === 0)
                        border.color: "#cccccc"

                        Column {
                            anchors.centerIn: parent
                            spacing: 10
                            Label {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: "No Surface Data Available"
                                font.bold: true
                            }
                            Label {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: "Run 'Disease By Region' analysis first"
                                font.pixelSize: 12
                                color: "#666666"
                            }
                        }
                    }

                    // Data info overlay
                    Rectangle {
                        anchors.top: parent.top
                        anchors.right: parent.right
                        anchors.margins: 10
                        width: 180
                        height: 60
                        color: "white"
                        border.color: "#cccccc"
                        radius: 5
                        z: 1

                        Column {
                            anchors.centerIn: parent
                            spacing: 3
                            Label {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: "Surface Data"
                                font.bold: true
                                font.pixelSize: 10
                            }
                            Label {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: "Points: " + (StatisticalAnalyzer && StatisticalAnalyzer.plotModel &&
                                                   StatisticalAnalyzer.plotModel.surfaceModel ?
                                                   StatisticalAnalyzer.plotModel.surfaceModel.rowCount : 0)
                                font.pixelSize: 9
                            }
                            Label {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: "20 Regions × 10 Diseases"
                                font.pixelSize: 9
                                color: "#666666"
                            }
                        }
                    }
                }
            }
        }
    }

    // =============================
    // Connections to Business Logic
    // =============================
    Connections {
        target: StatisticalAnalyzer

        function onAnalysisStarted(analysisName) {
            console.log("QML: Analysis started:", analysisName)
            root.isRunning = true
        }

        function onAnalysisCompleted(analysisName, result) {
            console.log("QML: Analysis completed:", analysisName)
            root.isRunning = false

            if (analysisName === "Disease Frequency") {
                if (result && result.diseases) {
                    currentResult = {
                        total_records: result.total_records,
                        top_category: result.diseases.length > 0 ? result.diseases[0].name : "—",
                        top_region: "—"
                    }
                }
            }
            else if (analysisName === "Disease By Region") {
                if (result) {
                    let topRegion = ""
                    let maxInfections = 0
                    if (result.regions_detail) {
                        for (var i = 0; i < result.regions_detail.length; i++) {
                            if (result.regions_detail[i].total_infections > maxInfections) {
                                maxInfections = result.regions_detail[i].total_infections
                                topRegion = result.regions_detail[i].name
                            }
                        }
                    }
                    currentResult = {
                        total_records: currentResult.total_records || result.total_records,
                        top_category: currentResult.top_category || "—",
                        top_region: topRegion || "—"
                    }

                    console.log("Surface data - Regions:", result.total_regions, "Diseases:", result.total_diseases)
                }
            }
            else if (analysisName === "Infection Rate Comparison") {
                if (result && result.varieties && result.varieties.length > 0) {
                    currentResult = {
                        total_records: currentResult.total_records || result.varieties.reduce((sum, v) => sum + v.total_infections, 0),
                        top_category: result.varieties[0].name,
                        top_region: currentResult.top_region || "—"
                    }
                }
            }
            else if (analysisName === "Variety Susceptibility") {
                if (result && result.varieties) {
                    currentResult = {
                        total_records: currentResult.total_records || result.varieties.reduce((sum, v) => sum + v.total_infections, 0),
                        top_category: result.varieties.length > 0 ? result.varieties[0].name : "—",
                        top_region: currentResult.top_region || "—"
                    }
                }
            }
        }

        function onAnalysisError(analysisName, errorMessage) {
            console.error("QML: Analysis error:", analysisName, errorMessage)
            root.isRunning = false
            errorDialog.text = "Error in " + analysisName + ":\n" + errorMessage
            errorDialog.open()
        }

        function onDatasetChanged() {
            console.log("QML: Dataset changed")
        }
    }

    // Error dialog
    Dialog {
        id: errorDialog
        title: "Analysis Error"
        property string text: ""

        ColumnLayout {
            Label {
                text: errorDialog.text
                wrapMode: Text.WordWrap
            }
            Button {
                text: "OK"
                onClicked: errorDialog.close()
            }
        }
    }

    // Initial load
    Component.onCompleted: {
        console.log("QML: Page loaded, checking for StatisticalAnalyzer...")
        if (StatisticalAnalyzer) {
            console.log("QML: StatisticalAnalyzer found")
            Qt.callLater(function() {
                root.currentAnalysis = "Disease Frequency"
                analysisSelector.currentIndex = 0
                root.callAnalysis(root.currentAnalysis)
            })
        } else {
            console.error("QML: StatisticalAnalyzer is null!")
        }
    }
}