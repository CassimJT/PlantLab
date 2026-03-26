from PySide6.QtCore import QObject, Signal, Slot, QMutex, QMutexLocker, QUrl, QMetaObject, Qt, Q_ARG, QThread, QElapsedTimer
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtGui import QImage
from PySide6.QtCore import QByteArray
import cv2
import numpy as np
import concurrent.futures
import threading


class RTSVideoWorker(QObject):
    """
    Worker class that handles network streaming and decoding
    """

    # Signals
    frameReady = Signal(QImage)
    error = Signal(str)
    started = Signal()
    stopped = Signal()
    fpsUpdated = Signal(float)
    detectionResult = Signal(str)
    connectionStatusChanged = Signal(bool)  # Connection status signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._running_lock = threading.Lock()
        self._url = ""
        self._buffer = QByteArray()
        self._jpeg_queue = []
        self._queue_mutex = QMutex()
        self._decoder_running = False
        self._decoder_lock = threading.Lock()

        self._nam = None
        self._reply = None

        # Processing configuration
        self._config = {
            'enabled': True,
            'targetWidth': 640,
            'targetHeight': 480,
            'overlayEnabled': True,
            'overlayText': "ESP32-CAM",
            'detectionEnabled': False,
            'detectionInterval': 5
        }

        # Performance monitoring
        self._fps_timer = QElapsedTimer()
        self._frame_count = 0
        self._current_fps = 0.0
        self._detection_counter = 0

        # Detection results
        self._last_detection = {
            'faces': [],
            'face_rects': [],
            'objects': [],
            'has_qr_code': False,
            'qr_code_data': ""
        }
        self._detection_mutex = QMutex()

        # Memory pool
        self._reusable_buffer = bytearray(65536)
        self._buffer_mutex = QMutex()

        self._fps_timer.start()
        print("Worker created")

    # ======================================
    # Configuration methods
    # ======================================

    @Slot(bool)
    def setProcessingEnabled(self, enabled):
        self._config['enabled'] = enabled

    @Slot(int, int)
    def setTargetSize(self, width, height):
        self._config['targetWidth'] = width
        self._config['targetHeight'] = height

    @Slot(str)
    def setOverlayText(self, text):
        self._config['overlayText'] = text

    @Slot(bool)
    def setOverlayEnabled(self, enabled):
        self._config['overlayEnabled'] = enabled

    @Slot(bool)
    def setDetectionEnabled(self, enabled):
        self._config['detectionEnabled'] = enabled

    # ======================================
    # Main control slots
    # ======================================

    @Slot(str)
    def start(self, url):
        print(f"Worker start called: {url}")

        with self._running_lock:
            if not url or self._running:
                print("Worker already running or URL empty")
                return
            self._running = True

        self._url = url
        self._buffer.clear()
        self._frame_count = 0
        self._fps_timer.restart()

        self._nam = QNetworkAccessManager(self)
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b"User-Agent", b"ESP32-CAM-Qt-Client/1.0")

        self._reply = self._nam.get(request)
        self._reply.setReadBufferSize(0)

        self._reply.readyRead.connect(self._onData)
        self._reply.finished.connect(self._onFinished)

        self.started.emit()
        self.connectionStatusChanged.emit(True)  # Emit connected when starting
        print(f"Worker: Connecting to {url}")

    @Slot()
    def stop(self):
        print("Worker stop called")

        with self._running_lock:
            self._running = False

        self._clearQueue()

        if self._reply:
            self._reply.abort()
            self._reply.deleteLater()
            self._reply = None

        if self._nam:
            self._nam.deleteLater()
            self._nam = None

        # Clear reusable buffer
        with QMutexLocker(self._buffer_mutex):
            self._reusable_buffer = bytearray(65536)

        self.connectionStatusChanged.emit(False)  # Emit disconnected when stopping
        self.stopped.emit()

    def _is_running(self):
        with self._running_lock:
            return self._running

    # ======================================
    # Network data handling
    # ======================================

    @Slot()
    def _onData(self):
        if not self._is_running():
            return

        data = self._reply.readAll()

        with QMutexLocker(self._buffer_mutex):
            self._buffer.append(data)

        self._parseStreamData()

    def _parseStreamData(self):
        while self._is_running():
            with QMutexLocker(self._buffer_mutex):
                buffer = self._buffer

            start = buffer.indexOf(b"--frame")
            if start == -1:
                break

            header_end = buffer.indexOf(b"\r\n\r\n", start)
            if header_end == -1:
                break

            end = buffer.indexOf(b"--frame", header_end + 4)
            if end == -1:
                break

            jpeg = buffer.mid(header_end + 4, end - (header_end + 4))
            if jpeg.endsWith(b"\r\n"):
                jpeg.chop(2)

            with QMutexLocker(self._buffer_mutex):
                self._buffer.remove(0, end)

            if jpeg.size() > 0:
                with QMutexLocker(self._queue_mutex):
                    while len(self._jpeg_queue) >= 3:
                        self._jpeg_queue.pop(0)
                    self._jpeg_queue.append(jpeg)

                with self._decoder_lock:
                    if not self._decoder_running:
                        self._decoder_running = True
                        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                        executor.submit(self._decodeLoop)
                        executor.shutdown(wait=False)

    # ======================================
    # Frame processing
    # ======================================

    def _processFrame(self, raw_frame):
        """Process a single frame through the pipeline"""
        # Resize to target dimensions
        processed = cv2.resize(raw_frame, (self._config['targetWidth'], self._config['targetHeight']))

        # Convert BGR to RGB
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)

        # Run detection if enabled
        if self._config['detectionEnabled']:
            self._detection_counter += 1
            if self._detection_counter >= self._config['detectionInterval']:
                self._detection_counter = 0
                self._runDetectionModels(processed)
            self._drawDetectionResults(processed)

        # Apply overlay text
        if self._config['overlayEnabled']:
            self._applyOverlay(processed)

        # Convert to QImage
        height, width, channel = processed.shape
        bytes_per_line = channel * width
        img = QImage(processed.data, width, height, bytes_per_line, QImage.Format_RGB888)

        return img.copy()

    def _applyOverlay(self, frame):
        """Apply text overlay to frame"""
        overlay_text = self._config['overlayText']
        if self._current_fps > 0:
            overlay_text += f" | FPS: {int(self._current_fps)}"

        cv2.putText(frame, overlay_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Add detection results
        with QMutexLocker(self._detection_mutex):
            y = 60
            for face in self._last_detection['faces']:
                cv2.putText(frame, face, (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                y += 25

            if self._last_detection['has_qr_code']:
                cv2.putText(frame, f"QR: {self._last_detection['qr_code_data']}",
                           (10, frame.shape[0] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    def _runDetectionModels(self, frame):
        """
        ============================================================
        PLACE YOUR DETECTION MODELS HERE
        ============================================================

        Example face detection (commented):
        """
        # Example face detection (commented)
        """
        face_cascade = cv2.CascadeClassifier('/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 3, 0, (30, 30))

        with QMutexLocker(self._detection_mutex):
            self._last_detection['faces'].clear()
            self._last_detection['face_rects'].clear()

            for (x, y, w, h) in faces:
                self._last_detection['faces'].append("Face")
                self._last_detection['face_rects'].append((x, y, w, h))
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            if len(faces) > 0:
                self.detectionResult.emit(f"Detected {len(faces)} face(s)")
        """
        pass

    def _drawDetectionResults(self, frame):
        """Draw detection results on frame"""
        with QMutexLocker(self._detection_mutex):
            for (x, y, w, h) in self._last_detection['face_rects']:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    def _updateFPS(self):
        """Update FPS counter"""
        self._frame_count += 1
        elapsed = self._fps_timer.elapsed()

        if elapsed >= 1000:
            self._current_fps = (self._frame_count * 1000.0) / elapsed
            self.fpsUpdated.emit(self._current_fps)
            self._frame_count = 0
            self._fps_timer.restart()

    def _decodeLoop(self):
        """Main decode loop"""
        while self._is_running():
            jpeg = None
            with QMutexLocker(self._queue_mutex):
                if self._jpeg_queue:
                    jpeg = self._jpeg_queue.pop(0)

            if jpeg is None:
                with self._decoder_lock:
                    self._decoder_running = False
                return

            # Decode JPEG using OpenCV
            nparr = np.frombuffer(jpeg, np.uint8)
            raw = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if raw is not None and raw.size > 0:
                # Process the frame
                processed_image = self._processFrame(raw)

                # Update FPS
                self._updateFPS()

                # Send to main thread
                self.frameReady.emit(processed_image)

        with self._decoder_lock:
            self._decoder_running = False

    @Slot()
    def _onFinished(self):
        """Handle network stream finished"""
        error = self._reply.errorString() if self._reply else "No reply"
        print(f"Stream finished. Error: {error}")
        self.connectionStatusChanged.emit(False)  # Emit disconnected when stream ends
        if self._reply and self._reply.error() != QNetworkReply.NetworkError.NoError:
            self.error.emit(error)
        self.stop()

    def _clearQueue(self):
        """Clear all queues"""
        with QMutexLocker(self._queue_mutex):
            self._jpeg_queue.clear()

        with QMutexLocker(self._buffer_mutex):
            self._buffer.clear()