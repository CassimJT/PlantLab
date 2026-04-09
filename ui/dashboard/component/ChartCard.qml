import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true

    property string title: "Pest & Disease Frequency"
    property var chartData: [12, 19, 7, 10, 15, 8, 14, 11, 18, 6]  // 10 records

    color: "#ffffff"
    radius: 14
    border.color: "#bae6fd"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 6

        Label {
            text: root.title
            font.bold: true
            font.pixelSize: 16
        }

        ChartView {
            id: chartView
            Layout.fillWidth: true
            Layout.fillHeight: true
            antialiasing: true
            legend.visible: false
            backgroundColor: "transparent"

            // Enable default animation for BarSeries
            animationOptions: ChartView.SeriesAnimations
            animationDuration: 800
            animationEasingCurve: Easing.InOutQuad

            BarSeries {
                id: barSeries
                axisX: BarCategoryAxis {
                    categories: ["Aphids", "Armyworm", "Blight", "Rust", "Mite",
                                 "Weevil", "Mildew", "Smut", "Leaf Spot", "Anthracnose"]
                }
                barWidth: 0.5  // Medium bar width

                BarSet {
                    id: barSet
                    label: "Detected Cases"
                    values: chartData
                    color: "#8BC34A"
                    borderColor: "#059669"
                    borderWidth: 0

                    // Smooth animation on value changes
                    Behavior on values {
                        NumberAnimation {
                            duration: 600
                            easing.type: Easing.InOutQuad
                        }
                    }
                }
            }

            ValueAxis {
                id: valueAxis
                min: 0
                max: 25
                titleText: "Cases Detected"
                labelsColor: "#6b7280"
                gridVisible: true
                gridLineColor: "#e5e7eb"
            }
        }
    }

    Component.onCompleted: {
        chartView.update(); // Trigger the initial animation
    }
}