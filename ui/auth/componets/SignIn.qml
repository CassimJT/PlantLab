//signin Component
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Page {
    id: signIn
    width: 360
    height: 800
    background: Rectangle { color: "#edf2e0" }

    signal onContinue()
    signal onCreateAccount()
    property var authLoader: null

    ColumnLayout {
        id: mainColumn
        anchors.fill: parent
        spacing: 0

        Item { Layout.preferredHeight: 100 }

        // App Logo
        Image {
            id: appLogo
            source: "qrc:/assets/app_icon/PlantDocutor.png"
            fillMode: Image.PreserveAspectFit
            Layout.preferredWidth: 100
            Layout.preferredHeight: 100
            Layout.alignment: Qt.AlignHCenter
        }

        Item { Layout.preferredHeight: 20 }
        //  Heading
        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "Sign in to PlantDoctor"
            font.family: "Georgia"
            font.pixelSize: 30
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

                // Password field
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

                // Sign In button
                Rectangle {
                    Layout.fillWidth: true
                    height: 52
                    radius: 14
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: continueMA.pressed ? "#2a9e48" : "#34c45a" }
                        GradientStop { position: 1.0; color: continueMA.pressed ? "#3dbf60" : "#5dde7a" }
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
                        id: continueMA
                        anchors.fill: parent
                        onClicked: signIn.onContinue()
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
                                if (signIn.authLoader) {
                                    signIn.authLoader.source = "../componets/SignUp.qml"
                                } else {
                                    var window = signIn.Window.window
                                    if (window && window.authLoader) {
                                        window.authLoader.source = "../componets/SignUp.qml"
                                    }
                                }
                            }
                        }
                    }
                }

                Item { Layout.preferredHeight: 8 }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
