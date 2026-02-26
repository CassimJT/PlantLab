# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal


class ApiClient(QObject):

    # ======================================================
    # Signals
    # ======================================================
    requestStarted = Signal(str)
    requestFinished = Signal(str, dict)
    requestFailed = Signal(str, str)

    # ======================================================
    # Init
    # ======================================================
    def __init__(self, parent=None):
        super().__init__(parent)

        self._base_url = ""
        self._token = None
        self._timeout = 30  # seconds

    # ======================================================
    # Properties (Pythonic — internal use only)
    # ======================================================

    @property
    def baseUrl(self):
        return self._base_url

    @baseUrl.setter
    def baseUrl(self, value: str):
        self._base_url = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value: str):
        self._token = value

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value: int):
        self._timeout = value

    # ======================================================
    # Public HTTP Interface (Business Logic Skeleton)
    # ======================================================

    def get(self, endpoint: str):
        """
        Perform GET request.
        - Build headers
        - Attach Authorization if token exists
        - Emit lifecycle signals
        """
        pass

    def post(self, endpoint: str, payload: dict):
        """
        Perform POST request.
        """
        pass

    def put(self, endpoint: str, payload: dict):
        """
        Perform PUT request.
        """
        pass

    def delete(self, endpoint: str):
        """
        Perform DELETE request.
        """
        pass

    # ======================================================
    # Internal Helpers
    # ======================================================

    def _build_url(self, endpoint: str) -> str:
        """
        Combine base URL and endpoint.
        """
        pass

    def _build_headers(self) -> dict:
        """
        Construct headers.
        Include Authorization if token exists.
        """
        pass
