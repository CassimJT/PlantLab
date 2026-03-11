import QtQuick 2.15
import QtQml.Models 2.15

Item {
    id: root

    property var selectedModel: null
    property int count: ModelList ? ModelList.rowCount() : 0

    function get(index) {
        if (ModelList && typeof ModelList.get === 'function') {
            return ModelList.get(index)
        }
        console.error("ModelList not available or doesn't have get method")
        return {}
    }

    function selectModel(index) {
        if (index >= 0 && index < count) {
            selectedModel = get(index)
        }
    }

    Component.onCompleted: {
        console.log("AvailableModel initialized, count:", count)
        if (count > 0) {
            selectModel(0)  // Select first model by default
        }
    }
}
