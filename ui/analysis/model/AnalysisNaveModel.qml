import QtQuick 2.15
import QtQuick.Controls

ListModel {
    id: action_model

    ListElement { title: "Data Explorer"; iconSource: "qrc:/assets/analysis/explore.svg" }
    ListElement { title: "Statistical Analysis"; iconSource: "qrc:/assets/analysis/analysis.svg" }
    ListElement { title: "Reports"; iconSource: "qrc:/assets/analysis/report.svg" }

}
