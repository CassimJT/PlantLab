import QtQuick 2.15
import QtGraphs
import QtQuick.Controls

Item {
    id: barSeriesChart
    property var chartMapper: null
    property string chartTitle: "Disease Frequency Distribution"

    onChartMapperChanged: {
        if (chartMapper) {
            chartMapper.barDataChanged.connect(updateFromMapper)
            updateFromMapper()
        }
    }

    function updateFromMapper() {
        if (!chartMapper) return
        var categories = chartMapper.barCategories
        var values = chartMapper.barValues
        var seriesName = chartMapper.barSeriesName || "Infections"

        console.log("Updating bar chart from mapper:", categories ? categories.length : 0, "bars")

        if (categories && values && categories.length > 0) {
            updateBarData(categories, values, seriesName)
        }
    }

    GraphsView {
        id: barChartView
        anchors.fill: parent
        anchors.margins: 10

        BarSeries {
            id: barSeries
            axisX: axisX
            axisY: axisY
            barWidth: 0.7
            labelsVisible: true
            labelsPosition: BarSeries.LabelsPosition.OutsideEnd
            labelsFormat: "%.0f"

            BarSet {
                id: mainBarSet
                label: "Infections"
                color: "#3498db"
                borderColor: "#2980b9"
                borderWidth: 1
            }

            ValueAxis {
                id: axisY
                min: 0
                titleText: "Number of Infections"
                titleVisible: true
            }

            BarCategoryAxis {
                id: axisX
                titleText: "Disease / Variety"
                titleVisible: true
                categories: []
            }
        }
    }

    Label {
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 5
        text: barSeriesChart.chartTitle
        font.bold: true
        font.pixelSize: 14
        z: 1
    }

    function updateBarData(categories, values, titleText) {
        console.log("Updating bar chart:", categories.length, "bars")

        // Update categories and values
        axisX.categories = categories
        mainBarSet.values = values

        if (titleText)
            chartTitle = titleText

        // Auto-scale Y axis
        if (values && values.length > 0) {
            var maxVal = Math.max.apply(null, values)
            axisY.max = maxVal + Math.max(1, maxVal * 0.1)
        } else {
            axisY.max = 10
        }
    }
}