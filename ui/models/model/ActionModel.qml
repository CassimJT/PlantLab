import QtQuick 2.15
import QtQuick.Controls

ListModel {
    id: action_model

    ListElement { title: "Library"; iconSource: "qrc:/assets/model/shelf.svg" }
    ListElement { title: "Download"; iconSource: "qrc:/assets/model/updates.svg" }
    ListElement { title: "Transform"; iconSource: "qrc:/assets/model/transform.svg" }
    ListElement { title: "Train "; iconSource: "qrc:/assets/topBar/infarence.svg" }
    //ListElement { title: "Export / Deploy"; icon: "" }
}
