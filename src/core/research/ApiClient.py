# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot


class ApiClient(QObject):
    # =======================================================
    # Signals
    # =======================================================
    requestFinished = Signal(str, dict)
    requestFailed = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Placeholder for network manager (e.g., QNetworkAccessManager)
        self._networkManager = None

    # =======================================================
    # Slots / Public API
    # =======================================================
    @Slot(str)
    def get(self, endpoint):
        """
        Perform a GET request to the given endpoint.
        Emit requestFinished or requestFailed.
        """
        # TODO: implement GET logic
        pass

    @Slot(str, dict)
    def post(self, endpoint, payload):
        """
        Perform a POST request to the given endpoint with payload.
        Emit requestFinished or requestFailed.
        """
        # TODO: implement POST logic
        pass

    @Slot(str, dict)
    def put(self, endpoint, payload):
        """
        Optional: perform a PUT request.
        """
        # TODO
        pass

    @Slot(str)
    def delete(self, endpoint):
        """
        Optional: perform a DELETE request.
        """
        # TODO
        pass

    # =======================================================
    # Internal Helpers
    # =======================================================
    def _handleResponse(self, endpoint, responseData):
        """
        Call this internally when a response arrives.
        """
        self.requestFinished.emit(endpoint, responseData)

    def _handleError(self, endpoint, errorMessage):
        """
        Call this internally on network error.
        """
        self.requestFailed.emit(endpoint, errorMessage)
