# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import json

class ApiClient(QObject):
    # =======================================================
    # Signals
    # =======================================================
    requestFinished = Signal(str, dict)
    requestFailed = Signal(str, str)
    batchFinished = Signal(bool, int, int, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._networkManager = QNetworkAccessManager(self)
        self._baseUrl = "http://192.168.8.130:5000/api/inference"
        self._authToken = ""

        # Connect network manager
        self._networkManager.finished.connect(self._onNetworkReply)

    # =======================================================
    # Properties
    # =======================================================
    def setBaseUrl(self, url):
        self._baseUrl = url

    def setAuthToken(self, token):
        self._authToken = token

    # =======================================================
    # Slots / Public API
    # =======================================================
    @Slot(str)
    def get(self, endpoint):
        """
        Perform a GET request to the given endpoint.
        """
        url = QUrl(self._baseUrl + endpoint)
        request = QNetworkRequest(url)
        self._setupRequestHeaders(request)
        self._networkManager.get(request)

    @Slot(dict)
    def post(self, endpoint, payload):
        """
        Perform a POST request to the given endpoint with payload.
        """
        url = QUrl(self._baseUrl + endpoint)
        request = QNetworkRequest(url)
        self._setupRequestHeaders(request)

        json_data = json.dumps(payload).encode('utf-8')
        self._networkManager.post(request, json_data)

    @Slot(dict)
    def postBatch(self, inferences):
        """
        Send batch inferences to the server.
        """
        payload = {
            "inferences": inferences,
            "batchSize": len(inferences)
        }
        self.post("/batch", payload)

    @Slot()
    def fetchAllInferences(self):
        """
        Fetch all inferences from the server.
        """
        self.get("")

    @Slot(str)
    def getInferenceById(self, inference_id):
        """
        Fetch a single inference by ID.
        """
        self.get(f"/{inference_id}")

    # =======================================================
    # Internal Helpers
    # =======================================================
    def _setupRequestHeaders(self, request):
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        if self._authToken:
            request.setRawHeader(b"Authorization", f"Bearer {self._authToken}".encode())

    def _onNetworkReply(self, reply):
        endpoint = reply.url().toString()
        error = reply.error()

        if error != QNetworkReply.NoError:
            self._handleError(endpoint, reply.errorString())
            reply.deleteLater()
            return

        response_data = reply.readAll().data().decode('utf-8')
        try:
            json_data = json.loads(response_data)
            self._handleResponse(endpoint, json_data)
        except json.JSONDecodeError as e:
            self._handleError(endpoint, f"JSON Parse Error: {str(e)}")

        reply.deleteLater()

    def _handleResponse(self, endpoint, responseData):
        self.requestFinished.emit(endpoint, responseData)

    def _handleError(self, endpoint, errorMessage):
        self.requestFailed.emit(endpoint, errorMessage)