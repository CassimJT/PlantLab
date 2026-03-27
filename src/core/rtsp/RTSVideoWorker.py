from PySide6.QtCore import QObject, Signal, Slot, QMutex, QMutexLocker, QUrl, QThreadPool, QRunnable
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtGui import QImage
from PySide6.QtCore import QByteArray

import cv2
import numpy as np
import threading
import time


# ============================================
# Detection Task (NON-BLOCKING)
# ============================================
class DetectionTask(QRunnable):
    def __init__(self, model, frame, callback):
        super().__init__()
        self.model = model
        self.frame = frame
        self.callback = callback
        self.setAutoDelete(True)

    def run(self):
        try:
            if self.model is None:
                return

            small = cv2.resize(self.frame, (224, 224))

            results = self.model(
                small,
                verbose=False,
                conf=0.5,
                iou=0.5,
                imgsz=224
            )

            self.callback(results)

        except Exception as e:
            print(f"[DetectionTask] Error: {e}")


# ============================================
# Worker
# ============================================
class RTSVideoWorker(QObject):

    # Signals
    frameReady = Signal(QImage)
    error = Signal(str)
    detectionResult = Signal(str)
    connectionStatusChanged = Signal(bool)
    fpsUpdated = Signal(float)   # ✅ FIXED

    def __init__(self):
        super().__init__()

        # Running state
        self._running = False
        self._running_lock = threading.Lock()

        # Network
        self._url = ""
        self._buffer = QByteArray()
        self._jpeg_queue = []

        self._queue_mutex = QMutex()
        self._buffer_mutex = QMutex()

        self._nam = None
        self._reply = None

        # Decoder
        self._decoder_thread = None
        self._stop_decoder = threading.Event()

        # Thread pool
        self._thread_pool = QThreadPool.globalInstance()
        self._thread_pool.setMaxThreadCount(1)

        # Detection
        self._model = None
        self._detection_enabled = False

        self._last_detection_time = 0
        self._detection_interval = 3.0
        self._detection_in_progress = False
        self._detection_mutex = QMutex()

        # Snapshot buffer
        self._latest_frame_for_detection = None
        self._frame_mutex = QMutex()

        # Detection results
        self._last_detection = {'pest_boxes': []}

        # FPS tracking
        self._frame_count = 0
        self._fps_timer = time.time()

        print("RTSVideoWorker initialized (SAFE MODE)")

    # ============================================
    # PUBLIC API
    # ============================================

    @Slot(object)
    def setModel(self, model):
        self._model = model

    @Slot(bool)
    def setDetectionEnabled(self, enabled):
        self._detection_enabled = enabled
        print(f"Detection {'ON' if enabled else 'OFF'}")

    @Slot(str)
    def start(self, url):
        with self._running_lock:
            if self._running:
                return
            self._running = True

        self._url = url
        self._buffer.clear()
        self._jpeg_queue.clear()
        self._stop_decoder.clear()

        self._nam = QNetworkAccessManager(self)
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b"Connection", b"close")

        self._reply = self._nam.get(request)
        self._reply.setReadBufferSize(1024)
        self._reply.readyRead.connect(self._onData)

        self._decoder_thread = threading.Thread(target=self._decodeLoop, daemon=True)
        self._decoder_thread.start()

        self.connectionStatusChanged.emit(True)
        print("Streaming started")

    @Slot()
    def stop(self):
        with self._running_lock:
            self._running = False

        self._stop_decoder.set()

        if self._reply:
            self._reply.abort()
            self._reply = None

        print("Streaming stopped")

    def _is_running(self):
        with self._running_lock:
            return self._running

    # ============================================
    # NETWORK
    # ============================================

    def _onData(self):
        if not self._is_running():
            return

        data = self._reply.read(1024)

        with QMutexLocker(self._buffer_mutex):
            if self._buffer.size() > 32768:
                self._buffer.clear()
                return
            self._buffer.append(data)

        self._parseStreamData()

    def _parseStreamData(self):
        while True:
            with QMutexLocker(self._buffer_mutex):
                buffer = self._buffer

            start = buffer.indexOf(b"\xff\xd8")
            end = buffer.indexOf(b"\xff\xd9")

            if start == -1 or end == -1:
                return

            jpeg = buffer.mid(start, end - start + 2)

            with QMutexLocker(self._buffer_mutex):
                self._buffer.remove(0, end + 2)

            with QMutexLocker(self._queue_mutex):
                self._jpeg_queue.clear()
                self._jpeg_queue.append(jpeg)

    # ============================================
    # DECODE LOOP
    # ============================================

    def _decodeLoop(self):
        last_time = 0
        min_interval = 0.15  # ~6 FPS

        while self._is_running() and not self._stop_decoder.is_set():

            jpeg = None
            with QMutexLocker(self._queue_mutex):
                if self._jpeg_queue:
                    jpeg = self._jpeg_queue.pop(-1)

            if jpeg is None:
                time.sleep(0.01)
                continue

            now = time.time()
            if now - last_time < min_interval:
                continue
            last_time = now

            arr = np.frombuffer(jpeg, np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

            if frame is None:
                continue

            image = self._processFrame(frame)
            self.frameReady.emit(image)

            # ✅ FPS CALCULATION
            self._frame_count += 1
            elapsed = now - self._fps_timer

            if elapsed >= 1.0:
                fps = self._frame_count / elapsed
                self.fpsUpdated.emit(fps)

                self._frame_count = 0
                self._fps_timer = now

    # ============================================
    # FRAME PROCESSING
    # ============================================

    def _processFrame(self, frame):

        frame = cv2.resize(frame, (640, 480))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Snapshot for detection
        with QMutexLocker(self._frame_mutex):
            self._latest_frame_for_detection = frame.copy()

        # Detection trigger
        if self._detection_enabled and self._model:

            now = time.time()

            with QMutexLocker(self._detection_mutex):
                busy = self._detection_in_progress

            if not busy and (now - self._last_detection_time >= self._detection_interval):

                frame_copy = None
                with QMutexLocker(self._frame_mutex):
                    if self._latest_frame_for_detection is not None:
                        frame_copy = self._latest_frame_for_detection.copy()

                if frame_copy is not None:
                    self._last_detection_time = now

                    with QMutexLocker(self._detection_mutex):
                        self._detection_in_progress = True

                    task = DetectionTask(self._model, frame_copy, self._detectionCallback)
                    self._thread_pool.start(task)

            else:
                self._drawDetections(frame)

        # Overlay
        cv2.putText(frame, "ESP32-CAM", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        h, w, c = frame.shape
        return QImage(frame.data, w, h, w * c, QImage.Format_RGB888)

    # ============================================
    # DETECTION CALLBACK
    # ============================================

    def _detectionCallback(self, results):

        with QMutexLocker(self._detection_mutex):
            self._detection_in_progress = False

        if not results or not self._is_running():
            return

        try:
            r = results[0]
            if r.boxes is None:
                return

            boxes = r.boxes.xyxy.cpu().numpy()

            new = {'pest_boxes': []}

            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                new['pest_boxes'].append((x1, y1, x2, y2))

            with QMutexLocker(self._detection_mutex):
                self._last_detection = new

        except Exception as e:
            print(f"[Callback] Error: {e}")

    # ============================================
    # DRAW DETECTIONS
    # ============================================

    def _drawDetections(self, frame):
        with QMutexLocker(self._detection_mutex):
            for (x1, y1, x2, y2) in self._last_detection['pest_boxes']:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)