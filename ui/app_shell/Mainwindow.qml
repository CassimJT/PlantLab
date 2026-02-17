import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts
import "../analysis"
import "../curation"
import "../dashboard"
import "../data"
import "../deployment"
import "../devices"
import "../settings"
import "../models"

Page {
    id: main_wondow
    background: Rectangle {
      color: "#f5f7fb"

    }
    //sideBar
    Sidebar{
        id: sideBar

    }
    //topBar
    Topbar {
        id: topbar
        height: 45
        anchors {
            left: sideBar.right
            right: parent.right
            top: parent.top
        }
    }

    //Layout
    StackLayout {
        id: pageStack
        currentIndex: 0
        anchors {
            top: topbar.bottom
            left: sideBar.right
            right: parent.right
            bottom: parent.bottom
            margins: 0
        }
        DashboardPage {}
        DataExplorerPage {}
        ModelsPage {}
        AnalysisPage {}
        DevicesPage {}
        Settings{}

    }
    //Statusbar
    footer: Statusbar {
        id: statusbar
    }
    

}
