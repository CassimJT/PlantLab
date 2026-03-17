import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    height: 70
    Layout.fillWidth: true

    color: "#ffffff"
    border.color: "#e2e8f0"

    property string titleText: ""
    property string subtitleText: ""

    RowLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20

        /* ======================
           Logo + Title
           ====================== */
        RowLayout {
            spacing: 12
            Layout.alignment: Qt.AlignVCenter

            Rectangle {
                width: 40
                height: 40
                radius: 8
                color: "#0284c7"

                Text {
                    anchors.centerIn: parent
                    text: ""
                    font.pixelSize: 24
                    color: "white"
                }
            }

            ColumnLayout {
                spacing: 2

                Text {
                    text: root.titleText
                    font.pixelSize: 18
                    font.bold: true
                    color: "#0f172a"
                }

                Text {
                    text: root.subtitleText
                    font.pixelSize: 12
                    color: "#64748b"
                }
            }
        }

        /* Push right side */
        Item { Layout.fillWidth: true }

        /* ======================
           Right Controls
           ====================== */
        RowLayout {
            spacing: 20
            Layout.alignment: Qt.AlignVCenter

            /* Language selector */
            RowLayout {
                spacing: 8

                Text {
                    text: qsTr("Language") + ":"
                    font.pixelSize: 14
                    color: "#475569"
                }

                ComboBox {
                    id: languageCombo
                    width: 140

                    model: [
                        { text: "English", value: "en" },
                        { text: "Chichewa", value: "ny" }
                    ]

                    textRole: "text"
                    valueRole: "value"

                    currentIndex: InfarenceRunner.current_language() === "ny" ? 1 : 0

                    onActivated: {
                        if (currentValue)
                            InfarenceRunner.set_language(currentValue)
                    }

                    delegate: ItemDelegate {
                        width: languageCombo.width
                        text: modelData.text
                        highlighted: languageCombo.highlightedIndex === index
                    }

                    indicator: Canvas {
                        width: 12
                        height: 8

                        x: languageCombo.width - width - languageCombo.rightPadding
                        y: languageCombo.topPadding +
                           (languageCombo.availableHeight - height) / 2

                        contextType: "2d"

                        onPaint: {
                            var ctx = getContext("2d")
                            ctx.reset()

                            ctx.beginPath()
                            ctx.moveTo(0,0)
                            ctx.lineTo(width,0)
                            ctx.lineTo(width/2,height)
                            ctx.closePath()

                            ctx.fillStyle = "#64748b"
                            ctx.fill()
                        }
                    }
                }
            }

            /* ======================
               Category selector
               ====================== */
            RowLayout {
                spacing: 8

                Text {
                    text: qsTr("Type") + ":"
                    font.pixelSize: 14
                    color: "#475569"
                }

                ComboBox {
                    id: categoryCombo
                    width: 120

                    model: [
                        { text: qsTr("Disease"), value: "disease" },
                        { text: qsTr("Pest"), value: "pest" }
                    ]

                    textRole: "text"
                    valueRole: "value"

                    Component.onCompleted: {
                        currentIndex = 0
                    }

                    onActivated: function(index) {
                        if (model[index])
                            InfarenceRunner.set_category(model[index].value)
                    }

                    delegate: ItemDelegate {
                        width: categoryCombo.width
                        text: modelData.text
                        highlighted: categoryCombo.highlightedIndex === index
                    }
                }
            }
        }
    }
}
