import QtQuick 2.15
import QtCharts
import QtQuick.Controls

Item {
    id: scatterSeriesChart
    property var chartMapper: null
    property string chartTitle: "Variety Susceptibility Analysis"
    property var currentPoints: []

    onChartMapperChanged: {
        if (chartMapper) {
            chartMapper.scatterDataChanged.connect(updateFromMapper)
            updateFromMapper()
        }
    }

    function updateFromMapper() {
        if (!chartMapper) return
        var points = chartMapper.scatterPoints
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
            markerSize: 12
            markerShape: ScatterSeries.MarkerShapeCircle
            name: "Low Susceptibility (0-33%)"

            onHovered: (point, hovered) => {
                if (hovered && point) {
                    var varietyName = "Unknown"
                    for (var i = 0; i < currentPoints.length; i++) {
                        if (Math.abs(currentPoints[i].x - point.x) < 0.1 &&
                            Math.abs(currentPoints[i].y - point.y) < 0.1) {
                            varietyName = currentPoints[i].variety || currentPoints[i].name || "Unknown"
                            break
                        }
                    }
                    tooltipText.text = "Variety: " + varietyName +
                                       "\nSusceptibility: " + point.y.toFixed(1) + "%" +
                                       "\nInfections: " + point.x.toFixed(0)
                    tooltip.visible = true
                    hideTimer.restart()
                } else if (!hovered) {
                    hideTimer.start()
                }
            }
        }

        ScatterSeries {
            id: mediumSeries
            axisX: axisX
            axisY: axisY
            color: "#FFA726"
            borderColor: "#F57C00"
            markerSize: 12
            markerShape: ScatterSeries.MarkerShapeCircle
            name: "Medium Susceptibility (34-66%)"

            onHovered: (point, hovered) => {
                if (hovered && point) {
                    var varietyName = "Unknown"
                    for (var i = 0; i < currentPoints.length; i++) {
                        if (Math.abs(currentPoints[i].x - point.x) < 0.1 &&
                            Math.abs(currentPoints[i].y - point.y) < 0.1) {
                            varietyName = currentPoints[i].variety || currentPoints[i].name || "Unknown"
                            break
                        }
                    }
                    tooltipText.text = "Variety: " + varietyName +
                                       "\nSusceptibility: " + point.y.toFixed(1) + "%" +
                                       "\nInfections: " + point.x.toFixed(0)
                    tooltip.visible = true
                    hideTimer.restart()
                } else if (!hovered) {
                    hideTimer.start()
                }
            }
        }

        ScatterSeries {
            id: highSeries
            axisX: axisX
            axisY: axisY
            color: "#EF5350"
            borderColor: "#C62828"
            markerSize: 12
            markerShape: ScatterSeries.MarkerShapeCircle
            name: "High Susceptibility (67-100%)"

            onHovered: (point, hovered) => {
                if (hovered && point) {
                    var varietyName = "Unknown"
                    for (var i = 0; i < currentPoints.length; i++) {
                        if (Math.abs(currentPoints[i].x - point.x) < 0.1 &&
                            Math.abs(currentPoints[i].y - point.y) < 0.1) {
                            varietyName = currentPoints[i].variety || currentPoints[i].name || "Unknown"
                            break
                        }
                    }
                    tooltipText.text = "Variety: " + varietyName +
                                       "\nSusceptibility: " + point.y.toFixed(1) + "%" +
                                       "\nInfections: " + point.x.toFixed(0)
                    tooltip.visible = true
                    hideTimer.restart()
                } else if (!hovered) {
                    hideTimer.start()
                }
            }
        }

        ValueAxis {
            id: axisX
            min: 0
            titleText: "Total Infections per Variety"
            titleVisible: true
            gridVisible: true
            labelsFont.pointSize: 10
        }

        ValueAxis {
            id: axisY
            min: 0
            max: 110
            titleText: "Disease Susceptibility (%)"
            titleVisible: true
            gridVisible: true
            labelsFont.pointSize: 10
        }
    }

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
            text: scatterSeriesChart.chartTitle
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

    // Tooltip popup - fixed at top center (same as bar chart)
    Rectangle {
        id: tooltip
        visible: false
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 50
        width: tooltipText.implicitWidth + 32
        height: tooltipText.implicitHeight + 20
        color: "#2C3E50"
        radius: 8
        z: 10

        Label {
            id: tooltipText
            anchors.centerIn: parent
            color: "white"
            font.pixelSize: 11
            font.weight: Font.Medium
            horizontalAlignment: Text.AlignCenter
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

    Rectangle {
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.margins: 10
        width: 160
        height: 95
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
                Label { text: "Low Susceptibility"; font.pixelSize: 10; color: "#666" }
            }
            Row {
                spacing: 8
                Rectangle { width: 12; height: 12; radius: 6; color: "#FFA726" }
                Label { text: "Medium Susceptibility"; font.pixelSize: 10; color: "#666" }
            }
            Row {
                spacing: 8
                Rectangle { width: 12; height: 12; radius: 6; color: "#EF5350" }
                Label { text: "High Susceptibility"; font.pixelSize: 10; color: "#666" }
            }
        }
    }

    Timer {
        id: hideTimer
        interval: 2000
        onTriggered: tooltip.visible = false
    }

    function updateScatterData(points) {
        if (!points) return
        currentPoints = points

        lowSeries.clear()
        mediumSeries.clear()
        highSeries.clear()

        for (var i = 0; i < points.length; i++) {
            var p = points[i]
            var percentage = p.y

            if (percentage < 33) {
                lowSeries.append(p.x, p.y)
            } else if (percentage < 66) {
                mediumSeries.append(p.x, p.y)
            } else {
                highSeries.append(p.x, p.y)
            }
        }

        if (points.length > 0) {
            var maxX = 0
            for (var i = 0; i < points.length; i++) {
                if (points[i].x > maxX) maxX = points[i].x
            }
            axisX.max = maxX + Math.max(1, maxX * 0.15)
        } else {
            axisX.max = 10
        }
    }
}