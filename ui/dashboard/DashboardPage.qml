import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "./component"

Page {
    id: dashboard
    property real metricCardheight: dashboard.height * 0.22
    property real chartHeight: dashboard.height * 0.32
    background: Rectangle {
        color: Qt.rgba(0,0,0,0)
        radius: 10
    }

    ColumnLayout {
        id: content
        width: parent.width
        spacing: 20
        anchors.fill: parent
        anchors.margins: 20

        /* =====================
               SECTION 1 — METRICS
               ===================== */
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16

            MetricCard {
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.metricCardheight
            }
            MetricCard {
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.metricCardheight
            }

            MetricCard {
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.metricCardheight
            }
            MetricCard {
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.metricCardheight
            }
        }

        /* =====================
               SECTION 2 — BAR CHARTS
               ===================== */
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16

            ChartCard {
                id:barcharts
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.height * .40
                BusyIndicator {
                    anchors.centerIn: parent
                }
            }

        }

        /* =====================
               SECTION 3 — PIE CHARTS
               ===================== */
        RowLayout {
            Layout.fillWidth: true
            spacing: 16
            Layout.fillHeight: true

            ChartCard {
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.chartHeight
            }
            ChartCard {
                Layout.fillWidth: true
                Layout.preferredHeight: dashboard.chartHeight
            }
        }
    }


}
