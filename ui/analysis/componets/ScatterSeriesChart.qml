import QtQuick 2.15
import QtGraphs
import QtQuick.Controls

Item {
    id: scatterSeriesChart
    property var chartMapper: null

    onChartMapperChanged: {
        if (chartMapper) {
            chartMapper.scatterDataChanged.connect(updateFromMapper)
            updateFromMapper()
        }
    }

    function updateFromMapper() {
        if (!chartMapper) return
        var points = chartMapper.scatterPoints
        console.log("Updating scatter chart from mapper:", points ? points.length : 0, "points")
        if (points && points.length > 0) {
            updateScatterData(points)
        }
    }

    GraphsView {
        id: scatterChartView
        anchors.fill: parent
        anchors.margins: 10

        ValueAxis {
            id: axisX
            min: 0
            titleText: "Total Infections per Variety"
            titleVisible: true
        }

        ValueAxis {
            id: axisY
            min: 0
            max: 100
            titleText: "Disease Percentage (%)"
            titleVisible: true
        }

        ScatterSeries {
            id: scatterSeries
            axisX: axisX
            axisY: axisY
            color: "#e74c3c"
           // markerSize: 8   // works in recent QtGraphs
        }
    }

    Label {
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 5
        text: "Variety Susceptibility Analysis"
        font.bold: true
        font.pixelSize: 14
        z: 1
    }

    function updateScatterData(points) {
        if (!points) return
        console.log("Updating scatter chart:", points.length, "points")

        scatterSeries.clear()   // Best way to remove old points

        for (var i = 0; i < points.length; i++) {
            var p = points[i]
            scatterSeries.append(p.x, p.y)
        }

        // Auto-scale X axis
        if (points.length > 0) {
            var maxX = 0
            for (var i = 0; i < points.length; i++) {
                if (points[i].x > maxX) maxX = points[i].x
            }
            axisX.max = maxX + Math.max(1, maxX * 0.1)
        }
    }
}