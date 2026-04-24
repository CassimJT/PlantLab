# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot, Property
from .ApiClient import ApiClient


class DataService(QObject):
    # =======================================================
    # Signals
    # =======================================================
    fieldDataReceived = Signal(list)
    inferenceResultSubmitted = Signal(bool)
    errorOccurred = Signal(str)
    inferencesFetched = Signal(list)
    loadingChanged = Signal()

    def __init__(self, apiClient=None, parent=None):
        super().__init__(parent)
        self._apiClient = apiClient
        self._isLoading = False

        # Connect ApiClient signals if provided
        if self._apiClient:
            self._apiClient.requestFinished.connect(self._onRequestFinished)
            self._apiClient.requestFailed.connect(self._onRequestFailed)
            self._apiClient.loadingChanged.connect(self._onLoadingChanged)

    # =======================================================
    # Properties
    # =======================================================
    @Property(bool, notify=loadingChanged)
    def isLoading(self):
        return self._isLoading

    def setIsLoading(self, loading):
        if self._isLoading != loading:
            self._isLoading = loading
            self.loadingChanged.emit()

    # =======================================================
    # Public API / Slots
    # =======================================================
    @Slot()
    def fetchFieldData(self):
        """
        Trigger fetching of all inferences from backend.
        """
        if not self._apiClient:
            self.errorOccurred.emit("ApiClient not set")
            return
        self.setIsLoading(True)
        self._apiClient.fetchAllInferences()

    @Slot(dict)
    def submitInferenceResult(self, inferenceData):
        """
        Submit inference result to backend.
        """
        if not self._apiClient:
            self.errorOccurred.emit("ApiClient not set")
            return
        self.setIsLoading(True)
        self._apiClient.post("", inferenceData)

    @Slot(list)
    def submitBatchInferences(self, inferencesList):
        """
        Submit batch inference results to backend.
        """
        if not self._apiClient:
            self.errorOccurred.emit("ApiClient not set")
            return
        self.setIsLoading(True)
        self._apiClient.postBatch(inferencesList)

    # =======================================================
    # Internal Handlers
    # =======================================================
    @Slot(str, dict)
    def _onRequestFinished(self, endpoint, data):
        """
        Handle raw data from ApiClient and convert to Python objects.
        """
        self.setIsLoading(False)

        # Handle different endpoints
        if "inferences" in data:
            # List endpoint returns { inferences: [...] }
            records = data.get("inferences", [])
            self.inferencesFetched.emit(records)
            self.fieldDataReceived.emit(records)
        elif "inference" in data:
            # Single inference endpoint
            records = [data.get("inference", {})]
            self.inferencesFetched.emit(records)
        else:
            # Direct array response
            if isinstance(data, list):
                self.inferencesFetched.emit(data)
                self.fieldDataReceived.emit(data)

    @Slot(str, str)
    def _onRequestFailed(self, endpoint, errorMessage):
        """
        Handle errors from ApiClient.
        """
        self.setIsLoading(False)
        self.errorOccurred.emit(f"{endpoint}: {errorMessage}")

    @Slot(bool)
    def _onLoadingChanged(self):
        """Propagate loading state from ApiClient"""
        if self._apiClient:
            self.setIsLoading(self._apiClient.isLoading)

    # =======================================================
    # Setter / Getter for ApiClient
    # =======================================================
    def setApiClient(self, apiClient):
        if self._apiClient is apiClient:
            return
        if self._apiClient:
            self._apiClient.requestFinished.disconnect(self._onRequestFinished)
            self._apiClient.requestFailed.disconnect(self._onRequestFailed)
            self._apiClient.loadingChanged.disconnect(self._onLoadingChanged)
        self._apiClient = apiClient
        if self._apiClient:
            self._apiClient.requestFinished.connect(self._onRequestFinished)
            self._apiClient.requestFailed.connect(self._onRequestFailed)
            self._apiClient.loadingChanged.connect(self._onLoadingChanged)