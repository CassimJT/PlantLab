// File Utilities
.pragma library

var QtQuick = require("QtQuick");

function FileUtils() {
    this.ensureDirectory = function(dirPath) {
        var dir = Qt.createQmlObject('import QtQuick 2.15; QtObject {}', null, "");
        // Note: In real implementation, you'd need to use C++ backend for file operations
        console.log("Ensuring directory:", dirPath);
    };

    this.saveJson = function(filePath, data) {
        try {
            var jsonString = JSON.stringify(data, null, 2);
            this.saveText(filePath, jsonString);
            return true;
        } catch (e) {
            console.error("Save JSON error:", e);
            return false;
        }
    };

    this.loadJson = function(filePath) {
        try {
            // This would need actual file reading implementation
            // For now, return empty object
            return {};
        } catch (e) {
            console.error("Load JSON error:", e);
            return null;
        }
    };

    this.saveText = function(filePath, content) {
        console.log("Saving file:", filePath);
        // Implementation would use C++ backend
        return true;
    };

    this.loadText = function(filePath) {
        console.log("Loading file:", filePath);
        // Implementation would use C++ backend
        return "";
    };

    this.deleteFile = function(filePath) {
        console.log("Deleting file:", filePath);
        // Implementation would use C++ backend
        return true;
    };

    this.fileExists = function(filePath) {
        // Implementation would use C++ backend
        return false;
    };
}

// Singleton instance
var fileUtils = new FileUtils();