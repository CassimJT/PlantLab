# This Python file uses the following encoding: utf-8
from PySide6 import QtCore
from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
    Property,
)
import FileSystemController


class DatasetProcessor(QtCore.QObject):
    # =======================
    # SIGNALS
    # =======================

    # --Processing feedback signals--
    normalizationStarted = Signal(str)
    normalizationProgress = Signal(int)
    normalizationCompleted = Signal(str)
    normalizationFailed = Signal(str)

    # --Export feedback signals for different formats--
    exportStarted = Signal(str, str)
    exportProgress = Signal(int)
    exportCompleted = Signal(str)
    exportFailed = Signal(str)
    csvWithPathsGenerated = Signal(str)
    csvWithMetadataGenerated = Signal(str)
    jsonGenerated = Signal(str)

    # --Property notify signals --
    isProcessingChanged = Signal()
    progressValueChanged = Signal()
    totalImagesToProcessChanged = Signal()

    def __init__(self, fileSystemController=None, parent=None):
        super.__init__(parent)
        self._is_processing = False
        self._progress_value = 0
        self._total_image = 0

    # --Property--
    @Property(bool, notify=isProcessingChanged)
    def isProcessing(self):
        return self._is_processing

    @Property(int, notify=progressValueChanged)
    def progressValue(self):
        return self._progress_value

    @Property(int, notify=totalImagesToProcessChanged)
    def totalImagesToProcess(self):
        return self._total_image

    # =========================================================
    # INTERNAL STATE HELPERS
    # =========================================================

    def _set_isProcessing(self, value: bool):
        if self._is_processing != value:
            self._is_processing = value
            self.totalImagesToProcessChanged.emit()

    def _set_progressValue(self, value: int):
        if self._progress_value != value:
            self._progress_value = value
            self.progressValueChanged.emit()

    def _set_totalImageToPreocess(self, value: int):
        if self._total_image != value:
            self._total_image = value
            self.totalImagesToProcessChanged.emit()

    # ========================================================
    # Slotes
    # ========================================================
    @Slot(int, bool, str, str)
    def applyNormalization(self, targetSize: int, grayscale: bool, normalization: str, dirPath: str):
        pass

    @Slot(str, str)
    def exportDataset(self, formate: str, destination: str):
        pass

    @Slot()
    def cancelProcessing():
        pass

    @Slot(result=str)
    def getDefaultExportPath():
        pass
