from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, Signal, Slot
from PySide6.QtQml import QmlElement
import json

# Define the QML module
QML_IMPORT_NAME = "plantlab.models"
QML_IMPORT_MAJOR_VERSION = 1

@QmlElement
class ModelListModel(QAbstractListModel):
    """QAbstractListModel implementation for QML ListView compatibility"""

    # Define roles
    NameRole = Qt.UserRole + 1
    FrameworkRole = Qt.UserRole + 2
    SizeRole = Qt.UserRole + 3
    AccuracyRole = Qt.UserRole + 4
    LearningRateRole = Qt.UserRole + 5
    EpochsRole = Qt.UserRole + 6
    StatusRole = Qt.UserRole + 7
    PathRole = Qt.UserRole + 8
    FormatRole = Qt.UserRole + 9
    LastModifiedRole = Qt.UserRole + 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self._models = []
        self._scanner = None

    def set_scanner(self, scanner):
        """Connect to the ModelScanner"""
        self._scanner = scanner
        self._scanner.modelsChanged.connect(self._on_models_changed)
        self._on_models_changed()

    def _on_models_changed(self):
        """Update when scanner models change"""
        self.beginResetModel()
        self._models = [self._scanner.get(i) for i in range(self._scanner.count())]
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._models)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._models):
            return None

        model = self._models[index.row()]

        if role == self.NameRole:
            return model.get('name', '')
        elif role == self.FrameworkRole:
            return model.get('framework', '')
        elif role == self.SizeRole:
            return model.get('size', '')
        elif role == self.AccuracyRole:
            return model.get('accuracy', 0.0)
        elif role == self.LearningRateRole:
            return model.get('learningRate', 0.0)
        elif role == self.EpochsRole:
            return model.get('epochs', 0)
        elif role == self.StatusRole:
            return model.get('status', '')
        elif role == self.PathRole:
            return model.get('path', '')
        elif role == self.FormatRole:
            return model.get('format', '')
        elif role == self.LastModifiedRole:
            return model.get('lastModified', '')

        return None

    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.FrameworkRole: b"framework",
            self.SizeRole: b"size",
            self.AccuracyRole: b"accuracy",
            self.LearningRateRole: b"learningRate",
            self.EpochsRole: b"epochs",
            self.StatusRole: b"status",
            self.PathRole: b"path",
            self.FormatRole: b"format",
            self.LastModifiedRole: b"lastModified"
        }

    @Slot(int, result='QVariant')
    def get(self, row):
        """Get model data at row"""
        if 0 <= row < len(self._models):
            return self._models[row]
        return {}
