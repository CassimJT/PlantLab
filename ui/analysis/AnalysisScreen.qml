import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts
import "./delegate"
import "./model"


Page {
    id: root
    // ====== TOP BAR ======
    Rectangle {
        id: topBar
        height: 52
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        color: "#ffffff"
        border.color: "#e5e7eb"

        RowLayout {
            anchors.fill: parent
            anchors.margins: 12

            Label {
                text: "Analisis"
                font.pixelSize: 18
                font.weight: Font.Medium
                Layout.fillWidth: true
            }

            TextField {
                placeholderText: "Search models..."
                Layout.preferredWidth: 220
            }

            Button {
                text: "New Model"
            }
        }
    }

    // ====== MAIN SPLIT VIEW ======
    SplitView {
        id: splitView
        anchors.top: topBar.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        orientation: Qt.Horizontal


        // ====== LEFT SIDEBAR ======
        Rectangle {
            implicitWidth: 70
            SplitView.minimumWidth: 60
            SplitView.maximumWidth: 180
            color: "#f8fafc"
            border.color: "#e5e7eb"

            ListView {
                id: listView
                anchors.fill: parent
                anchors.margins: 5
                clip:true
                model: AnalysisNaveModel{}
                delegate: AnalysisNavDelegate{}

            }
        }

        // ====== CENTER WORKSPACE ======
        Rectangle {
            SplitView.fillWidth: true
            color: "#f5f7fb"

            StackLayout {
                anchors.fill: parent
                currentIndex: listView.currentIndex
                DataExplorerPage{}
                AnalysisPage{}
                Reports{}
            }

        }

    }
}
