import QtQuick
import QtQuick.Shapes

Item {
    id: progress

    implicitWidth: parent.width * 0.5
    implicitHeight: parent.height * 0.5

    // scaling reference
    property real gaugeSize: Math.min(width, height)
    property real scaleFactor: gaugeSize / 200

    // value
    property real rawValue: 0
    property real maxValue: 38
    property real value: rawValue

    // General
    property bool roundCap: true
    property int startAngle: -240
    property int samples: 4

    // Bg Circle
    property color bgColor: "transparent"
    property color bgStrokeColor: "#7e7e7e"
    property int strokeBgWidth: 16

    // Progress Circle
    property color progressColor: "#55aaff"
    property int progressWidth: 16

    // Text
    property string text: "Diseases"
    property bool textShowValue: true
    property string textFontFamily: "Segoe UI"
    property int textSize: Math.max(10, 12 * scaleFactor)
    property color textColor: "#7c7c7c"

    // icon scaling
    property real iconSize: 26 * scaleFactor

    // -----------------------------
    // DOTTED OUTER RING
    // -----------------------------
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

        // background arc
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
                startAngle: progress.startAngle
                sweepAngle: 300
            }
        }

        // progress arc
        ShapePath {
            strokeColor: progress.progressColor
            fillColor: "transparent"
            strokeWidth: progress.progressWidth
            capStyle: progress.roundCap ? ShapePath.RoundCap : ShapePath.FlatCap

            PathAngleArc {
                radiusX: (progress.width / 2) - (progress.progressWidth / 2)
                radiusY: (progress.height / 2) - (progress.progressWidth / 2)
                centerX: progress.width / 2
                centerY: progress.height / 2
                startAngle: progress.startAngle
                sweepAngle: (300 / progress.maxValue * progress.value)
            }
        }

        // value text (shows "n / total")
        Text {
            id: textProgress

            text: progress.textShowValue
                  ? Math.floor(progress.value) + " / " + Math.floor(progress.maxValue)
                  : ""

            anchors.centerIn: parent

            color: progress.textColor
            font.pointSize: progress.textSize
            font.family: progress.textFontFamily
            font.bold: true

            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }

        // icon
        Image {
            id: diseaseIcon

            width: progress.iconSize
            height: width

            source: "qrc:/Assert/icons8-disease-100.png"
            fillMode: Image.PreserveAspectFit

            anchors {
                bottom: textProgress.top
                horizontalCenter: textProgress.horizontalCenter
                bottomMargin: 5 * progress.scaleFactor
            }
        }
    }
}