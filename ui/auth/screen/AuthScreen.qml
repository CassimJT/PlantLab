import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls
import QtQuick.Layouts
import "../pages"

Window {
    width: 600
    height: 600
    visible: true
    title: "Auth"

    modality: Qt.ApplicationModal
    flags: Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint

    StackLayout {
        id: authStackLayout
        currentIndex: 1
        SignInPage{

        }
        SignUpPage {

        }
    }

}
