from PySide6.QtCore import QObject, Signal, Slot, QMutex, QMutexLocker, QUrl, QMetaObject, Qt, Q_ARG, QThread, Property, QElapsedTimer
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtQuick import QQuickItem, QSGNode, QSGTexture, QSGSimpleTextureNode
from PySide6.QtGui import QImage
from PySide6.QtCore import QByteArray
from .RTSVideoWorker import RTSVideoWorker
import cv2
import numpy as np
import threading
import concurrent.futures
import torch
from ultralytics import YOLO
import os


class RTSVideoOutput(QQuickItem):
    """
    QML-accessible video output component that displays RTSP/MJPEG streams.
    """

    # QML Properties
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

        self._rts_url = ""
        self._frame = QImage()
        self._frame_mutex = QMutex()
        self._processing_enabled = True
        self._overlay_text = "ESP32-CAM"
        self._detection_enabled = False
        self._current_fps = 0.0
        self._is_connected = False
        self._is_model_loaded = False
        self._modelPath = "/media/csociety/Backup/CISociety/Qt/Projects/Plantlab/assets/models/best.pt"
        self._model = None

        # Worker management
        self._worker = None
        self._worker_thread = None
        self._processing = False

        # Texture caching
        self._cached_texture = None
        self._texture_size = None

        print("RTSVideoOutput created")

        # Load model on initialization
        self._loadModel()

    # ======================================
    # Property getters/setters
    # ======================================

    @Property(str, notify=rtsUrlChanged)
    def rtsUrl(self):
        return self._rts_url

    @rtsUrl.setter
    def rtsUrl(self, url):
        if self._rts_url == url:
            return

        was_processing = self._processing
        self.stopProcessing()

        self._rts_url = url
        self.rtsUrlChanged.emit()
        print(f"URL changed to: {url}")

        if was_processing and self.isComponentComplete() and self._rts_url:
            self.startProcessing()

    @Property(bool, notify=processingEnabledChanged)
    def processingEnabled(self):
        return self._processing_enabled

    @processingEnabled.setter
    def processingEnabled(self, enabled):
        if self._processing_enabled == enabled:
            return
        self._processing_enabled = enabled
        self.processingEnabledChanged.emit()
        self._applyWorkerSettings()

    @Property(str, notify=overlayTextChanged)
    def overlayText(self):
        return self._overlay_text

    @overlayText.setter
    def overlayText(self, text):
        if self._overlay_text == text:
            return
        self._overlay_text = text
        self.overlayTextChanged.emit()
        self._applyWorkerSettings()

    @Property(bool, notify=detectionEnabledChanged)
    def detectionEnabled(self):
        return self._detection_enabled

    @detectionEnabled.setter
    def detectionEnabled(self, enabled):
        if self._detection_enabled == enabled:
            return
        self._detection_enabled = enabled
        self.detectionEnabledChanged.emit()
        self._applyWorkerSettings()

    @Property(float, notify=fpsChanged)
    def fps(self):
        return self._current_fps

    @Property(bool, notify=isConnectedChanged)
    def isConnected(self):
        return self._is_connected

    @Property(bool)
    def isModelLoaded(self):
        return self._is_model_loaded

    @Property(str)
    def modelPath(self):
        return self._modelPath

    @modelPath.setter
    def modelPath(self, path):
        if self._modelPath == path:
            return
        self._modelPath = path
        self._loadModel()

    # ======================================
    # Public slots
    # ======================================

    def componentComplete(self):
        """Called when QML component is fully created"""
        super().componentComplete()
        print(f"RTSVideoOutput componentComplete, URL: {self._rts_url}")
        if self._rts_url:
            try:
                self.startProcessing()
            except Exception as e:
                print(f"Error in componentComplete: {e}")

    @Slot()
    def startProcessing(self):
        """Start the video processing pipeline"""
        print(f"RTSVideoOutput::startProcessing called with URL: {self._rts_url}")

        if not self._rts_url or self._processing:
            print("Cannot start - URL empty or already processing")
            return

        self.stopProcessing()

        # Create worker and thread
        self._worker = RTSVideoWorker()
        self._worker_thread = QThread()
        self._worker.moveToThread(self._worker_thread)

        # Connect signals
        self._worker_thread.started.connect(lambda: print("Worker thread started"))
        self._worker_thread.finished.connect(self._onWorkerThreadFinished)
        self._worker.frameReady.connect(self._onFrameReady)
        self._worker.error.connect(self._onWorkerError)
        self._worker.fpsUpdated.connect(self._onFpsUpdated)
        self._worker.detectionResult.connect(self._onDetectionResult)
        self._worker.connectionStatusChanged.connect(self._onConnectionChanged)

        self._worker_thread.start()

        # Apply settings before starting
        self._applyWorkerSettings()

        # Start the worker
        QMetaObject.invokeMethod(self._worker, "start",
                                 Qt.ConnectionType.QueuedConnection,
                                 Q_ARG(str, self._rts_url))

        self._processing = True
        print("Processing started")

    @Slot()
    def stopProcessing(self):
        """Stop the video processing pipeline"""
        if not self._processing:
            return

        print("Stopping processing")

        if self._worker:
            # Stop the worker first
            QMetaObject.invokeMethod(self._worker, "stop", Qt.ConnectionType.BlockingQueuedConnection)

            # Wait for worker to finish
            if self._worker_thread and self._worker_thread.isRunning():
                self._worker_thread.quit()
                if not self._worker_thread.wait(3000):
                    print("Worker thread didn't finish in time")

            # Clean up
            self._worker.deleteLater()
            self._worker = None

        if self._worker_thread:
            self._worker_thread.deleteLater()
            self._worker_thread = None

        with QMutexLocker(self._frame_mutex):
            self._frame = QImage()

        self._processing = False
        self._setConnected(False)
        self.update()
        print("Processing stopped")

    @Slot()
    def reloadModel(self):
        """Manually reload the model"""
        self._loadModel()

    # ======================================
    # Private slots
    # ======================================

    @Slot(QImage)
    def _onFrameReady(self, frame):
        """Receive processed frame from worker"""
        if not frame.isNull():
            with QMutexLocker(self._frame_mutex):
                self._frame = frame
            self.update()

    @Slot(str)
    def _onWorkerError(self, message):
        """Handle worker errors"""
        print(f"Worker error: {message}")
        self._setConnected(False)

    @Slot(float)
    def _onFpsUpdated(self, fps):
        """Update FPS display"""
        self._current_fps = fps
        self.fpsChanged.emit()

    @Slot(str)
    def _onDetectionResult(self, result):
        """Forward detection results to QML"""
        self.detectionResult.emit(result)

    @Slot(bool)
    def _onConnectionChanged(self, connected):
        """Handle connection state changes from worker"""
        self._setConnected(connected)

    def _setConnected(self, connected):
        """Set connection state and emit signal"""
        if self._is_connected != connected:
            self._is_connected = connected
            self.isConnectedChanged.emit(connected)
            print(f"Connection state changed: {connected}")

    def _onWorkerThreadFinished(self):
        """Handle worker thread finished"""
        print("Worker thread finished")
        self._worker_thread = None

    def _applyWorkerSettings(self):
        """Apply current settings to the worker"""
        if not self._worker:
            return

        QMetaObject.invokeMethod(self._worker, "setProcessingEnabled",
                                Qt.ConnectionType.QueuedConnection,
                                Q_ARG(bool, self._processing_enabled))
        QMetaObject.invokeMethod(self._worker, "setOverlayText",
                                Qt.ConnectionType.QueuedConnection,
                                Q_ARG(str, self._overlay_text))
        QMetaObject.invokeMethod(self._worker, "setDetectionEnabled",
                                Qt.ConnectionType.QueuedConnection,
                                Q_ARG(bool, self._detection_enabled))

        # Pass model to worker if loaded (direct assignment since we can't pass through signal)
        if self._is_model_loaded and self._model is not None and self._worker:
            self._worker.setModel(self._model)

    def _loadModel(self):
        """Load the model when the class app opens"""
        try:
            # Check if model file exists
            if not os.path.exists(self._modelPath):
                error_msg = f"Model file not found at: {self._modelPath}"
                print(error_msg)
                self._is_model_loaded = False
                self._model = None
                self.modelLoadingFailed.emit(error_msg)
                return

            print(f"Loading model from: {self._modelPath}")

            # Load the YOLO model
            self._model = YOLO(self._modelPath)
            self._is_model_loaded = True
            print("Pest detection model loaded successfully")
            if hasattr(self._model, 'names'):
                print(f"Model loaded with {len(self._model.names)} classes")

            # If worker exists, set the model directly
            if self._worker:
                self._worker.setModel(self._model)

            # Emit signal to notify QML that model is ready
            self.modelloaded.emit()

        except Exception as e:
            error_msg = f"Error loading model: {str(e)}"
            print(error_msg)
            self._is_model_loaded = False
            self._model = None
            self.modelLoadingFailed.emit(error_msg)

    # ======================================
    # Scene Graph Rendering
    # ======================================

    def _updateTexture(self):
        """Update the texture with the latest frame"""
        with QMutexLocker(self._frame_mutex):
            frame = self._frame

        if frame.isNull():
            if self._cached_texture:
                self._cached_texture = None
            return

        # Delete old texture
        if self._cached_texture:
            self._cached_texture = None

        window = self.window()
        if window:
            self._cached_texture = window.createTextureFromImage(frame)
            if self._cached_texture:
                self._cached_texture.setFiltering(QSGTexture.Filtering.Linear)

    def updatePaintNode(self, old_node, update_paint_node_data):
        """Update the scene graph node for rendering"""
        node = old_node if isinstance(old_node, QSGSimpleTextureNode) else None

        self._updateTexture()

        if not self._cached_texture:
            if node:
                node.deleteLater()
            return None

        if not node:
            node = QSGSimpleTextureNode()
            node.setOwnsTexture(False)

        node.setTexture(self._cached_texture)
        node.setRect(self.boundingRect())
        node.setFiltering(QSGTexture.Filtering.Linear)
        node.markDirty(QSGNode.DirtyMaterial)

        return node