# This Python file uses the following encoding: utf-8
import os
from pathlib import Path  # Add this import
from typing import Optional
from PySide6 import QtCore
from PySide6.QtCore import (
    QObject,
    Slot,
    Signal,
    Property,
    QThreadPool
)
from src.core.model_engineering.ModelTrainerWorker import ModelTrainerTask


class ModelTrainer(QtCore.QObject):
    # ====================================================
    # Signals
    # ====================================================
    trainingProgressChanged = Signal(int)
    trainingStarted = Signal()
    trainingCompleted = Signal(str)
    dataSetPathChanged = Signal(str)
    epochChanged = Signal(float)
    batchSizeChanged = Signal(float)
    learningRateChanged = Signal(float)
    trainTestSplitChanged = Signal(int)
    isTrainingInProgressChanged = Signal(bool)
    trainingPaused = Signal()
    trainingResumed = Signal()
    lossUpdated = Signal(float)
    accuracyUpdated = Signal(float)
    statusMessageChanged = Signal(str)
    # Add missing signals
    outputLocationChanged = Signal(str)  # ← ADDED

    def __init__(self, parent=None):
        super().__init__(parent)
        self._training_progress = 0
        self._is_training_in_progress = False
        self._dataset_path = ""
        self._epoch = 15.0
        self._batch_size = 8.0
        self._learning_rate = 0.0001
        self._train_test_split = 80  # 80% train, 20% test
        self._status_message = ""
        self._current_loss = 0.0
        self._current_accuracy = 0.0
        self._output_location = ""  # ← ADDED
        self._thread_pool = QThreadPool.globalInstance()  # ← FIXED: Use globalInstance
        self._current_task = None
        self._current_model_type = ""

        # Set default output location (like other classes)
        home = str(Path.home())
        self._output_location = os.path.join(home, "Documents", "plantlab", "models")
        os.makedirs(self._output_location, exist_ok=True)

    # ====================================================
    # Property Getters
    # ====================================================
    @Property(str, notify=dataSetPathChanged)
    def datasetPath(self):
        return self._dataset_path

    @Property(float, notify=epochChanged)
    def epoch(self):
        return self._epoch

    @Property(float, notify=batchSizeChanged)
    def batchSize(self):
        return self._batch_size

    @Property(float, notify=learningRateChanged)
    def learningRate(self):
        return self._learning_rate

    @Property(int, notify=trainTestSplitChanged)
    def trainTestSplit(self):
        return self._train_test_split

    @Property(int, notify=trainingProgressChanged)
    def trainingProgress(self):
        return self._training_progress

    @Property(bool, notify=isTrainingInProgressChanged)
    def isTrainingInProgress(self):
        return self._is_training_in_progress

    @Property(str, notify=statusMessageChanged)
    def statusMessage(self):
        return self._status_message

    @Property(float, notify=lossUpdated)
    def currentLoss(self):
        return self._current_loss

    @Property(float, notify=accuracyUpdated)
    def currentAccuracy(self):
        return self._current_accuracy

    @Property(str, notify=outputLocationChanged)  # ← ADDED
    def outputLocation(self):
        return self._output_location

    # ====================================================
    # Property Setters (Internal)
    # ====================================================
    def _setTrainingProgress(self, value: int):
        if self._training_progress != value:
            self._training_progress = value
            self.trainingProgressChanged.emit(value)

    def _setIsTrainingInProgress(self, value: bool):
        if self._is_training_in_progress != value:
            self._is_training_in_progress = value
            self.isTrainingInProgressChanged.emit(value)

    def _setStatusMessage(self, message: str):
        if self._status_message != message:
            self._status_message = message
            self.statusMessageChanged.emit(message)

    def _setCurrentLoss(self, loss: float):
        if self._current_loss != loss:
            self._current_loss = loss
            self.lossUpdated.emit(loss)

    def _setCurrentAccuracy(self, accuracy: float):
        if self._current_accuracy != accuracy:
            self._current_accuracy = accuracy
            self.accuracyUpdated.emit(accuracy)

    def _setOutputLocation(self, location: str):  # ← ADDED
        if self._output_location != location:
            self._output_location = location
            self.outputLocationChanged.emit(location)

    # ====================================================
    # Public Slots - Property Setters
    # ====================================================
    @Slot(str)
    def setDatasetPath(self, datasetPath: str):
        if self._dataset_path != datasetPath:
            self._dataset_path = datasetPath
            self.dataSetPathChanged.emit(datasetPath)
            self._setStatusMessage(f"Dataset path set to: {datasetPath}")

    @Slot(float)
    def setEpoch(self, epoch: float):
        if self._epoch != epoch:
            self._epoch = epoch
            self.epochChanged.emit(epoch)
            self._setStatusMessage(f"Epochs set to: {epoch}")

    @Slot(float)
    def setBatchSize(self, batchSize: float):
        if self._batch_size != batchSize:
            self._batch_size = batchSize
            self.batchSizeChanged.emit(batchSize)
            self._setStatusMessage(f"Batch size set to: {batchSize}")

    @Slot(float)
    def setLearningRate(self, learningRate: float):
        if self._learning_rate != learningRate:
            self._learning_rate = learningRate
            self.learningRateChanged.emit(learningRate)
            self._setStatusMessage(f"Learning rate set to: {learningRate}")

    @Slot(int)
    def setTrainTestSplit(self, value: int):
        if self._train_test_split != value:
            self._train_test_split = value
            self.trainTestSplitChanged.emit(value)
            split_percent = value
            self._setStatusMessage(f"Train/test split set to: {split_percent}% train")

    @Slot(str)  # ← ADDED
    def setOutputLocation(self, location: str):
        """Set the output directory for trained models"""
        if location.startswith("file://"):
            location = location[7:]

        # Create directory if it doesn't exist
        os.makedirs(location, exist_ok=True)
        self._setOutputLocation(location)
        self._setStatusMessage(f"Output location set to: {location}")

    # ====================================================
    # Public Slots - Business Logic
    # ====================================================
    @Slot(str)
    def startTraining(self, modelType: str):
        """Start transfer learning with the specified model type."""
        if self._is_training_in_progress:
            self._setStatusMessage("Training already in progress")
            return

        if not self._dataset_path:
            self._setStatusMessage("No dataset path selected")
            self.trainingCompleted.emit("failed: no dataset")
            return

        if not os.path.exists(self._dataset_path):
            self._setStatusMessage(f"Dataset path does not exist: {self._dataset_path}")
            self.trainingCompleted.emit("failed: invalid dataset path")
            return

        # Clean up any existing worker
        if self._current_task is not None:
            try:
                self._current_task.cancel()
                self._current_task = None
            except:
                pass

        self._current_model_type = modelType
        self._setIsTrainingInProgress(True)
        self._setTrainingProgress(0)
        self._setCurrentLoss(0.0)
        self._setCurrentAccuracy(0.0)
        self.trainingStarted.emit()

        # Parse model type to get the actual model name
        model_name = self._parse_model_type(modelType)
        self._setStatusMessage(f"Starting training with {model_name}")

        # Create and configure the training task
        split_ratio = self._train_test_split / 100.0
        self._current_task = ModelTrainerTask(
            dataset_path=self._dataset_path,
            model_type=model_name,
            epochs=int(self._epoch),
            batch_size=int(self._batch_size),
            learning_rate=self._learning_rate,
            train_test_split=split_ratio
        )

        # Connect signals
        self._current_task.signals.progress.connect(self._on_training_progress)
        self._current_task.signals.finished.connect(self._on_training_finished)
        self._current_task.signals.error.connect(self._on_training_error)
        self._current_task.signals.status.connect(self._setStatusMessage)
        self._current_task.signals.file_progress.connect(self._on_file_progress)
        self._current_task.signals.conversion_step.connect(self._on_conversion_step)
        self._current_task.signals.loss_updated.connect(self._on_loss_updated)
        self._current_task.signals.accuracy_updated.connect(self._on_accuracy_updated)
        self._current_task.signals.canceled.connect(self._on_training_canceled)

        # Start the task
        self._thread_pool.start(self._current_task)

    @Slot()
    def pauseTraining(self):
        """Pause training"""
        if self._current_task and self._is_training_in_progress:
            self._current_task.pause()
            self.trainingPaused.emit()
            self._setStatusMessage("Training paused")

    @Slot()
    def resumeTraining(self):
        """Resume Training"""
        if self._current_task and self._is_training_in_progress:
            self._current_task.resume()
            self.trainingResumed.emit()
            self._setStatusMessage("Training resumed")

    @Slot()
    def stopTraining(self):
        """Stop/cancel training"""
        if self._current_task and self._is_training_in_progress:
            self._current_task.cancel()
            self._setStatusMessage("Training stopped by user")

    # ====================================================
    # Private Slots for Task Signals
    # ====================================================
    @Slot(int)
    def _on_training_progress(self, progress: int):
        self._setTrainingProgress(progress)

    @Slot(str)
    def _on_training_finished(self, result: str):
        self._setIsTrainingInProgress(False)
        # Disconnect signals before clearing
        if self._current_task:
            try:
                self._current_task.signals.progress.disconnect()
                self._current_task.signals.finished.disconnect()
                self._current_task.signals.error.disconnect()
                self._current_task.signals.status.disconnect()
                self._current_task.signals.loss_updated.disconnect()
                self._current_task.signals.accuracy_updated.disconnect()
            except:
                pass
            self._current_task = None
        self.trainingCompleted.emit(result)
        if "success" in result.lower():
            self._setStatusMessage("Training completed successfully!")
        else:
            self._setStatusMessage("Training failed")

    @Slot(str)
    def _on_training_error(self, error_msg: str):
        self._setStatusMessage(f"Error: {error_msg}")
        self._setIsTrainingInProgress(False)
        # Clean up
        if self._current_task:
            self._current_task = None

    @Slot(bool)
    def _on_training_canceled(self, canceled: bool):
        if canceled:
            self._setIsTrainingInProgress(False)
            self._current_task = None
            self._setStatusMessage("Training canceled")

    @Slot(str, int, int)
    def _on_file_progress(self, filename: str, current: int, total: int):
        if current == total:
            self._setStatusMessage(f"Completed: {filename}")

    @Slot(str)
    def _on_conversion_step(self, step: str):
        self._setStatusMessage(f"Step: {step}")

    @Slot(float)
    def _on_loss_updated(self, loss: float):
        self._setCurrentLoss(loss)

    @Slot(float)
    def _on_accuracy_updated(self, accuracy: float):
        self._setCurrentAccuracy(accuracy)

    # ====================================================
    # Helper Methods
    # ====================================================
    def _parse_model_type(self, model_type_str: str) -> str:
        """Parse the model type from the combobox string"""
        if "MobileNetV3-Small" in model_type_str:
            return "mobilenetv3_small"
        elif "MobileNetV3-Large" in model_type_str:
            return "mobilenetv3_large"
        elif "SSDLite-MobileNetV3" in model_type_str:
            return "ssdlite_mobilenetv3"
        else:
            return "mobilenetv3_small"
