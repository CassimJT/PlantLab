import QtQuick 2.15
import QtQuick.Controls 2.15

ListModel {
    ListElement { key: "dashboard";  label: "Dashboard";  iconSource: "qrc:/assets/sidebar_icon/dashboard.svg" }
    ListElement { key: "data";       label: "Data";       iconSource: "qrc:/assets/sidebar_icon/data.svg" }
    ListElement { key: "models";     label: "Models";     iconSource: "qrc:/assets/sidebar_icon/model.svg" }
    ListElement { key: "analysis";   label: "Analysis";   iconSource: "qrc:/assets/sidebar_icon/analysis.svg" }
    ListElement { key: "devices";    label: "Devices";    iconSource: "qrc:/assets/sidebar_icon/devices.svg" }
    // ListElement { key: "deployment"; label: "Deployment"; iconSource: "qrc:/assets/sidebar_icon/deployment.svg" }
    // ListElement { key: "labeling";   label: "Labeling";   iconSource: "qrc:/assets/sidebar_icon/label.svg" }
    //ListElement { key: "settings";   label: "Settings";   iconSource: "qrc:/assets/sidebar_icon/settings.svg" }
}
