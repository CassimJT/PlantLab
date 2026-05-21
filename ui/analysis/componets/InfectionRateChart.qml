import QtQuick 2.15
import QtCharts
import QtQuick.Controls 2.15

Item {
    id: infectionRateChart
    property var chartMapper: null
    property string chartTitle: "Infection Rate by Variety & Disease"

    // Store all variety data for access on click
    property var allVarietyData: []

    onChartMapperChanged: {
        if (chartMapper) {
            chartMapper.infectionRateDataChanged.connect(updateFromMapper)
            updateFromMapper()
        }
    }

    function updateFromMapper() {
        if (!chartMapper) return

        var varieties = chartMapper.infectionRateCategories
        var diseaseGroups = chartMapper.diseaseGroups
        var valuesMatrix = chartMapper.infectionRateValuesMatrix

        if (varieties && diseaseGroups && valuesMatrix && varieties.length > 0) {
            updateGroupedBarData(varieties, diseaseGroups, valuesMatrix)
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#FAFAFA"
        radius: 4
        z: -1
    }

    // Scroll handle
    Rectangle {
        id: scrollHandle
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 8
        height: 6
        radius: 3
        color: "#FF9800"
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
            width: Math.max(parent.width, varietiesCount * 160)
            height: flickable.height
            theme: ChartView.ChartThemeLight
            backgroundColor: "transparent"
            animationOptions: ChartView.SeriesAnimations
            animationDuration: 800
            legend.visible: true
            legend.alignment: Qt.AlignTop
            //legend.font.pointSize: 9

            property int varietiesCount: 0

            BarSeries {
                id: barSeries
                axisX: axisX
                axisY: axisY
                barWidth: 0.85
                labelsVisible: false
            }

            ValueAxis {
                id: axisY
                min: 0
                max: 100
                titleText: "Percentage of Infections (%)"
                titleVisible: true
                gridVisible: true
            }

            BarCategoryAxis {
                id: axisX
                titleText: "Variety"
                titleVisible: true
                categories: []
                labelsAngle: 45
                labelsFont.pointSize: 10
            }
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
            text: infectionRateChart.chartTitle
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

    // Top-center popup
    Rectangle {
        id: popup
        visible: false
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 50
        width: 350
        height: popupContentColumn.implicitHeight + 30
        color: "#2C3E50"
        opacity: 0.95
        radius: 8
        z: 10

        Column {
            id: popupContentColumn
            anchors.centerIn: parent
            spacing: 10
            width: parent.width - 20

            Label {
                id: popupTitle
                width: parent.width
                color: "#FF9800"
                font.pixelSize: 14
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
            }

            Rectangle {
                width: parent.width
                height: 1
                color: "#555555"
            }

            Column {
                id: popupDiseaseColumn
                width: parent.width
                spacing: 6
            }
        }

        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 3
            radius: 2
            color: "#FF9800"
        }
    }

    Timer {
        id: popupTimer
        interval: 10000
        onTriggered: popup.visible = false
    }

    function updateGroupedBarData(varieties, diseaseGroups, valuesMatrix) {
        // Clear existing bar sets
        while (barSeries.count > 0) {
            barSeries.remove(barSeries.at(0))
        }

        axisX.categories = varieties
        chartView.varietiesCount = varieties.length

        if (!varieties.length || !diseaseGroups.length) return

        var colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
                      "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E2"]

        // Calculate totals per variety
        var totals = []
        for (var j = 0; j < varieties.length; j++) {
            var total = 0
            for (var i = 0; i < diseaseGroups.length; i++) {
                if (valuesMatrix[j] && valuesMatrix[j][i]) {
                    total += valuesMatrix[j][i]
                }
            }
            totals.push(total)
        }

        // Store data for popup
        allVarietyData = []
        for (var j = 0; j < varieties.length; j++) {
            var diseases = []
            for (var i = 0; i < diseaseGroups.length; i++) {
                var count = (valuesMatrix[j] && valuesMatrix[j][i]) ? valuesMatrix[j][i] : 0
                if (count > 0) {
                    var pct = totals[j] > 0 ? Math.round((count / totals[j]) * 100) : 0
                    diseases.push({
                        name: diseaseGroups[i],
                        count: count,
                        percentage: pct,
                        color: colors[i % colors.length]
                    })
                }
            }
            diseases.sort(function(a, b) {
                return b.percentage - a.percentage
            })
            allVarietyData.push({
                name: varieties[j],
                total: totals[j],
                diseases: diseases
            })
        }

        // Create bar sets
        for (var i = 0; i < diseaseGroups.length; i++) {
            var percentages = []
            for (var j = 0; j < varieties.length; j++) {
                var count = (valuesMatrix[j] && valuesMatrix[j][i]) ? valuesMatrix[j][i] : 0
                var pct = totals[j] > 0 ? (count / totals[j]) * 100 : 0
                percentages.push(pct)
            }

            var barSet = barSeries.append(diseaseGroups[i], percentages)
            barSet.color = colors[i % colors.length]
            barSet.borderColor = Qt.darker(barSet.color, 1.2)
            barSet.borderWidth = 1

            // Simple click handler
            barSet.clicked.connect(function(index) {
                showPopupForVariety(index)
            })
        }

        // Adjust label angles
        if (varieties.length > 15) {
            axisX.labelsAngle = 75
            axisX.labelsFont.pointSize = 8
        } else if (varieties.length > 10) {
            axisX.labelsAngle = 60
            axisX.labelsFont.pointSize = 9
        } else if (varieties.length > 6) {
            axisX.labelsAngle = 45
        } else {
            axisX.labelsAngle = 30
        }
    }

    function showPopupForVariety(varietyIndex) {
        // Clear previous items - FIXED: use destroy() properly
        var children = popupDiseaseColumn.children
        for (var i = children.length - 1; i >= 0; i--) {
            var child = children[i]
            child.destroy()
        }

        var data = allVarietyData[varietyIndex]
        if (!data || data.total === 0) return

        popupTitle.text = data.name + " - Total: " + data.total + " infections"

        // Add each disease row
        for (var i = 0; i < data.diseases.length; i++) {
            var disease = data.diseases[i]

            // Create row using createObject instead of string
            var component = Qt.createComponent("diseaseRowComponent.qml")
            if (component.status === Component.Ready) {
                var row = component.createObject(popupDiseaseColumn, {
                    diseaseColor: disease.color,
                    diseaseName: disease.name,
                    diseasePercentage: disease.percentage,
                    diseaseCount: disease.count
                })
            } else {
                // Fallback to inline creation
                var rowString = 'import QtQuick 2.15; Row { spacing: 8; Rectangle { width: 12; height: 12; radius: 2; color: "' + disease.color + '"; anchors.verticalCenter: parent.verticalCenter } Text { text: "' + disease.name + ':"; color: "white"; font.pixelSize: 12; anchors.verticalCenter: parent.verticalCenter } Text { text: "' + disease.percentage + '%"; color: "' + disease.color + '"; font.pixelSize: 12; font.bold: true; anchors.verticalCenter: parent.verticalCenter } Text { text: "(" + disease.count + " cases)"; color: "#CCCCCC"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter } }'
                var row = Qt.createQmlObject(rowString, popupDiseaseColumn, "diseaseRow")
            }
        }

        popup.visible = true
        popupTimer.restart()
    }
}