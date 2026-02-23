# This Python file uses the following encoding: utf-8
from PySide6 import QtCore
from PySide6.QtCore import (
    QObject,
    Slot,
    Signal,
    Property
)


class ModelDownloader(QtCore.QObject):

    # ==============================================
    # Signals
    # ==============================================
    downloadProgress = Signal(str, int)
    downloadCompleted = Signal()
    downlaodStateted = Signal()
    downloadFinished = Signal()
    downloadErrorOccured = Signal(str)
    downloadPregressChanged = Signal(int)
    isdownoadingChanged = Signal()
    downlaodLocationChanged = Signal(str)
    modelVersionChanged = Signal()

    def __init__(self,  parent=None):
        super().__init__(parent)
        self._isdownloading = False
        self._download_progress = 0
        self._downloadLocation = ""
        self._modelVersion = "Latest"

    # ===============================================
    # Property
    # ===============================================
    @Property(bool, notify=downloadPregressChanged)
    def downloadPregress(self):
        return self._download_progress

    @Property(bool, notify=isdownoadingChanged)
    def isdownoadingChanged(self):
        return self._isdownloading

    def downlaodLocation(self):
        return self._downloadLocation

    def modeVersion(self):
        return self._modelVersion

    # =========================================================
    # INTERNAL STATE HELPERS
    # =========================================================
    def _setDowloadProgress(self, value: int):
        if self._download_progress != value:
            self._download_progress = value
            self.downloadPregressChanged.emit()

    def _setIsDownloading(self, value: bool):
        if self._isdownloading != value:
            self._isdownloading = value
            self.isdownoadingChanged.emit()

    # =========================================================
    # Slotes
    # =========================================================
    @Slot()
    def setDowloadLocaion(self, location: str):
        if self._downloadLocation != location:
            self._downloadLocation = location
            self.downlaodLocationChanged.emit(location)

    @Slot()
    def setModelVersion(self, modelVersion: str):
        if self._modelVersion != modelVersion:
            self._modelVersion = modelVersion
            self.modelVersionChanged.emit()

    @Slot(str, str)
    def downloadModel(self, modelId: str, framwork: str):
        # Dowload a model from huginface for the specified framwork
        pass
