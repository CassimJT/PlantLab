# This Python file uses the following encoding: utf-8
from PySide6 import QtCore
from PySide6.QtCore import (
    QObject,
    Slot,
    Signal,
    Property
)


class ModelTrainer(QtCore.QObject):

    # ====================================================
    # Signal
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

    def __init__(self, parent=None):
        super().__init__(parent)
        self._training_progress = 0
        self._is_training_in_progress = False
        self._dataset_path = ""
        self._epoch = 0.0
        self._batch_size = 0.0
        self._learning_rate = 0.0
        self._train_test_split = 0.0

    # ====================================================
    # Property
    # ====================================================
    @Property(str, notify=dataSetPathChanged)
    def dataSetPathChanged(self):
        return self._dataset_path

    @Property(float, notify=epochChanged)
    def epoch(self):
        return self._epoch

    @Property(float, notify=batchSizeChanged)
    def batchSize(self):
        return self._batch_size

    @Property(float, notify=learningRateChanged)
    def learningRateChanged(self):
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

    # ====================================================
    # Internale State
    # ====================================================
    def _setTrainingProgress(self, value: int):
        if self._training_progress != value:
            self._training_progress = value
            self.trainingProgressChanged.emit(value)

    def _setIsTrainingInProgress(self, value: bool):
        if self._is_training_in_progress != value:
            self._is_training_in_progress = value
            self.isTrainingInProgressChanged.emit(value)

    # ====================================================
    # Slots
    # ====================================================
    @Slot(str)
    # Getters
    def setDatasetPath(self, datasetPath: str):
        if self._dataset_path != datasetPath:
            self._dataset_path = datasetPath
            self.dataSetPathChanged.emit(datasetPath)

    @Slot(float)
    def setEpoch(self, epoch: float):
        if self._epoch != epoch:
            self._epoch = epoch
            self.epochChanged.emit()

    @Slot(float)
    def setBatchSize(self, batchSize: float):
        if self._batch_size != batchSize:
            self._batch_size = batchSize
            self.batchSizeChanged.emit(batchSize)

    @Slot(float)
    def setLearningRate(self, learnigRate: float):
        if self._learning_rate != learnigRate:
            self._learning_rate = learnigRate
            self.learningRateChanged.emit(learnigRate)

    @Slot(int)
    def setTrainTestSplit(self, value: int):
        if self._train_test_split != value:
            self._train_test_split = value
            self.trainTestSplitChanged.emit(value)

    #   business logic
    @Slot(str)
    def startTraining(self, modelType: str):
        """ start stransfer learning with the specified model type."""
        pass

    @Slot()
    def pauseTraining(self):
        """ Pause training """
        pass

    @Slot()
    def resumeTraining(self):
        """ Resume Training """
        pass
