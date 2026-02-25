# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot
from ApiClient import ApiClient

class DataService(QObject):
    # =======================================================
    # Signals
    # =======================================================
    fieldDataReceived = Signal(list)
    inferenceResultSubmitted = Signal(bool)
    errorOccurred = Signal(str)

    def __init__(self, apiClient=None, parent=None):
        super().__init__(parent)
        self._apiClient = ApiClient

        # Connect ApiClient signals if provided
        if self._apiClient:
            self._apiClient.requestFinished.connect(self._onRequestFinished)
            self._apiClient.requestFailed.connect(self._onRequestFailed)

    # =======================================================
    # Public API / Slots
    # =======================================================
    @Slot()
    def fetchFieldData(self):
        """
        Trigger fetching of all field data from backend.
        """
        if not self._apiClient:
            self.errorOccurred.emit("ApiClient not set")
            return

        # TODO: call self._apiClient.get("endpoint_for_field_data")
        pass

    @Slot(dict)
    def submitInferenceResult(self, inferenceData):
        """
        Submit inference result to backend.
        """
        if not self._apiClient:
            self.errorOccurred.emit("ApiClient not set")
            return

        # TODO: call self._apiClient.post("endpoint_for_submission", inferenceData)
        pass

    # =======================================================
    # Internal Handlers
    # =======================================================
    @Slot(str, dict)
    def _onRequestFinished(self, endpoint, data):
        """
        Handle raw data from ApiClient and convert to Python objects.
        """
        # TODO: parse JSON and extract list of field records
        # For example:
        # records = data.get("records", [])
        # self.fieldDataReceived.emit(records)
        pass

    @Slot(str, str)
    def _onRequestFailed(self, endpoint, errorMessage):
        """
        Handle errors from ApiClient.
        """
        self.errorOccurred.emit(f"{endpoint}: {errorMessage}")

    # =======================================================
    # Setter / Getter for ApiClient (optional)
    # =======================================================
    def setApiClient(self, apiClient):
        if self._apiClient is apiClient:
            return
        if self._apiClient:
            # Disconnect previous signals
            self._apiClient.requestFinished.disconnect(self._onRequestFinished)
            self._apiClient.requestFailed.disconnect(self._onRequestFailed)
        self._apiClient = apiClient
        if self._apiClient:
            self._apiClient.requestFinished.connect(self._onRequestFinished)
            self._apiClient.requestFailed.connect(self._onRequestFailed)
