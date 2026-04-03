from PySide6.QtCore import QObject, Signal, Slot, QMutex, QMutexLocker, QUrl, QThreadPool, QRunnable
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtGui import QImage
from PySide6.QtCore import QByteArray
import cv2
import numpy as np
import threading
import time


# ============================================
# Detection Task
# ============================================
class DetectionTask(QRunnable):
    def __init__(self, model, frame, callback, original_shape):
        super().__init__()
        self.model = model
        self.frame = frame
        self.callback = callback
        self.original_shape = original_shape
        self.setAutoDelete(True)

    def run(self):
        try:
            if self.model is None:
                return

            input_size = 640
            small = cv2.resize(self.frame, (input_size, input_size))

            results = self.model(
                small,
                verbose=False,
                conf=0.20,
                iou=0.45,
                imgsz=input_size,
                max_det=20
            )
            self.callback(results, self.original_shape)
        except Exception as e:
            print(f"[DetectionTask] Error: {e}")


# ============================================
# Worker
# ============================================
class RTSVideoWorker(QObject):
    frameReady = Signal(QImage)
    error = Signal(str)
    detectionResult = Signal(str)
    connectionStatusChanged = Signal(bool)
    fpsUpdated = Signal(float)

    def __init__(self):
        super().__init__()
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
        self._thread_pool.setMaxThreadCount(2)

        # Detection
        self._model = None
        self._detection_enabled = False
        self._last_detection_time = 0
        self._detection_interval = 0.8
        self._detection_in_progress = False
        self._detection_mutex = QMutex()

        self._latest_frame_for_detection = None
        self._frame_mutex = QMutex()

        self._last_detection = {'detections': []}
        self._last_good_detection_time = 0
        self._persistence_time = 7.0

        self._frame_count = 0
        self._fps_timer = time.time()

        print("RTSVideoWorker initialized - 5 SECOND PERSISTENCE")

    @Slot(object)
    def setModel(self, model):
        self._model = model
        if model and hasattr(model, 'names'):
            print(f"Model loaded with {len(model.names)} classes")

    @Slot(bool)
    def setDetectionEnabled(self, enabled):
        self._detection_enabled = enabled
        print(f"Detection {'ON' if enabled else 'OFF'}")

    @Slot(str)
    def start(self, url):
        with self._running_lock:
            if self._running: return
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

    def _onData(self):
        if not self._is_running(): return
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
            if start == -1 or end == -1: return
            jpeg = buffer.mid(start, end - start + 2)
            with QMutexLocker(self._buffer_mutex):
                self._buffer.remove(0, end + 2)
            with QMutexLocker(self._queue_mutex):
                self._jpeg_queue.clear()
                self._jpeg_queue.append(jpeg)

    def _decodeLoop(self):
        last_time = 0
        min_interval = 0.12
        while self._is_running() and not self._stop_decoder.is_set():
            jpeg = None
            with QMutexLocker(self._queue_mutex):
                if self._jpeg_queue:
                    jpeg = self._jpeg_queue.pop(-1)

            if jpeg is None:
                time.sleep(0.01)
                continue

            now = time.time()
            if now - last_time < min_interval: continue
            last_time = now

            arr = np.frombuffer(jpeg, np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is None: continue

            image = self._processFrame(frame)
            self.frameReady.emit(image)

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

        with QMutexLocker(self._frame_mutex):
            self._latest_frame_for_detection = frame.copy()

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

                    task = DetectionTask(self._model, frame_copy, self._detectionCallback, frame_copy.shape)
                    self._thread_pool.start(task)
            else:
                self._drawDetections(frame)

        cv2.putText(frame, "ESP32-CAM", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        count = len(self._last_detection['detections'])
        color = (0, 255, 0) if count > 0 else (0, 0, 255)
        cv2.putText(frame, f"Pests: {count}", (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        h, w, c = frame.shape
        return QImage(frame.data, w, h, w * c, QImage.Format_RGB888)

    # ============================================
    # DETECTION CALLBACK
    # ============================================
    def _detectionCallback(self, results, original_shape):
        with QMutexLocker(self._detection_mutex):
            self._detection_in_progress = False

        if not results or not self._is_running():
            return

        try:
            r = results[0]
            if r.boxes is not None and len(r.boxes) > 0:
                orig_h, orig_w = original_shape[:2]
                input_size = 640
                new_detections = []
                boxes = r.boxes.xyxy.cpu().numpy()
                classes = r.boxes.cls.cpu().numpy().astype(int)
                confs = r.boxes.conf.cpu().numpy()
                names = self._model.names

                for box, cls_id, conf in zip(boxes, classes, confs):
                    x1, y1, x2, y2 = box
                    x1 = int(x1 * orig_w / input_size)
                    y1 = int(y1 * orig_h / input_size)
                    x2 = int(x2 * orig_w / input_size)
                    y2 = int(y2 * orig_h / input_size)

                    label = names.get(cls_id, f"Pest_{cls_id}")
                    new_detections.append((x1, y1, x2, y2, label, float(conf)))

                with QMutexLocker(self._detection_mutex):
                    self._last_detection = {'detections': new_detections}
                    self._last_good_detection_time = time.time()

                print(f"Detected {len(new_detections)} pests")
        except Exception as e:
            print(f"[Callback] Error: {e}")

    # ============================================
    # DRAW DETECTIONS WITH 5s PERSISTENCE
    # ============================================
    def _drawDetections(self, frame):
        now = time.time()
        with QMutexLocker(self._detection_mutex):
            if (now - self._last_good_detection_time) < self._persistence_time:
                detections = self._last_detection['detections']
            else:
                detections = []

        for det in detections:
            x1, y1, x2, y2, label, conf = det
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            text = f"{label} {conf:.2f}"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
            cv2.rectangle(frame, (x1, y1-28), (x1 + tw + 8, y1), (0, 255, 0), -1)
            cv2.putText(frame, text, (x1 + 4, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)