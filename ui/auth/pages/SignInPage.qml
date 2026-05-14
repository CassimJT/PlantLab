import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    id:signInPage
    property var stackView: null
    width: 360
    height: 800
    background: Rectangle { color: "#edf2e0" }

    Flickable {
        anchors.fill: parent
        contentHeight: mainColumn.implicitHeight + 60
        clip: true

        ColumnLayout {
            id: mainColumn
            width: parent.width
            spacing: 0

            Item { Layout.preferredHeight: 100 }

            // App Logo
            Image {
                id: appLogo
                source: "qrc:/assets/app_icon/PlantDocutor.png"
                fillMode: Image.PreserveAspectFit

                Layout.preferredWidth: 40
                Layout.preferredHeight: 40
                Layout.alignment: Qt.AlignHCenter
            }
            // ── Heading ─────────────────────────────────────────────────────
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Sign in to PlantDoctor"
                font.family: "Georgia"
                font.pixelSize: 26
                font.bold: true
                color: "#1A2E1F"
                font.letterSpacing: 0.3
            }

            Item { Layout.preferredHeight: 70 }
            // ── Card ─────────────────────────────────────────────────────────
            Rectangle {
                Layout.leftMargin: 20
                Layout.rightMargin: 20
                Layout.fillWidth: true
                implicitHeight: cardColumn.implicitHeight + 36
                radius: 20
                color: "#FFFFFF"
                border.color: "#000000"
                border.width: 1


                ColumnLayout {
                    id: cardColumn
                    anchors {
                        top: parent.top; left: parent.left; right: parent.right
                        topMargin: 28; leftMargin: 20; rightMargin: 20
                    }
                    spacing: 16
                    // ── Continue with Google ──────────────────────────────────
                    Rectangle {
                        Layout.fillWidth: true
                        height: 50
                        radius: 12
                        color: googleMA.pressed ? "#F0F0F0" : "#FAFAFA"
                        border.color: "#000000"
                        border.width: 1

                        Behavior on color { ColorAnimation { duration: 120 } }

                        Row {
                            anchors.centerIn: parent
                            spacing: 10

                            Item {
                                width: 22; height: 22
                                anchors.verticalCenter: parent.verticalCenter

                                Canvas {
                                    anchors.fill: parent
                                    onPaint: {
                                        var ctx = getContext("2d")
                                        ctx.clearRect(0, 0, width, height)
                                        var cx = width / 2
                                        var cy = height / 2
                                        var r  = width / 2

                                        ctx.beginPath()
                                        ctx.moveTo(cx, cy)
                                        ctx.arc(cx, cy, r, -0.5, 1.1)
                                        ctx.closePath()
                                        ctx.fillStyle = "#4285F4"
                                        ctx.fill()

                                        ctx.beginPath()
                                        ctx.moveTo(cx, cy)
                                        ctx.arc(cx, cy, r, 1.1, 2.2)
                                        ctx.closePath()
                                        ctx.fillStyle = "#EA4335"
                                        ctx.fill()

                                        ctx.beginPath()
                                        ctx.moveTo(cx, cy)
                                        ctx.arc(cx, cy, r, 2.2, 3.8)
                                        ctx.closePath()
                                        ctx.fillStyle = "#FBBC05"
                                        ctx.fill()

                                        ctx.beginPath()
                                        ctx.moveTo(cx, cy)
                                        ctx.arc(cx, cy, r, 3.8, -0.5)
                                        ctx.closePath()
                                        ctx.fillStyle = "#34A853"
                                        ctx.fill()

                                        ctx.beginPath()
                                        ctx.arc(cx, cy, r * 0.58, 0, Math.PI * 2)
                                        ctx.fillStyle = "#FAFAFA"
                                        ctx.fill()

                                        ctx.fillStyle = "#4285F4"
                                        ctx.fillRect(cx, cy - r * 0.18, r * 0.95, r * 0.36)

                                        ctx.beginPath()
                                        ctx.arc(cx, cy, r * 0.58, 0, Math.PI * 2)
                                        ctx.fillStyle = "#FAFAFA"
                                        ctx.fill()

                                        ctx.font = "bold 11px sans-serif"
                                        ctx.fillStyle = "#4285F4"
                                        ctx.textAlign = "center"
                                        ctx.textBaseline = "middle"
                                        ctx.fillText("G", cx + 0.5, cy + 0.5)
                                    }
                                }
                            }

                            Text {
                                text: "Continue with Google"
                                font.pixelSize: 14
                                color: "#000000"
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }

                        MouseArea {
                            id: googleMA
                            anchors.fill: parent
                            onClicked: console.log("Google sign-in tapped")
                        }
                    }
                    // ── Divider ───────────────────────────────────────────────
                    Row {
                        Layout.fillWidth: true
                        spacing: 8

                        Rectangle {
                            width: (cardColumn.width - 36) / 2
                            height: 1
                            color: "#000000"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            text: "or"
                            font.pixelSize: 12
                            color: "#000000"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Rectangle {
                            width: (cardColumn.width - 36) / 2
                            height: 1
                            color: "#000000"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    // ── Email / Phone field ───────────────────────────────────
                    Rectangle {
                        Layout.fillWidth: true
                        height: 56
                        radius: 12
                        color: "#FAFAFA"
                        border.color: emailField.activeFocus ? "#8FAF8F" : "#000000"
                        border.width: emailField.activeFocus ? 1.5 : 1

                        Behavior on border.color { ColorAnimation { duration: 150 } }

                        Text {
                            id: emailLabel
                            text: "Email or phone number"
                            color: "#000000"
                            font.pixelSize: 14
                            anchors.verticalCenter: parent.verticalCenter
                            x: 16
                            visible: emailField.text.length === 0 && !emailField.activeFocus
                        }

                        TextField {
                            id: emailField
                            anchors {
                                fill: parent
                                leftMargin: 16; rightMargin: 14
                            }
                            placeholderText: ""
                            color: "#000000"
                            font.pixelSize: 14
                            background: Item {}
                            inputMethodHints: Qt.ImhEmailCharactersOnly
                            verticalAlignment: TextInput.AlignVCenter
                        }
                    }
                    Item { Layout.preferredHeight: 4 }

                    // ── Continue button ───────────────────────────────────────
                    Rectangle {
                        Layout.fillWidth: true
                        height: 52
                        radius: 14
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: continueMA.pressed ? "#2a9e48" : "#34c45a" }
                            GradientStop { position: 1.0; color: continueMA.pressed ? "#3dbf60" : "#5dde7a" }
                        }

                        Behavior on color { ColorAnimation { duration: 120 } }

                        Rectangle {
                            anchors { top: parent.top; left: parent.left; right: parent.right }
                            height: parent.height / 2
                            radius: parent.radius
                            color: "#1affffff"
                        }

                        Text {
                            anchors.centerIn: parent
                            text: "Continue"
                            font.family: "Georgia"
                            font.pixelSize: 16
                            color: "#FFFFFF"
                            font.letterSpacing: 0.4
                        }

                        MouseArea {
                            id: continueMA
                            anchors.fill: parent
                            onClicked: {
                                mainStackView?.push("home/screens/HomeScreen.qml")
                            }
                        }
                    }
                    Item { Layout.preferredHeight: 2 }
                    // ── Create account ────────────────────────────────────────
                    Row {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 4

                        Text {
                            text: "Don't have an account?"
                            font.pixelSize: 13
                            color: "#000000"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            text: "Create account"
                            font.pixelSize: 13
                            font.bold: true
                            color:  "#34c45a"
                            font.underline: true
                            anchors.verticalCenter: parent.verticalCenter

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    stackView.push("ui/auth/pages/SignUpPage.qml")
                                }
                            }
                        }
                    }


                    Item { Layout.preferredHeight: 8 }
                }
            }

            Item { Layout.preferredHeight: 40 }
        }
    }
}









