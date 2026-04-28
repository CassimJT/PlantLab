import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true
    property string title: "Pest & Disease Frequency"
    property var chartData: [12, 19, 7, 10, 15, 8, 14, 11, 18, 6]
    property var categories: ["Aphids", "Armyworm", "Blight", "Rust", "Mite",
                              "Weevil", "Mildew", "Smut", "Leaf Spot", "Anthracnose"]

    color: "#ffffff"
    radius: 14
    border.color: "#bae6fd"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        Label {
            text: root.title
            font.bold: true
            font.pixelSize: 16
            color: "#1f2937"
        }

        ChartView {
            id: chartView
            Layout.fillWidth: true
            Layout.fillHeight: true
            antialiasing: true
            legend.visible: false
            backgroundColor: "transparent"
            animationOptions: ChartView.SeriesAnimations
            animationDuration: 800

            // X Axis - Category Axis (for disease names)
            BarCategoryAxis {
                id: axisX
                categories: root.categories
                labelsAngle: -45
                labelsFont.pixelSize: 11
                titleText: "Pest / Disease"
            }

            // Y Axis - Value Axis
            ValueAxis {
                id: axisY
                min: 0
                max: 25
                titleText: "Cases Detected"
                labelsColor: "#6b7280"
                gridVisible: true
                gridLineColor: "#e5e7eb"
            }

            BarSeries {
                id: barSeries
                axisX: axisX          // Correct way to link
                axisY: axisY          // Correct way to link
                barWidth: 0.6

                BarSet {
                    id: barSet
                    label: "Detected Cases"
                    values: root.chartData
                    color: "#8BC34A"
                    borderColor: "#059669"
                    borderWidth: 1

                    // Smooth animation when values change
                    Behavior on values {
                        NumberAnimation {
                            duration: 600
                            easing.type: Easing.InOutQuad
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        chartView.update()
    }
}