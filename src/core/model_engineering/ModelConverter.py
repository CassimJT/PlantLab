# This Python file uses the following encoding: utf-8
from PySide6 import QtCore
from PySide6.QtCore import (
    QObject,
    Slot,
    Signal,
    Property
)


class ModelConverter(QtCore.QObject):
    # =============================================
    # Signal
    # =============================================
    conversionProgressChanged = Signal(int)
    conversionCompleted = Signal(str)
    conversionStarted = Signal()
    conversionStatusChanged = Signal(str)
    modelNameChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_conversion_in_progress = False
        self._conversion_progress = 0
        self._conversion_status = ""
        self._modleName = ""

    # =============================================
    # Property
    # =============================================
    @Property(int, notify=conversionProgressChanged)
    def conversionProgress(self):
        return self._conversion_progress

    @Property(int, notify=conversionStatusChanged)
    def conversionStatus(self):
        return self._conversion_status

    @Property(str, notify=modelNameChanged)
    def modelName(self):
        return self._modleName

    # =============================================
    # Internal States
    # =============================================
    def _setConversionStatus(self, status: str):
        if self._conversion_status != status:
            self._conversion_status = status
            self.conversionProgressChanged.emit()

    def _setConversionProgress(self, value: int):
        if self._conversion_progress != value:
            self._conversion_progress = value
            self.conversionProgressChanged.emit(value)

    # =============================================
    # Slots
    # =============================================
    @Slot()
    def setModlename(self, name: str):
        if self._modleName != name:
            """Transifrom the path to to standard path when nessessary"""
            self._modleName = name
            self.modelName.emit()

    @Slot(str, str)
    def transform(self, modelPath: str, frameWork: str):
        # tranform the model using tourchscript to another format
        pass

    @Slot()
    def cancelTransiformation():
        # cancel ongoing transiformation
        pass
