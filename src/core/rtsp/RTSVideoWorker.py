from PySide6.QtCore import QObject, Signal, Slot, QMutex, QMutexLocker, QUrl, QMetaObject, Qt, Q_ARG, QElapsedTimer, QThreadPool, QRunnable, QTimer
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtGui import QImage
from PySide6.QtCore import QByteArray
import cv2
import numpy as np
import threading
import time


class DetectionTask(QRunnable):
    """Optimized detection task with smaller frame size"""
    def __init__(self, model, frame, callback):
        super().__init__()
        self.model = model
        # Resize frame to smaller size BEFORE detection to save CPU
        self.frame = cv2.resize(frame, (320, 240))
        self.callback = callback
        self.setAutoDelete(True)

    def run(self):
        try:
            if self.model is None:
                return
            # Run detection with lower confidence threshold for faster processing
            results = self.model(self.frame, verbose=False, conf=0.4, iou=0.5)
            self.callback(results)
        except Exception as e:
            print(f"Detection task error: {e}")


class RTSVideoWorker(QObject):
    """
    Optimized version with gentle detection to prevent ESP32 reset
    """

    frameReady = Signal(QImage)
    error = Signal(str)
    started = Signal()
    stopped = Signal()
    fpsUpdated = Signal(float)
    detectionResult = Signal(str)
    connectionStatusChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._running_lock = threading.Lock()
        self._url = ""
        self._buffer = QByteArray()
        self._jpeg_queue = []
        self._queue_mutex = QMutex()
        self._buffer_mutex = QMutex()
        self._decoder_running = False
        self._decoder_lock = threading.Lock()
        self._decoder_thread = None
        self._stop_decoder = threading.Event()

        self._nam = None
        self._reply = None

        # Thread pool for detection
        self._thread_pool = QThreadPool.globalInstance()
        self._thread_pool.setMaxThreadCount(1)

        # Detection throttling
        self._detection_in_progress = False
        self._detection_progress_mutex = QMutex()
        self._last_detection_time = 0
        self._detection_cooldown = 2.0  # 2 seconds between detections (much slower)

        self._config = {
            'enabled': True,
            'targetWidth': 640,
            'targetHeight': 480,
            'overlayEnabled': True,
            'overlayText': "ESP32-CAM",
            'detectionEnabled': False,
            'detectionInterval': 30,  # Run every 30 frames (much less frequent)
        }

        self._fps_timer = QElapsedTimer()
        self._frame_count = 0
        self._current_fps = 0.0
        self._detection_counter = 0

        self._last_detection = {
            'pests': [], 'pest_boxes': [], 'pest_classes': [], 'pest_confidences': []
        }
        self._detection_mutex = QMutex()

        self._model = None
        self._fps_timer.start()
        print("Worker created - Detection will run every 2 seconds maximum")

    @Slot(bool)
    def setDetectionEnabled(self, enabled):
        """Enable detection with delayed start to let ESP32 stabilize"""
        if enabled and self._model is not None:
            print("Detection will start in 5 seconds to let ESP32 stabilize...")
            QTimer.singleShot(5000, lambda: self._actuallyEnableDetection(True))
        else:
            self._actuallyEnableDetection(enabled)

    def _actuallyEnableDetection(self, enabled):
        """Actually enable detection"""
        self._config['detectionEnabled'] = enabled
        if enabled:
            self._detection_counter = 0
            self._last_detection_time = 0
            print("PEST DETECTION NOW ACTIVE - Running every 2 seconds")
        else:
            print("Pest detection disabled")

    @Slot(object)
    def setModel(self, model):
        self._model = model
        if model and hasattr(model, 'names'):
            print(f"Model set with {len(model.names)} classes")

    @Slot(str)
    def start(self, url):
        with self._running_lock:
            if not url or self._running:
                return
            self._running = True

        self._url = url
        self._buffer.clear()
        self._jpeg_queue.clear()
        self._stop_decoder.clear()

        # Use connection: close to prevent hanging
        self._nam = QNetworkAccessManager(self)
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b"User-Agent", b"ESP32-CAM-Qt-Client/1.0")
        request.setRawHeader(b"Connection", b"close")
        request.setRawHeader(b"Cache-Control", b"no-cache")

        self._reply = self._nam.get(request)
        self._reply.setReadBufferSize(4096)  # Smaller buffer

        self._reply.readyRead.connect(self._onData)
        self._reply.finished.connect(self._onFinished)

        with self._decoder_lock:
            if not self._decoder_running:
                self._decoder_running = True
                self._decoder_thread = threading.Thread(target=self._decodeLoop, daemon=True)
                self._decoder_thread.start()

        self.started.emit()
        self.connectionStatusChanged.emit(True)
        print(f"Started streaming from {url}")

    @Slot()
    def stop(self):
        print("Stopping worker")
        with self._running_lock:
            self._running = False
        self._stop_decoder.set()

        if self._reply:
            self._reply.abort()
            self._reply.deleteLater()
            self._reply = None
        if self._nam:
            self._nam.deleteLater()
            self._nam = None

        if self._decoder_thread and self._decoder_thread.is_alive():
            self._decoder_thread.join(timeout=1.0)

        with QMutexLocker(self._queue_mutex):
            self._jpeg_queue.clear()
        with QMutexLocker(self._buffer_mutex):
            self._buffer.clear()

        self.connectionStatusChanged.emit(False)
        self.stopped.emit()
        print("Worker stopped")

    def _is_running(self):
        with self._running_lock:
            return self._running

    @Slot()
    def _onData(self):
        if not self._is_running():
            return
        try:
            data = self._reply.read(2048)  # Even smaller reads
            if data:
                with QMutexLocker(self._buffer_mutex):
                    # Limit buffer size to prevent memory bloat
                    if self._buffer.size() < 65536:
                        self._buffer.append(data)
                self._parseStreamData()
        except Exception as e:
            print(f"Network read error: {e}")

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
                    # Keep only the latest frame
                    self._jpeg_queue.clear()
                    self._jpeg_queue.append(jpeg)

    def _decodeLoop(self):
        try:
            last_frame_time = 0
            min_frame_interval = 0.05  # 20 FPS max (faster than ESP32's 10 FPS limit)
            frame_count = 0
            start_time = time.time()

            while self._is_running() and not self._stop_decoder.is_set():
                jpeg = None
                with QMutexLocker(self._queue_mutex):
                    if self._jpeg_queue:
                        jpeg = self._jpeg_queue.pop(0)

                if jpeg is None:
                    time.sleep(0.005)
                    continue

                # Throttle frame rate to match ESP32's output
                current_time = time.time()
                if current_time - last_frame_time < min_frame_interval:
                    continue
                last_frame_time = current_time

                nparr = np.frombuffer(jpeg, np.uint8)
                raw = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if raw is not None and raw.size > 0:
                    processed_image = self._processFrame(raw)
                    self._updateFPS()

                    # Log FPS occasionally
                    frame_count += 1
                    if frame_count % 60 == 0:
                        elapsed = time.time() - start_time
                        fps = frame_count / elapsed
                        if fps > 20:
                            print(f"WARNING: High FPS {fps:.1f} - Consider reducing")
                        frame_count = 0
                        start_time = time.time()

                    if self._is_running():
                        self.frameReady.emit(processed_image)
        except Exception as e:
            print(f"Decode loop error: {e}")
        finally:
            with self._decoder_lock:
                self._decoder_running = False
                print("Decode loop ended")

    def _processFrame(self, raw_frame):
        # Resize to target dimensions
        processed = cv2.resize(raw_frame, (self._config['targetWidth'], self._config['targetHeight']))
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)

        # Run detection only if enabled and model exists
        if self._config['detectionEnabled'] and self._model is not None:
            self._detection_counter += 1

            # Check if we should run detection (based on both frame count AND time)
            current_time = time.time()
            time_since_last = current_time - self._last_detection_time

            if (self._detection_counter >= self._config['detectionInterval'] or
                time_since_last >= 2.0):  # At least 2 seconds between detections

                # Check if detection is already in progress
                detection_in_progress = False
                with QMutexLocker(self._detection_progress_mutex):
                    detection_in_progress = self._detection_in_progress

                if not detection_in_progress:
                    self._detection_counter = 0
                    self._last_detection_time = current_time

                    with QMutexLocker(self._detection_progress_mutex):
                        self._detection_in_progress = True

                    # Run detection on background thread with smaller frame
                    task = DetectionTask(self._model, processed, self._detectionCallback)
                    self._thread_pool.start(task)
            else:
                # Draw last known detection results
                self._drawDetectionResults(processed)

        # Apply overlay
        if self._config['overlayEnabled']:
            self._applyOverlay(processed)

        h, w, c = processed.shape
        return QImage(processed.data, w, h, w * c, QImage.Format_RGB888)

    # Callback from detection thread
    def _detectionCallback(self, results):
        # Reset detection in progress flag
        with QMutexLocker(self._detection_progress_mutex):
            self._detection_in_progress = False

        if not self._is_running() or not results:
            return

        try:
            result = results[0]
            if not hasattr(result, 'boxes') or result.boxes is None:
                return

            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy().astype(int)
            class_names = self._model.names

            # Scale boxes from detection size (320x240) to display size (640x480)
            sx = self._config['targetWidth'] / 320.0
            sy = self._config['targetHeight'] / 240.0

            detected_pests = []
            new_detections = {
                'pests': [], 'pest_boxes': [], 'pest_classes': [], 'pest_confidences': []
            }

            for box, conf, cls in zip(boxes, confidences, classes):
                if conf < 0.4:  # Higher threshold for fewer false positives
                    continue
                pest_name = class_names.get(cls, f"Pest_{cls}")
                x1, y1, x2, y2 = map(int, box * [sx, sy, sx, sy])

                new_detections['pests'].append(f"{pest_name}: {conf:.2f}")
                new_detections['pest_boxes'].append((x1, y1, x2, y2))
                new_detections['pest_classes'].append(cls)
                new_detections['pest_confidences'].append(conf)
                detected_pests.append(f"{pest_name} ({conf:.2f})")

            # Update last detection results
            with QMutexLocker(self._detection_mutex):
                self._last_detection = new_detections

            # Emit detection result summary (throttled)
            if detected_pests and self._is_running():
                summary = f"Detected {len(detected_pests)} pests: {', '.join(detected_pests[:2])}"
                if len(detected_pests) > 2:
                    summary += f" and {len(detected_pests) - 2} more"
                self.detectionResult.emit(summary)
                print(summary)

        except Exception as e:
            print(f"Detection callback error: {e}")

    def _get_class_color(self, class_id):
        """Generate consistent color for each pest class"""
        np.random.seed(class_id % 256)
        color = np.random.randint(100, 255, 3).tolist()
        return (color[2], color[1], color[0])

    def _drawDetectionResults(self, frame):
        """Draw detection results on frame"""
        with QMutexLocker(self._detection_mutex):
            for idx, (x1, y1, x2, y2) in enumerate(self._last_detection.get('pest_boxes', [])):
                if idx < len(self._last_detection.get('pest_classes', [])):
                    color = self._get_class_color(self._last_detection['pest_classes'][idx])
                else:
                    color = (0, 255, 0)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                if idx < len(self._last_detection.get('pests', [])):
                    label = self._last_detection['pests'][idx]
                    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(frame, (x1, y1 - th - 5), (x1 + tw, y1), color, -1)
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def _applyOverlay(self, frame):
        """Apply overlay text with pest count"""
        overlay_text = self._config['overlayText']
        if self._current_fps > 0:
            overlay_text += f" | FPS: {int(self._current_fps)}"

        with QMutexLocker(self._detection_mutex):
            pest_count = len(self._last_detection.get('pests', []))
            if pest_count > 0:
                overlay_text += f" | Pests: {pest_count}"

        detection_status = "ON" if (self._config['detectionEnabled'] and self._model) else "OFF"
        overlay_text += f" | Detect: {detection_status}"

        cv2.putText(frame, overlay_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    def _updateFPS(self):
        self._frame_count += 1
        elapsed = self._fps_timer.elapsed()
        if elapsed >= 1000:
            self._current_fps = (self._frame_count * 1000.0) / elapsed
            self.fpsUpdated.emit(self._current_fps)
            self._frame_count = 0
            self._fps_timer.restart()

    @Slot()
    def _onFinished(self):
        print("Stream finished")
        self.connectionStatusChanged.emit(False)
        self.stop()