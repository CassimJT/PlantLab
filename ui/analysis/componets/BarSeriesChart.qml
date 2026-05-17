import QtQuick 2.15
import QtCharts
import QtQuick.Controls

Item {
    id: barSeriesChart
    property var chartMapper: null
    property string chartTitle: "Disease Frequency Distribution"
    property var currentCategories: []
    property var currentValues: []

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

        if (seriesName && seriesName !== "Infections") {
            chartTitle = seriesName
        }

        if (categories && values && categories.length > 0) {
            updateBarData(categories, values, seriesName)
        }
    }

    // Subtle background
    Rectangle {
        anchors.fill: parent
        color: "#FAFAFA"
        radius: 4
        z: -1
    }

    // Custom scroll bar handle
    Rectangle {
        id: scrollHandle
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 8
        height: 6
        radius: 3
        color: "#42A5F5"
        opacity: (flickable.contentWidth > flickable.width) ? 0.8 : 0
        visible: opacity > 0
        z: 3

        width: Math.max(50, (flickable.width / flickable.contentWidth) * (parent.width - 40))

        x: 20 + ((flickable.contentX / (flickable.contentWidth - flickable.width)) * (parent.width - width - 40))

        MouseArea {
            anchors.fill: parent
            drag.target: parent
            drag.axis: Drag.XAxis
            drag.minimumX: 20
            drag.maximumX: scrollHandle.parent.width - scrollHandle.width - 20

            onPositionChanged: {
                var ratio = (scrollHandle.x - 20) / (scrollHandle.parent.width - scrollHandle.width - 40)
                flickable.contentX = ratio * (flickable.contentWidth - flickable.width)
            }
        }
    }

    Flickable {
        id: flickable
        anchors.fill: parent
        anchors.topMargin: 45
        anchors.bottomMargin: 30
        anchors.margins: 15
        contentWidth: chartView.width
        contentHeight: chartView.height
        clip: true
        flickableDirection: Flickable.HorizontalFlick

        // Scroll indicator text
        Label {
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.margins: 5
            text: "← Scroll →"
            font.pixelSize: 10
            color: "#999999"
            visible: flickable.contentWidth > flickable.width
            z: 2
        }

        ChartView {
            id: chartView
            width: Math.min(
                Math.max(parent.width, currentCategories.length * 80),
                currentCategories.length * 120
            )
            height: flickable.height
            theme: ChartView.ChartThemeLight
            backgroundColor: "transparent"
            animationOptions: ChartView.SeriesAnimations
            animationDuration: 800

            BarSeries {
                id: barSeries
                axisX: axisX
                axisY: axisY
                barWidth: Math.min(0.8, Math.max(0.5, 0.7 / Math.sqrt(currentCategories.length)))
                labelsVisible: false

                BarSet {
                    id: mainBarSet
                    label: "Infections"
                    color: "#42A5F5"
                    borderColor: "#1E88E5"
                    borderWidth: 1

                    onClicked: (index) => {
                        var category = axisX.categories[index]
                        var value = mainBarSet.values[index]
                        var maxVal = currentValues.length > 0 ? Math.max.apply(null, currentValues) : 1
                        var percentage = ((value / maxVal) * 100).toFixed(1)

                        tooltipText.text = category + " | Infections: " + value + " | " + percentage + "%"
                        tooltip.visible = true
                        hideTimer.restart()
                    }
                }
            }

            ValueAxis {
                id: axisY
                min: 0
                titleText: "Number of Infections"
                titleVisible: true
                gridVisible: true
            }

            BarCategoryAxis {
                id: axisX
                titleText: "Disease / Variety"
                titleVisible: true
                categories: []
                labelsAngle: 0
                labelsFont.pointSize: 10
            }
        }
    }

    // Professional title
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
            text: barSeriesChart.chartTitle
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

    // Tooltip popup - fixed at top center
    Rectangle {
        id: tooltip
        visible: false
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 50
        width: tooltipText.implicitWidth + 32
        height: tooltipText.implicitHeight + 16
        color: "#2C3E50"
        radius: 8
        z: 10

        Label {
            id: tooltipText
            anchors.centerIn: parent
            color: "white"
            font.pixelSize: 12
            font.weight: Font.Medium
            horizontalAlignment: Text.AlignCenter
        }

        // Decorative line at top
        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 3
            radius: 2
            color: "#42A5F5"
        }
    }

    Timer {
        id: hideTimer
        interval: 3000
        onTriggered: tooltip.visible = false
    }

    function updateBarData(categories, values, titleText) {
        currentCategories = categories
        currentValues = values

        // Clear existing barsets
        while (barSeries.count > 0) {
            barSeries.remove(barSeries.at(0))
        }

        axisX.categories = categories

        if (values && values.length > 0) {
            var maxVal = Math.max.apply(null, values)

            var barSet = barSeries.append("Infections", values)
            barSet.color = "#42A5F5"
            barSet.borderColor = "#1E88E5"
            barSet.borderWidth = 1

            // Connect click handler
            barSet.clicked.connect(function(index) {
                var category = categories[index]
                var value = values[index]
                var percentage = ((value / maxVal) * 100).toFixed(1)
                tooltipText.text = category + " | Infections: " + value + " | " + percentage + "%"
                tooltip.visible = true
                hideTimer.restart()
            })

            axisY.max = maxVal + Math.max(1, maxVal * 0.15)

            // Label rotation based on number of categories
            if (categories.length > 15) {
                axisX.labelsAngle = 75
                axisX.labelsFont.pointSize = 9
            } else if (categories.length > 10) {
                axisX.labelsAngle = 60
                axisX.labelsFont.pointSize = 9
            } else if (categories.length > 6) {
                axisX.labelsAngle = 45
                axisX.labelsFont.pointSize = 10
            } else if (categories.length > 3) {
                axisX.labelsAngle = 30
                axisX.labelsFont.pointSize = 10
            } else {
                axisX.labelsAngle = 0
                axisX.labelsFont.pointSize = 11
            }

        } else {
            axisY.max = 10
        }
    }
}