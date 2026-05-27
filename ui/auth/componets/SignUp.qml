import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    id: signUpPage
    objectName: "SignUp"
    width: 360
    height: 800
    background: Rectangle { color: "#edf2e0" }
    signal onBack()
    signal onSignUp()
    property var authLoader: null

    Flickable {
        anchors.fill: parent
        contentHeight: mainColumn.implicitHeight + 60
        clip: true

        ColumnLayout {
            id: mainColumn
            width: parent.width
            spacing: 0

            Item { Layout.preferredHeight: 85 }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 72
                text: "Sign Up To PlantDoctor"
                font.family: "Georgia"
                font.pixelSize: 26
                color: "#1A2E1F"
                font.bold: true
                font.letterSpacing: 0.3
            }

            Item { Layout.preferredHeight: 60 }

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

                    Rectangle {
                        Layout.fillWidth: true
                        height: 56
                        radius: 12
                        color: "#FAFAFA"
                        border.color: nameField.activeFocus ? "#8FAF8F" : "#000000"
                        border.width: nameField.activeFocus ? 1.5 : 1

                        Behavior on border.color { ColorAnimation { duration: 150 } }

                        Text {
                            text: "Full Name"
                            color: "#000000"
                            font.pixelSize: 14
                            anchors.verticalCenter: parent.verticalCenter
                            x: 16
                            visible: nameField.text.length === 0 && !nameField.activeFocus
                        }

                        TextField {
                            id: nameField
                            anchors {
                                fill: parent
                                leftMargin: 16; rightMargin: 14
                            }
                            placeholderText: ""
                            color: "#000000"
                            font.pixelSize: 14
                            background: Item {}
                            verticalAlignment: TextInput.AlignVCenter
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 56
                        radius: 12
                        color: "#FAFAFA"
                        border.color: phoneNumberField.activeFocus ? "#8FAF8F" : "#000000"
                        border.width: phoneNumberField.activeFocus ? 1.5 : 1

                        Behavior on border.color { ColorAnimation { duration: 150 } }

                        Text {
                            text: "Phone Number"
                            color: "#000000"
                            font.pixelSize: 14
                            anchors.verticalCenter: parent.verticalCenter
                            x: 16
                            visible: phoneNumberField.text.length === 0 && !phoneNumberField.activeFocus
                        }

                        TextField {
                            id: phoneNumberField
                            anchors {
                                fill: parent
                                leftMargin: 16; rightMargin: 14
                            }
                            placeholderText: ""
                            color: "#000000"
                            font.pixelSize: 14
                            background: Item {}
                            verticalAlignment: TextInput.AlignVCenter
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 56
                        radius: 12
                        color: "#FAFAFA"
                        border.color: districtField.activeFocus ? "#8FAF8F" : "#000000"
                        border.width: districtField.activeFocus ? 1.5 : 1

                        Behavior on border.color { ColorAnimation { duration: 150 } }

                        Text {
                            text: "District"
                            color: "#000000"
                            font.pixelSize: 14
                            anchors.verticalCenter: parent.verticalCenter
                            x: 16
                            visible: districtField.text.length === 0 && !districtField.activeFocus
                        }

                        TextField {
                            id: districtField
                            anchors {
                                fill: parent
                                leftMargin: 16; rightMargin: 14
                            }
                            placeholderText: ""
                            color: "#000000"
                            font.pixelSize: 14
                            background: Item {}
                            verticalAlignment: TextInput.AlignVCenter
                        }
                    }

                    Item { Layout.preferredHeight: 4 }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 52
                        radius: 14
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: signUpMA.pressed ? "#2a9e48" : "#34c45a" }
                            GradientStop { position: 1.0; color: signUpMA.pressed ? "#3dbf60" : "#5dde7a" }
                        }

                        Rectangle {
                            anchors { top: parent.top; left: parent.left; right: parent.right }
                            height: parent.height / 2
                            radius: parent.radius
                            color: "#1affffff"
                        }

                        Text {
                            anchors.centerIn: parent
                            text: "Sign Up"
                            font.family: "Georgia"
                            font.pixelSize: 16
                            color: "#FFFFFF"
                            font.letterSpacing: 0.4
                        }

                        MouseArea {
                            id: signUpMA
                            anchors.fill: parent
                            onClicked: {
                                signUpPage.onSignUp()
                                console.log("Sign up tapped")
                            }
                        }
                    }

                    Row {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 4

                        Text {
                            text: "Already have an account?"
                            font.pixelSize: 13
                            color: "#000000"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                        Text {
                            text: "Sign in"
                            font.pixelSize: 13
                            font.bold: true
                            color: "#34c45a"
                            font.underline: true
                            anchors.verticalCenter: parent.verticalCenter

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    // Fixed: removed nested MouseArea
                                    if (signUpPage.authLoader) {
                                        signUpPage.authLoader.source = "../componets/SignIn.qml"
                                    } else {
                                        var window = signUpPage.Window.window
                                        if (window && window.authLoader) {
                                            window.authLoader.source = "../componets/SignIn.qml"
                                        }
                                    }
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