import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../../analysis/componets"

Rectangle {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true
    property string title: "Disease Distribution"

    color: "#ffffff"
    radius: 14
    border.color: "#bae6fd"
    border.width: 1

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

        PieSeriesChart {
            id: pieChart
            Layout.fillWidth: true
            Layout.fillHeight: true
            chartMapper: StatisticalAnalyzer ? StatisticalAnalyzer.plotModel.chartMapper : null
        }
    }
}