import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    Layout.fillWidth: true
    Layout.fillHeight: true

    property string title: "Distribution"

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
            Layout.fillWidth: true
            Layout.fillHeight: true
            antialiasing: true
            legend.visible: true
            legend.alignment: Qt.AlignBottom  // Place legend at the bottom
            legend.markerShape: ChartLegend.MarkerShapeCircle
            backgroundColor: "transparent"

            PieSeries {
                //animated: true  //

                PieSlice { label: "Healthy"; value: 40; exploded: true } // Expanded by default
                PieSlice { label: "Pests"; value: 25 }
                PieSlice { label: "Diseases"; value: 15 }
                PieSlice { label: "Unknown"; value: 10 }
                PieSlice { label: "Weeds"; value: 10 }
            }
        }
    }
}