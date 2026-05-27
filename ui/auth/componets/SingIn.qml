import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    id: signInPage
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

            //  Heading
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

            //  Card
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

                    //  Email field
                    Rectangle {
                        Layout.fillWidth: true
                        height: 56
                        radius: 12
                        color: "#FAFAFA"
                        border.color: emailField.activeFocus ? "#8FAF8F" : "#000000"
                        border.width: emailField.activeFocus ? 1.5 : 1

                        Behavior on border.color { ColorAnimation { duration: 150 } }

                        Text {
                            text: "Email"
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

                    //  Password field
                    Rectangle {
                        Layout.fillWidth: true
                        height: 56
                        radius: 12
                        color: "#FAFAFA"
                        border.color: passwordField.activeFocus ? "#8FAF8F" : "#000000"
                        border.width: passwordField.activeFocus ? 1.5 : 1

                        Behavior on border.color { ColorAnimation { duration: 150 } }

                        Text {
                            text: "Password"
                            color: "#000000"
                            font.pixelSize: 14
                            anchors.verticalCenter: parent.verticalCenter
                            x: 16
                            visible: passwordField.text.length === 0 && !passwordField.activeFocus
                        }

                        TextField {
                            id: passwordField
                            anchors {
                                fill: parent
                                leftMargin: 16; rightMargin: 14
                            }
                            placeholderText: ""
                            color: "#000000"
                            font.pixelSize: 14
                            background: Item {}
                            echoMode: TextInput.Password
                            verticalAlignment: TextInput.AlignVCenter
                        }
                    }

                    Item { Layout.preferredHeight: 4 }

                    //  Sign In button
                    Rectangle {
                        Layout.fillWidth: true
                        height: 52
                        radius: 14
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: signInMA.pressed ? "#2a9e48" : "#34c45a" }
                            GradientStop { position: 1.0; color: signInMA.pressed ? "#3dbf60" : "#5dde7a" }
                        }

                        Rectangle {
                            anchors { top: parent.top; left: parent.left; right: parent.right }
                            height: parent.height / 2
                            radius: parent.radius
                            color: "#1affffff"
                        }

                        Text {
                            anchors.centerIn: parent
                            text: "Sign In"
                            font.family: "Georgia"
                            font.pixelSize: 16
                            color: "#FFFFFF"
                            font.letterSpacing: 0.4
                        }

                        MouseArea {
                            id: signInMA
                            anchors.fill: parent
                            onClicked: {
                                mainStackView?.push("home/screens/HomeScreen.qml")
                            }
                        }
                    }

                    Item { Layout.preferredHeight: 2 }

                    //  Create account
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
                            color: "#34c45a"
                            font.underline: true
                            anchors.verticalCenter: parent.verticalCenter

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    mainStackView.push("ui/auth/pages/SignUpPage.qml")
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
