import QtQuick
import QtQuick.Shapes
import QtQuick.Layouts
import QtQuick.Controls

Item {
    id: progress

    implicitWidth: parent.width * 0.75
    implicitHeight: parent.width * 0.75

    // scaling reference
    property real gaugeSize: Math.min(width, height)
    property real scaleFactor: gaugeSize / 200

    // Properties
    property bool roundCap: true
    property int progressWidth: 16
    property int samples: 4
    property bool textShowValue: true
    property string textFontFamily: "Segoe UI"
    property int textSize: 12
    property color textColor: "#7c7c7c"

    // Bg Circle
    property color bgColor: "transparent"
    property color bgStrokeColor: "#7e7e7e"
    property int strokeBgWidth: 16

    // Progress Circle
    property color t_progressColor: "#55aaff"
    property color h_progressColor: "#f50057"

    property bool isTempCritical: false

    // Text
    property string t_unit: "°C"
    property string h_unit: "%"
    property string stateLabel: "OFF"

    //progress start & end
    property int h_startAngle: -80
    property int h_sweepAngle: 160
    property int t_startAngle: -260
    property int t_sweepAngle: 160

    //maximum progress
    property real t_maxValue: 83.33
    property real h_maxValue: 100

    //progress values
    property real t_value: 0
    property real h_value: 0

    // Images
    property real iconSize: 32 * scaleFactor

    // label colors
    property color stateLableColor: "Cyan"
    property color valuesLableColor: "Gray"

    property real valuesLableSize: Math.max(8, 12 * scaleFactor)

    //signals
    signal connectClicked()

    // dotted line
    Canvas {
        id: outerDotted
        anchors.centerIn: parent
        opacity: 0.4
        width: parent.width + 2 * (progress.strokeBgWidth + 4)
        height: parent.height + 2 * (progress.strokeBgWidth + 4)

        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0,0,width,height)

            var cx = width / 2
            var cy = height / 2
            var gauge_r = Math.min(parent.width, parent.height) / 2
            var r = gauge_r + progress.strokeBgWidth + 2

            var dots = 40
            ctx.fillStyle = "#555"

            for (var i = 0; i < dots; i++) {
                var ang = (i / dots) * Math.PI * 2
                var x = cx + Math.cos(ang) * r
                var y = cy + Math.sin(ang) * r

                ctx.beginPath()
                ctx.arc(x, y, 2, 0, Math.PI * 2)
                ctx.fill()
            }
        }
    }

    Shape {
        id: shape
        anchors.fill: parent
        layer.enabled: true
        layer.samples: progress.samples

        // temperature background
        ShapePath {
            strokeColor: progress.bgStrokeColor
            fillColor: progress.bgColor
            strokeWidth: progress.strokeBgWidth
            capStyle: progress.roundCap ? ShapePath.RoundCap : ShapePath.FlatCap

            PathAngleArc {
                radiusX: (progress.width / 2) - (progress.progressWidth / 2)
                radiusY: (progress.height / 2) - (progress.progressWidth / 2)
                centerX: progress.width / 2
                centerY: progress.height / 2
                startAngle: progress.t_startAngle
                sweepAngle: progress.t_sweepAngle
            }
        }

        // humidity background
        ShapePath {
            strokeColor: progress.bgStrokeColor
            fillColor: progress.bgColor
            strokeWidth: progress.strokeBgWidth
            capStyle: progress.roundCap ? ShapePath.RoundCap : ShapePath.FlatCap

            PathAngleArc {
                radiusX: (progress.width / 2) - (progress.progressWidth / 2)
                radiusY: (progress.height / 2) - (progress.progressWidth / 2)
                centerX: progress.width / 2
                centerY: progress.height / 2
                startAngle: progress.h_startAngle
                sweepAngle: progress.h_sweepAngle
            }
        }

        // temperature fill
        ShapePath {
            strokeColor: progress.t_progressColor
            fillColor: "transparent"
            strokeWidth: progress.progressWidth
            capStyle: progress.roundCap ? ShapePath.RoundCap : ShapePath.FlatCap

            PathAngleArc {
                radiusX: (progress.width / 2) - (progress.progressWidth / 2)
                radiusY: (progress.height / 2) - (progress.progressWidth / 2)
                centerX: progress.width / 2
                centerY: progress.height / 2
                startAngle: progress.t_startAngle
                sweepAngle: (progress.t_sweepAngle / progress.t_maxValue * progress.t_value)
            }
        }

        // humidity fill
        ShapePath {
            strokeColor: progress.h_progressColor
            fillColor: "transparent"
            strokeWidth: progress.progressWidth
            capStyle: progress.roundCap ? ShapePath.RoundCap : ShapePath.FlatCap

            PathAngleArc {
                radiusX: (progress.width / 2) - (progress.progressWidth / 2)
                radiusY: (progress.height / 2) - (progress.progressWidth / 2)
                centerX: progress.width / 2
                centerY: progress.height / 2
                startAngle: -(progress.h_startAngle)
                sweepAngle: -(progress.h_sweepAngle / progress.h_maxValue * progress.h_value)
            }
        }

        // warning icon
        Image {
            id: warning
            width: 52 * progress.scaleFactor
            height: width
            visible: isTempCritical
            source: "qrc:/assets/dashboard/warning.png"
            fillMode: Image.PreserveAspectFit

            anchors {
                bottom: rowLayout.top
                horizontalCenter: rowLayout.horizontalCenter
            }
        }

        // center layout
        RowLayout {
            id: rowLayout
            anchors.centerIn: parent
            spacing: 5 * progress.scaleFactor

            // temperature
            ColumnLayout {
                spacing: 5 * progress.scaleFactor

                Image {
                    Layout.preferredWidth: progress.iconSize
                    Layout.preferredHeight: progress.iconSize
                    source: "qrc:/assets/dashboard/temperature.png"
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignHCenter
                }

                Label {
                    id: tempValue
                    text: progress.t_value + t_unit
                    font.pointSize: progress.valuesLableSize
                    color: progress.valuesLableColor
                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideRight
                    Layout.alignment: Qt.AlignHCenter
                }
            }

            Label {
                id: state
                text: progress.stateLabel
                font.pointSize: Math.max(10, 14 * progress.scaleFactor)
                font.bold: true
                color: progress.stateLableColor
                Layout.alignment: Qt.AlignCenter
            }

            // humidity
            ColumnLayout {
                spacing: 5 * progress.scaleFactor

                Image {
                    Layout.preferredWidth: progress.iconSize
                    Layout.preferredHeight: progress.iconSize
                    source: "qrc:/assets/dashboard/ihumidity.png"
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignHCenter
                }

                Label {
                    id: humValue
                    text: progress.h_value + h_unit
                    font.pointSize: progress.valuesLableSize
                    color: progress.valuesLableColor
                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideRight
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }

        Label {
            text: "Heating"
            visible: t_value > 40

            anchors {
                top: rowLayout.bottom
                topMargin: 10 * progress.scaleFactor
                horizontalCenter: rowLayout.horizontalCenter
            }
        }

        Image {
            id: connect
            width: 26 * progress.scaleFactor
            height: width
            source: "qrc:/assets/com/connect.png"
            fillMode: Image.PreserveAspectFit
            visible: state.text === "OFF"

            anchors {
                top: rowLayout.bottom
                topMargin: 10 * progress.scaleFactor
                horizontalCenter: rowLayout.horizontalCenter
            }

            MouseArea {
                anchors.fill: parent
                onClicked: connectClicked()
            }
        }
    }

    Timer {
        running: true
        interval: 1000
        repeat: true

        onTriggered: {
            if (t_value > 40)
                isTempCritical = !isTempCritical
            else
                isTempCritical = false
        }
    }

    BusyIndicator {
        anchors.centerIn: parent
    }
}
