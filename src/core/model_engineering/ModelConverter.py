# This Python file uses the following encoding: utf-8
from PySide6 import QtCore
from PySide6.QtCore import (
    QObject,
    Slot,
    Signal,
    Property,
    QThreadPool
)
from pathlib import Path
import os
from src.core.model_engineering.ModelConverterWorker import ModelConverterTask


class ModelConverter(QtCore.QObject):
    # =============================================
    # Signals
    # =============================================
    conversionProgressChanged = Signal(int)
    conversionCompleted = Signal(str)
    conversionStarted = Signal()
    conversionError = Signal(str)
    conversionStatusChanged = Signal(str)
    modelNameChanged = Signal(str)
    isConvertingChanged = Signal()
    outputLocationChanged = Signal(str)
    conversionStepChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._isConverting = False
        self._conversionProgress = 0
        self._conversionStatus = "Ready"
        self._modelName = ""
        self._outputLocation = ""
        self._currentWorker = None
        self._threadpool = QThreadPool.globalInstance()

        # Set default output location
        home = str(Path.home())
        self._outputLocation = os.path.join(home, "Documents", "plantlab", "models")
        os.makedirs(self._outputLocation, exist_ok=True)

    # =============================================
    # Properties
    # =============================================
    @Property(int, notify=conversionProgressChanged)
    def conversionProgress(self):
        return self._conversionProgress

    @Property(str, notify=conversionStatusChanged)
    def conversionStatus(self):
        return self._conversionStatus

    @Property(str, notify=modelNameChanged)
    def modelName(self):
        return self._modelName

    @Property(bool, notify=isConvertingChanged)
    def isConverting(self):
        return self._isConverting

    @Property(str, notify=outputLocationChanged)
    def outputLocation(self):
        return self._outputLocation

    # =============================================
    # Internal State Helpers
    # =============================================
    def _setConversionStatus(self, status: str):
        if self._conversionStatus != status:
            self._conversionStatus = status
            self.conversionStatusChanged.emit(status)

    def _setConversionProgress(self, value: int):
        if self._conversionProgress != value:
            self._conversionProgress = value
            self.conversionProgressChanged.emit(value)

    def _setIsConverting(self, value: bool):
        if self._isConverting != value:
            self._isConverting = value
            self.isConvertingChanged.emit()

    def _setModelName(self, name: str):
        if self._modelName != name:
            self._modelName = name
            self.modelNameChanged.emit(name)

    def _setOutputLocation(self, location: str):
        if self._outputLocation != location:
            self._outputLocation = location
            self.outputLocationChanged.emit(location)

    # =============================================
    # Worker Signal Handlers
    # =============================================
    def _on_conversion_progress(self, value: int):
        self._setConversionProgress(value)

    def _on_conversion_status(self, status: str):
        self._setConversionStatus(status)

    def _on_conversion_step(self, step: str):
        self.conversionStepChanged.emit(step)
        self._setConversionStatus(step)

    def _on_conversion_finished(self, output_path: str):
        self._setIsConverting(False)
        self._setConversionProgress(100)
        self._setConversionStatus(f"Conversion completed successfully!")
        self.conversionCompleted.emit(output_path)
        self._currentWorker = None

    def _on_conversion_canceled(self):
        self._setIsConverting(False)
        self._setConversionProgress(0)
        self._setConversionStatus("Conversion canceled")
        self._currentWorker = None

    def _on_conversion_error(self, error_msg: str):
        self._setIsConverting(False)
        self._setConversionProgress(0)
        self._setConversionStatus(f"Error: {error_msg}")
        self.conversionError.emit(error_msg)
        self._currentWorker = None

    def _on_file_progress(self, filename: str, current: int, total: int):
        # Optional: handle file progress if needed
        pass

    # =============================================
    # Slots
    # =============================================
    @Slot(str)
    def setModelName(self, name: str):
        """Set the model name (can be path or just name)"""
        # Clean up file:// prefix if present
        if name.startswith("file://"):
            name = name[7:]

        # If it's a full path, extract just the filename
        if '/' in name or '\\' in name:
            path = Path(name)
            name = path.stem  # Get filename without extension

        self._setModelName(name)

    @Slot(str)
    def setOutputLocation(self, location: str):
        """Set the output directory for converted models"""
        if location.startswith("file://"):
            location = location[7:]

        # Create directory if it doesn't exist
        os.makedirs(location, exist_ok=True)
        self._setOutputLocation(location)

    @Slot(str, str, str, str)
    def transform(self, modelPath: str, fromFramework: str, toFramework: str, outputPath: str = None):
        """Transform model from one framework to another"""

        if not modelPath:
            self.conversionError.emit("Model path cannot be empty")
            return

        if self._isConverting:
            self.conversionError.emit("A conversion is already in progress")
            return

        # Clean up file:// prefix if present
        if modelPath.startswith("file://"):
            modelPath = modelPath[7:]

        # Check if model file exists
        if not os.path.exists(modelPath):
            self.conversionError.emit(f"Model file not found: {modelPath}")
            return

        # Use provided output path or default
        save_path = outputPath if outputPath else self._outputLocation

        # Extract model name for display
        self.setModelName(modelPath)

        # Create worker
        worker = ModelConverterTask(
            model_path=modelPath,
            from_framework=fromFramework,
            to_framework=toFramework,
            save_path=save_path
        )

        # Connect worker signals
        worker.signals.progress.connect(self._on_conversion_progress)
        worker.signals.finished.connect(self._on_conversion_finished)
        worker.signals.canceled.connect(self._on_conversion_canceled)
        worker.signals.error.connect(self._on_conversion_error)
        worker.signals.status.connect(self._on_conversion_status)
        worker.signals.file_progress.connect(self._on_file_progress)
        worker.signals.conversion_step.connect(self._on_conversion_step)

        self._currentWorker = worker
        self._setIsConverting(True)
        self._setConversionProgress(0)
        self._setConversionStatus(f"Starting conversion to {toFramework}...")
        self.conversionStarted.emit()

        self._threadpool.start(worker)

    @Slot()
    def cancelTransformation(self):
        """Cancel ongoing transformation"""
        if self._currentWorker and self._isConverting:
            self._setConversionStatus("Canceling conversion...")
            self._currentWorker.cancel()
