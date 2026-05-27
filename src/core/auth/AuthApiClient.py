# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import json


class AuthApiClient(QObject):

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
        self._network_manager = QNetworkAccessManager(self)

        # Connect network manager
        self._network_manager.finished.connect(self._on_network_reply)

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
    # Public HTTP Interface
    # ======================================================

    def get(self, endpoint: str):
        """
        Perform GET request.
        """
        if not self._base_url:
            self.requestFailed.emit(endpoint, "Base URL not set")
            return

        self.requestStarted.emit(endpoint)
        url = self._build_url(endpoint)
        request = QNetworkRequest(url)
        self._setup_request_headers(request)
        self._network_manager.get(request)

    def post(self, endpoint: str, payload: dict):
        """
        Perform POST request.
        """
        if not self._base_url:
            self.requestFailed.emit(endpoint, "Base URL not set")
            return

        self.requestStarted.emit(endpoint)
        url = self._build_url(endpoint)
        request = QNetworkRequest(url)
        self._setup_request_headers(request)

        json_data = json.dumps(payload).encode('utf-8')
        self._network_manager.post(request, json_data)

    def put(self, endpoint: str, payload: dict):
        """
        Perform PUT request.
        """
        if not self._base_url:
            self.requestFailed.emit(endpoint, "Base URL not set")
            return

        self.requestStarted.emit(endpoint)
        url = self._build_url(endpoint)
        request = QNetworkRequest(url)
        self._setup_request_headers(request)

        json_data = json.dumps(payload).encode('utf-8')
        self._network_manager.put(request, json_data)

    def delete(self, endpoint: str):
        """
        Perform DELETE request.
        """
        if not self._base_url:
            self.requestFailed.emit(endpoint, "Base URL not set")
            return

        self.requestStarted.emit(endpoint)
        url = self._build_url(endpoint)
        request = QNetworkRequest(url)
        self._setup_request_headers(request)
        self._network_manager.deleteResource(request)

    # ======================================================
    # Internal Helpers
    # ======================================================

    def _build_url(self, endpoint: str) -> str:
        """
        Combine base URL and endpoint.
        """
        base = self._base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        return f"{base}/{endpoint}"

    def _build_headers(self) -> dict:
        """
        Construct headers.
        Include Authorization if token exists.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _setup_request_headers(self, request: QNetworkRequest):
        """
        Set up headers for QNetworkRequest.
        """
        headers = self._build_headers()
        for key, value in headers.items():
            request.setRawHeader(key.encode(), value.encode())

    def _on_network_reply(self, reply: QNetworkReply):
        """
        Handle network reply.
        """
        endpoint = reply.url().toString()
        error = reply.error()

        if error != QNetworkReply.NoError:
            self.requestFailed.emit(endpoint, reply.errorString())
            reply.deleteLater()
            return

        response_data = reply.readAll().data().decode('utf-8')
        try:
            json_data = json.loads(response_data)
            self.requestFinished.emit(endpoint, json_data)
        except json.JSONDecodeError as e:
            self.requestFailed.emit(endpoint, f"JSON Parse Error: {str(e)}")

        reply.deleteLater()