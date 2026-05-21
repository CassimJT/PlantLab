import QtQuick 2.15
import QtCharts
import QtQuick.Controls 2.15

Item {
    id: scatterSeriesChart
    property var chartMapper: null
    property string chartTitle: "Variety Susceptibility Analysis"
    property var currentPoints: []
    property int minSampleSize: 3

    onChartMapperChanged: {
        if (chartMapper) {
            chartMapper.scatterDataChanged.connect(updateFromMapper)
            updateFromMapper()
        }
    }

    function updateFromMapper() {
        if (!chartMapper) return
        var points = chartMapper.scatterPoints
        console.log("ScatterChart: Received", points?.length, "points")
        if (points && points.length > 0) {
            updateScatterData(points)
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#FAFAFA"
        radius: 4
        z: -1
    }

    ChartView {
        id: chartView
        anchors.fill: parent
        anchors.margins: 15
        anchors.topMargin: 45
        theme: ChartView.ChartThemeLight
        backgroundColor: "transparent"
        animationOptions: ChartView.SeriesAnimations
        animationDuration: 800

        ScatterSeries {
            id: lowSeries
            axisX: axisX
            axisY: axisY
            color: "#66BB6A"
            borderColor: "#4CAF50"
            markerSize: 10
            markerShape: ScatterSeries.MarkerShapeCircle
            name: "Low (0-33%)"

            onHovered: (point, hovered) => {
                if (hovered && point) showTooltip(point)
                else if (!hovered) hideTimer.start()
            }
        }

        ScatterSeries {
            id: mediumSeries
            axisX: axisX
            axisY: axisY
            color: "#FFA726"
            borderColor: "#F57C00"
            markerSize: 10
            markerShape: ScatterSeries.MarkerShapeCircle
            name: "Medium (34-66%)"

            onHovered: (point, hovered) => {
                if (hovered && point) showTooltip(point)
                else if (!hovered) hideTimer.start()
            }
        }

        ScatterSeries {
            id: highSeries
            axisX: axisX
            axisY: axisY
            color: "#EF5350"
            borderColor: "#C62828"
            markerSize: 10
            markerShape: ScatterSeries.MarkerShapeCircle
            name: "High (67-100%)"

            onHovered: (point, hovered) => {
                if (hovered && point) showTooltip(point)
                else if (!hovered) hideTimer.start()
            }
        }

        ValueAxis {
            id: axisX
            min: 0
            titleText: "Total Infections per Variety"
            titleVisible: true
            gridVisible: true
        }

        ValueAxis {
            id: axisY
            min: 0
            max: 100
            titleText: "Disease Susceptibility (%)"
            titleVisible: true
            gridVisible: true
        }
    }

    // Title bar
    Item {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 35
        z: 2

        Label {
            anchors.left: parent.left
            anchors.leftMargin: 15
            anchors.verticalCenter: parent.verticalCenter
            text: scatterSeriesChart.chartTitle + " (min " + minSampleSize + " infections)"
            font.bold: true
            font.pixelSize: 13
            color: "#333333"
        }

        Rectangle {
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: 1
            color: "#E0E0E0"
        }
    }

    // Enhanced tooltip
    Rectangle {
        id: tooltip
        visible: false
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 50
        width: 280
        height: 110
        color: "#2C3E50"
        opacity: 0.95
        radius: 8
        z: 10

        Column {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 6

            Label {
                id: tooltipVariety
                width: parent.width
                color: "#FF9800"
                font.pixelSize: 13
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
            }

            Label {
                id: tooltipDisease
                width: parent.width
                color: "#FF9800"
                font.pixelSize: 11
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
            }

            Label {
                id: tooltipStats
                width: parent.width
                color: "white"
                font.pixelSize: 11
                horizontalAlignment: Text.AlignHCenter
            }

            Label {
                id: tooltipPercent
                width: parent.width
                color: "#4ECDC4"
                font.pixelSize: 12
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
            }
        }

        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 3
            radius: 2
            color: "#EF5350"
        }
    }

    // Simple legend
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.margins: 10
        width: 150
        height: 110
        color: "white"
        radius: 4
        border.color: "#E0E0E0"
        border.width: 1
        z: 2

        Column {
            anchors.centerIn: parent
            spacing: 5

            Row {
                spacing: 8
                Rectangle { width: 12; height: 12; radius: 6; color: "#66BB6A" }
                Label { text: "Low (0-33%)"; font.pixelSize: 10; color: "#666" }
            }
            Row {
                spacing: 8
                Rectangle { width: 12; height: 12; radius: 6; color: "#FFA726" }
                Label { text: "Medium (34-66%)"; font.pixelSize: 10; color: "#666" }
            }
            Row {
                spacing: 8
                Rectangle { width: 12; height: 12; radius: 6; color: "#EF5350" }
                Label { text: "High (67-100%)"; font.pixelSize: 10; color: "#666" }
            }
            Rectangle {
                width: 130
                height: 1
                color: "#E0E0E0"
            }
            Label {
                text: "min " + minSampleSize + " infections per variety"
                font.pixelSize: 9
                color: "#999"
                font.italic: true
            }
        }
    }

    Timer {
        id: hideTimer
        interval: 2000
        onTriggered: tooltip.visible = false
    }

    function showTooltip(point) {
        console.log("Tooltip triggered for point:", point.x, point.y)

        for (var i = 0; i < currentPoints.length; i++) {
            if (Math.abs(currentPoints[i].x - point.x) < 0.1 &&
                Math.abs(currentPoints[i].y - point.y) < 0.1) {

                var data = currentPoints[i]
                console.log("Found data:", data.variety, data.disease, data.count, data.x, data.y)

                tooltipVariety.text = data.variety || "Unknown"
                tooltipDisease.text = "Disease: " + (data.disease || "N/A")
                tooltipStats.text = data.count + " out of " + data.x + " total infections"
                tooltipPercent.text = data.y.toFixed(1) + "% of infections"
                tooltip.visible = true
                hideTimer.restart()
                break
            }
        }
    }

    function updateScatterData(points) {
        if (!points) return

        console.log("updateScatterData called with", points.length, "total points")

        // Filter points with minimum sample size
        var filteredPoints = []
        var filteredOut = 0
        for (var i = 0; i < points.length; i++) {
            if (points[i].x >= minSampleSize) {
                filteredPoints.push(points[i])
            } else {
                filteredOut++
            }
        }

        console.log("Filtered out", filteredOut, "points with <", minSampleSize, "infections")
        console.log("Keeping", filteredPoints.length, "points")

        currentPoints = filteredPoints

        lowSeries.clear()
        mediumSeries.clear()
        highSeries.clear()

        var maxX = 0
        for (var i = 0; i < filteredPoints.length; i++) {
            var p = filteredPoints[i]
            var percentage = p.y

            if (percentage < 33) {
                lowSeries.append(p.x, p.y)
                console.log("Low point:", p.variety, "-", p.disease, ":", p.x, "infections,", p.y, "%")
            } else if (percentage < 66) {
                mediumSeries.append(p.x, p.y)
                console.log("Medium point:", p.variety, "-", p.disease, ":", p.x, "infections,", p.y, "%")
            } else {
                highSeries.append(p.x, p.y)
                console.log("HIGH point:", p.variety, "-", p.disease, ":", p.x, "infections,", p.y, "%")
            }

            if (p.x > maxX) maxX = p.x
        }

        axisX.max = maxX > 0 ? maxX + Math.max(1, maxX * 0.15) : 10

        // Update title with filtered count
        if (filteredOut > 0) {
            chartTitle = "Variety Susceptibility (" + filteredPoints.length + " varieties shown)"
        } else {
            chartTitle = "Variety Susceptibility Analysis"
        }
    }
}