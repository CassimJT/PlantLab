# This Python file uses the following encoding: utf-8
from PySide6 import QtCore
from PySide6.QtCore import (
    QObject,
    Slot,
    Signal,
    Property,
    QThreadPool
)
from src.core.model_engineering.DownloadWorker import DownloadTask


class ModelDownloader(QtCore.QObject):

    # ==============================================
    # Signals
    # ==============================================
    progressUpdated = Signal(str, int)  # Renamed from downloadProgress to avoid conflict
    downloadStarted = Signal()
    downloadFinished = Signal(str)  # path
    downloadErrorOccurred = Signal(str)
    downloadProgressChanged = Signal(int)
    isDownloadingChanged = Signal()
    downloadLocationChanged = Signal(str)
    modelVersionChanged = Signal(str)
    statusMessageChanged = Signal(str)
    fileDownloadProgress = Signal(str, int, int)  # filename, current, total

    def __init__(self, parent=None):
        super().__init__(parent)
        self._isDownloading = False
        self._downloadProgress = 0
        self._downloadLocation = ""
        self._modelVersion = "Latest"
        self._statusMessage = "Ready"
        self._currentWorker = None
        self._threadpool = QThreadPool.globalInstance()

    # ===============================================
    # Properties
    # ===============================================
    @Property(int, notify=downloadProgressChanged)
    def downloadProgress(self):
        return self._downloadProgress

    @Property(bool, notify=isDownloadingChanged)
    def isDownloading(self):
        return self._isDownloading

    @Property(str, notify=downloadLocationChanged)
    def downloadLocation(self):
        return self._downloadLocation

    @Property(str, notify=modelVersionChanged)
    def modelVersion(self):
        return self._modelVersion

    @Property(str, notify=statusMessageChanged)
    def statusMessage(self):
        return self._statusMessage

    # =========================================================
    # INTERNAL STATE HELPERS
    # =========================================================
    def _setDownloadProgress(self, value: int):
        if self._downloadProgress != value:
            self._downloadProgress = value
            self.downloadProgressChanged.emit(value)

    def _setIsDownloading(self, value: bool):
        if self._isDownloading != value:
            self._isDownloading = value
            self.isDownloadingChanged.emit()

    def _setStatusMessage(self, value: str):
        if self._statusMessage != value:
            self._statusMessage = value
            self.statusMessageChanged.emit(value)

    # ─── Worker signal handlers ──────────────────────────
    def _on_download_progress(self, value: int):
        self._setDownloadProgress(value)
        self.progressUpdated.emit("Overall", value)  # Use renamed signal

    def _on_file_progress(self, filename: str, current: int, total: int):
        self.fileDownloadProgress.emit(filename, current, total)
        self._setStatusMessage(f"Downloading {filename}...")

    def _on_download_finished(self, path: str):
        self._setIsDownloading(False)
        self._setDownloadProgress(100)
        self._setStatusMessage("Download completed successfully!")
        self.downloadFinished.emit(path)
        self._currentWorker = None

    def _on_download_canceled(self):
        self._setIsDownloading(False)
        self._setDownloadProgress(0)
        self._setStatusMessage("Download canceled")
        self._currentWorker = None

    def _on_download_error(self, error_msg: str):
        self._setIsDownloading(False)
        self._setDownloadProgress(0)
        self._setStatusMessage(f"Error: {error_msg}")
        self.downloadErrorOccurred.emit(error_msg)
        self._currentWorker = None

    def _on_status_update(self, status: str):
        self._setStatusMessage(status)

    # =========================================================
    # Slots
    # =========================================================
    @Slot(str)
    def setDownloadLocation(self, location: str):
        if self._downloadLocation != location:
            if location.startswith("file://"):
                location = location.replace("file://", "", 1)
            self._downloadLocation = location
            self.downloadLocationChanged.emit(location)

    @Slot(str)
    def setModelVersion(self, modelVersion: str):
        if self._modelVersion != modelVersion:
            self._modelVersion = modelVersion
            self.modelVersionChanged.emit(modelVersion)

    @Slot(str, list, str, str)
    def downloadModel(self, modelId: str, frameworks: list, branch: str = "Latest", commitHash: str = ""):
        if not modelId or not modelId.strip():
            self.downloadErrorOccurred.emit("Model ID cannot be empty")
            return

        if self._isDownloading:
            self.downloadErrorOccurred.emit("A download is already in progress")
            return

        worker = DownloadTask(
            huggingface_id=modelId.strip(),
            frameworks=frameworks,
            branch=branch,
            download_path=self._downloadLocation,
            commit_hash=commitHash
        )

        # Connect worker signals
        worker.signals.progress.connect(self._on_download_progress)
        worker.signals.file_progress.connect(self._on_file_progress)
        worker.signals.finished.connect(self._on_download_finished)
        worker.signals.canceled.connect(self._on_download_canceled)
        worker.signals.error.connect(self._on_download_error)
        worker.signals.status.connect(self._on_status_update)

        self._currentWorker = worker
        self._setIsDownloading(True)
        self._setDownloadProgress(0)
        self._setStatusMessage(f"Starting download of {modelId}...")
        self.downloadStarted.emit()

        self._threadpool.start(worker)

    @Slot()
    def cancelDownload(self):
        if self._currentWorker and self._isDownloading:
            self._currentWorker.cancel()
