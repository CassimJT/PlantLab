import QtQuick 2.15
import QtCharts 2.15
import QtQuick.Controls

Item {
    id: pieChartRoot
    property var chartMapper: null
    property string chartTitle: "Infections by Region"

    property var fullLines: []
    property var fullRegions: []

    onChartMapperChanged: {
        if (chartMapper) {
            chartMapper.lineDataChanged.connect(updateFromMapper)
            updateFromMapper()
        }
    }

    function updateFromMapper() {
        if (!chartMapper) return
        fullLines = chartMapper.lineSeries || []
        fullRegions = chartMapper.lineCategories || []
        updatePie(fullLines, fullRegions)
    }

    ChartView {
        id: chartView
        anchors.fill: parent
        anchors.margins: 15
        antialiasing: true
        legend.visible: true
        legend.alignment: Qt.AlignRight
        title: pieChartRoot.chartTitle
        animationOptions: ChartView.SeriesAnimations
        animationDuration: 800

        PieSeries {
            id: pieSeries

            onClicked: function(slice) {
                pieChartRoot.showRegionDetails(slice.label)
            }
        }
    }

    // Improved Info Box
    Rectangle {
        id: infoBox
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 30
        width: 200
        height: 280
        color: Qt.rgba(0,0,0,0.65)
        border.color: "#3498db"
        border.width: 2
        radius: 12
        visible: false
        z: 100
        clip: true


        Column {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 8

            Label {
                text: "<b>Region:</b>"
                font.pixelSize: 16
                color: "#ffffff"           // White text for dark background
            }
            Label {
                id: regionName
                text: ""
                font.pixelSize: 20
                font.bold: true
                color: "#ffffff"           // White
            }

            Label {
                text: "Total Infections:"
                font.pixelSize: 14
                color: "#a0d8ff"           // Light blue
            }
            Label {
                id: totalCount
                text: "0"
                font.pixelSize: 19
                font.bold: true
                color: "#4ade80"           // Bright green
            }

            Label {
                text: "Diseases in this region:"
                font.pixelSize: 14
                color: "#a0d8ff"
            }

            // Scrollable disease list
            ScrollView {
                width: parent.width - 10
                height: parent.height * 0.5
                clip: true

                TextArea {
                    id: diseaseList
                    readOnly: true
                    textFormat: TextEdit.RichText
                    background: null
                    font.pixelSize: 13
                    color: "#e0f0ff"           // Light cyan for good contrast
                    wrapMode: Text.Wrap
                    selectByMouse: true
                    bottomPadding: 6

                }
            }
        }
    }

    function updatePie(lines, regions) {
        pieSeries.clear()
        fullLines = lines
        fullRegions = regions

        if (!lines || lines.length === 0 || !regions || regions.length === 0) {
            pieSeries.append("No Data", 100)
            return
        }

        var regionTotals = {}
        for (var r = 0; r < regions.length; r++) {
            regionTotals[regions[r]] = 0
        }

        for (var i = 0; i < lines.length; i++) {
            var pts = lines[i].points || []
            for (var j = 0; j < pts.length && j < regions.length; j++) {
                var regName = regions[j]
                regionTotals[regName] = (regionTotals[regName] || 0) + (pts[j].y || 0)
            }
        }

        // Find highest region
        var maxCount = 0
        var maxRegion = ""
        for (var reg in regionTotals) {
            if (regionTotals[reg] > maxCount) {
                maxCount = regionTotals[reg]
                maxRegion = reg
            }
        }

        // Create slices
        for (var region in regionTotals) {
            var count = regionTotals[region]
            if (count <= 0) continue

            var slice = pieSeries.append(region, count)
            slice.labelVisible = true
            slice.labelPosition = PieSlice.LabelOutside

            if (region === maxRegion) {
                slice.exploded = true
                slice.color = "#e74c3c"
            }
        }

        pieChartRoot.chartTitle = "Infections by Region (Highest: " + maxRegion + ")"
        console.log("Pie updated with", pieSeries.count, "regions")
    }

    function showRegionDetails(clickedRegion) {
        regionName.text = clickedRegion

        var total = 0
        var diseasesText = ""

        for (var i = 0; i < fullLines.length; i++) {
            var line = fullLines[i]
            var diseaseName = line.name || "Unknown"
            var pts = line.points || []

            for (var j = 0; j < pts.length; j++) {
                if (fullRegions[j] === clickedRegion) {
                    var count = pts[j].y || 0
                    if (count > 0) {
                        diseasesText += diseaseName + ": <b>" + count + "</b><br>"
                        total += count
                    }
                    break
                }
            }
        }

        totalCount.text = total
        diseaseList.text = diseasesText || "<i>No disease data recorded for this region.</i>"

        infoBox.visible = true
        hideTimer.restart()
    }

    Timer {
        id: hideTimer
        interval: 8000
        onTriggered: infoBox.visible = false
    }
}