from PySide6.QtCore import QObject, Signal, Slot, QMutex, QMutexLocker, QUrl, QMetaObject, Qt, Q_ARG, QThread, Property
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtQuick import QQuickItem, QSGNode, QSGTexture, QSGSimpleTextureNode
from PySide6.QtGui import QImage
from .RTSVideoWorker import RTSVideoWorker
import os
import torch
from ultralytics import YOLO


class RTSVideoOutput(QQuickItem):
    # Signals
    rtsUrlChanged = Signal()
    processingEnabledChanged = Signal()
    overlayTextChanged = Signal()
    detectionEnabledChanged = Signal()
    fpsChanged = Signal()
    isConnectedChanged = Signal(bool)
    detectionResult = Signal(str)
    modelloaded = Signal()
    modelLoadingFailed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QQuickItem.ItemHasContents, True)

        # Core state
        self._rts_url = ""
        self._frame = QImage()
        self._frame_mutex = QMutex()
        self._processing_enabled = True
        self._overlay_text = "ESP32-CAM"
        self._detection_enabled = False
        self._current_fps = 0.0
        self._is_connected = False

        # Model
        self._modelPath = "/media/csociety/Backup/CISociety/Qt/Projects/Plantlab/assets/models/best.pt"
        self._model = None
        self._is_model_loaded = False

        # Worker
        self._worker = None
        self._worker_thread = None
        self._processing = False

        print("RTSVideoOutput created")
        self._loadModel()

    # ======================================
    # Properties (unchanged)
    # ======================================
    @Property(str, notify=rtsUrlChanged)
    def rtsUrl(self):
        return self._rts_url

    @rtsUrl.setter
    def rtsUrl(self, url):
        if self._rts_url == url:
            return
        was_running = self._processing
        self.stopProcessing()
        self._rts_url = url
        self.rtsUrlChanged.emit()
        print(f"URL changed to: {url}")
        if was_running and self.isComponentComplete() and self._rts_url:
            self.startProcessing()

    @Property(bool, notify=processingEnabledChanged)
    def processingEnabled(self):
        return self._processing_enabled

    @processingEnabled.setter
    def processingEnabled(self, val):
        if self._processing_enabled == val:
            return
        self._processing_enabled = val
        self.processingEnabledChanged.emit()
        self._applyWorkerSettings()

    @Property(bool, notify=detectionEnabledChanged)
    def detectionEnabled(self):
        return self._detection_enabled

    @detectionEnabled.setter
    def detectionEnabled(self, val):
        if self._detection_enabled == val:
            return
        self._detection_enabled = val
        self.detectionEnabledChanged.emit()
        self._applyWorkerSettings()

    @Property(float, notify=fpsChanged)
    def fps(self):
        return self._current_fps

    @Property(bool, notify=isConnectedChanged)
    def isConnected(self):
        return self._is_connected

    # ======================================
    # Lifecycle & Processing (unchanged - shortened for space)
    # ======================================
    def componentComplete(self):
        super().componentComplete()
        print(f"componentComplete, URL: {self._rts_url}")
        if self._rts_url:
            try:
                self.startProcessing()
            except Exception as e:
                print(f"componentComplete error: {e}")

    @Slot()
    def startProcessing(self):
        print(f"startProcessing → {self._rts_url}")
        if not self._rts_url or self._processing:
            return
        self.stopProcessing()

        self._worker = RTSVideoWorker()
        self._worker_thread = QThread()
        self._worker.moveToThread(self._worker_thread)

        self._worker.frameReady.connect(self._onFrameReady)
        self._worker.error.connect(self._onWorkerError)
        self._worker.fpsUpdated.connect(self._onFpsUpdated)
        self._worker.connectionStatusChanged.connect(self._onConnectionChanged)

        try:
            self._worker.detectionResult.connect(self._onDetectionResult)
        except:
            pass

        self._worker_thread.start()
        self._applyWorkerSettings()

        QMetaObject.invokeMethod(
            self._worker, "start", Qt.QueuedConnection, Q_ARG(str, self._rts_url)
        )
        self._processing = True

    @Slot()
    def stopProcessing(self):
        if not self._processing:
            return
        print("Stopping processing")
        if self._worker:
            QMetaObject.invokeMethod(self._worker, "stop", Qt.BlockingQueuedConnection)
        if self._worker_thread:
            self._worker_thread.quit()
            self._worker_thread.wait(2000)
        self._worker = None
        self._worker_thread = None
        with QMutexLocker(self._frame_mutex):
            self._frame = QImage()
        self._processing = False
        self._setConnected(False)
        self.update()

    @Slot(QImage)
    def _onFrameReady(self, frame):
        if frame.isNull(): return
        with QMutexLocker(self._frame_mutex):
            self._frame = frame
        self.update()

    @Slot(float)
    def _onFpsUpdated(self, fps):
        self._current_fps = fps
        self.fpsChanged.emit()

    @Slot(str)
    def _onWorkerError(self, msg):
        print(f"Worker error: {msg}")
        self._setConnected(False)

    @Slot(bool)
    def _onConnectionChanged(self, state):
        self._setConnected(state)

    @Slot(str)
    def _onDetectionResult(self, result):
        self.detectionResult.emit(result)

    def _setConnected(self, val):
        if self._is_connected != val:
            self._is_connected = val
            self.isConnectedChanged.emit(val)

    def _applyWorkerSettings(self):
        if not self._worker:
            return
        QMetaObject.invokeMethod(
            self._worker,
            "setDetectionEnabled",
            Qt.QueuedConnection,
            Q_ARG(bool, self._detection_enabled)
        )
        if self._is_model_loaded and self._model:
            self._worker.setModel(self._model)

    # ======================================
    # FIXED MODEL LOADING
    # ======================================
    def _loadModel(self):
        try:
            if not os.path.exists(self._modelPath):
                raise FileNotFoundError(self._modelPath)

            print(f"Loading model: {self._modelPath}")

            # Load custom .pth file
            checkpoint = torch.load(self._modelPath, map_location='cpu', weights_only=False)

            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                print("Found custom checkpoint with model_state_dict")

                # Create a new YOLO model (use the correct architecture)
                self._model = YOLO("yolo11n.yaml")   # Change to yolo11s.yaml / yolo11m.yaml if needed

                # Load the weights
                self._model.model.load_state_dict(checkpoint['model_state_dict'])

                # Optional: Set class names if available
                if 'class_names' in checkpoint:
                    self._model.names = {i: name for i, name in enumerate(checkpoint['class_names'])}
                    print(f"Loaded {len(self._model.names)} class names")

                print("Custom .pth model loaded successfully!")
            else:
                # Fallback for normal .pt
                self._model = YOLO(self._modelPath)
                print("Standard .pt model loaded")

            self._is_model_loaded = True
            if self._worker:
                self._worker.setModel(self._model)
            self.modelloaded.emit()

        except Exception as e:
            self._is_model_loaded = False
            self._model = None
            print(f"Model load failed: {e}")
            self.modelLoadingFailed.emit(str(e))

    # ======================================
    # Rendering
    # ======================================
    def updatePaintNode(self, old_node, _):
        node = old_node if isinstance(old_node, QSGSimpleTextureNode) else None
        with QMutexLocker(self._frame_mutex):
            frame = self._frame
        if frame.isNull():
            return None
        texture = self.window().createTextureFromImage(frame)
        if not node:
            node = QSGSimpleTextureNode()
        node.setTexture(texture)
        node.setRect(self.boundingRect())
        return node