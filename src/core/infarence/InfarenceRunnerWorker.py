# InfarenceRunnerWorker.py
import numpy as np
import cv2
import traceback
import os
from PySide6.QtCore import QRunnable, QObject, Signal, Slot, QMutex, QMutexLocker

from .frameworks import FrameworkFactory
from .frameworks.pytorch_framework import PyTorchFramework


# ============================================
# Signal Class (must be separate QObject)
# ============================================
class InfarenceRunnerSignals(QObject):
    """Signals for communicating between worker and main thread"""

    # Inference signals
    inference_started = Signal()
    inference_finished = Signal(int, float, str)  # class_id, confidence, framework_name
    inference_failed = Signal(str, str)  # error_message, framework_name

    # Model loading signals
    model_load_started = Signal(str)  # model_path
    model_load_finished = Signal(str, bool)  # framework_name, success
    model_load_failed = Signal(str, str)  # error_message, framework_name

    # Progress signals
    progress_updated = Signal(int)  # percentage

    # Framework signals
    frameworks_detected = Signal(list)  # available frameworks

    # Debug/status signals
    status_message = Signal(str)
    debug_info = Signal(dict)


# ============================================
# Worker Task (QRunnable)
# ============================================
class InfarenceRunnerTask(QRunnable):
    """QRunnable task for running inference in thread pool"""

    def __init__(self):
        super().__init__()

        # Signals (must be created in this thread)
        self.signals = InfarenceRunnerSignals()

        # Framework instances
        self.framework = None
        self.framework_name = None
        self.is_model_loaded = False

        # Model configuration
        self.input_size = 224
        self.num_classes = 38
        self.default_framework = "pytorch"
        self.model_path = None

        # Thread safety
        self.mutex = QMutex()
        self._is_running = True

        # Set auto-deletion (freed after run() completes)
        self.setAutoDelete(True)

        # Auto-detect available frameworks
        self._detect_available_frameworks()

    def _detect_available_frameworks(self):
        """Detect which frameworks are available"""
        available = []

        # Check each framework
        for fw_name in ["pytorch", "tensorflow", "executorch", "opencv"]:
            try:
                framework = FrameworkFactory.create(fw_name)
                if framework and framework.is_available():
                    available.append(fw_name)
            except Exception as e:
                print(f"Framework {fw_name} not available: {e}")

        self.signals.frameworks_detected.emit(available)
        self.signals.status_message.emit(f"Detected frameworks: {available}")
        return available

    def stop(self):
        """Stop the current task gracefully"""
        with QMutexLocker(self.mutex):
            self._is_running = False

    @Slot(str, str)
    def load_model(self, model_path: str, framework_name: str = None):
        """Load model using specified framework or auto-detect"""
        self.signals.model_load_started.emit(model_path)
        self.model_path = model_path

        try:
            self.signals.status_message.emit(f"Loading model from: {model_path}")

            # Use specified framework or try to detect
            if framework_name:
                self.signals.status_message.emit(f"Using specified framework: {framework_name}")
                self.framework = FrameworkFactory.create(framework_name, model_path=model_path)
                if not self.framework:
                    error = f"Framework '{framework_name}' not available"
                    self.signals.model_load_failed.emit(error, framework_name)
                    return
            else:
                # Try to detect framework from file extension
                self.signals.status_message.emit("Auto-detecting framework...")
                self.framework = self._detect_framework(model_path)

            if not self.framework:
                # Fallback to PyTorch
                self.signals.status_message.emit("Falling back to PyTorch framework")
                self.framework = PyTorchFramework(model_path)

            # Load the model
            self.signals.status_message.emit(f"Loading with {self.framework.get_framework_name()}...")
            success = self.framework.load_model(model_path)

            if success:
                self.is_model_loaded = True
                self.framework_name = self.framework.get_framework_name()
                self.signals.model_load_finished.emit(self.framework_name, True)
                self.signals.status_message.emit(f"✅ Model loaded with {self.framework_name}")
            else:
                self.is_model_loaded = False
                self.framework_name = self.framework.get_framework_name() if self.framework else "Unknown"
                self.signals.model_load_failed.emit("Failed to load model", self.framework_name)
                self.signals.status_message.emit(f"❌ Failed to load model with {self.framework_name}")

        except Exception as e:
            error_msg = f"Model loading failed: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            self.is_model_loaded = False
            self.signals.model_load_failed.emit(error_msg, framework_name or "unknown")

    def _detect_framework(self, model_path: str):
        """Try to detect appropriate framework from file extension"""
        ext = os.path.splitext(model_path)[1].lower()

        # Map extensions to frameworks
        framework_map = {
            '.pt': 'pytorch',
            '.pth': 'pytorch',
            '.pt2': 'pytorch',
            '.onnx': 'onnx',
            '.tflite': 'tensorflow',
            '.h5': 'tensorflow',
            '.pb': 'tensorflow',
            '.caffemodel': 'opencv',
            '.weights': 'opencv',
            '.pte': 'executorch',
            '.bin': 'executorch',
        }

        suggested = framework_map.get(ext)
        if suggested:
            self.signals.status_message.emit(f"Detected framework from extension: {suggested}")
            return FrameworkFactory.create(suggested)

        # Try each available framework
        for fw_name in ["pytorch", "tensorflow", "executorch", "opencv"]:
            try:
                framework = FrameworkFactory.create(fw_name)
                if framework and framework.is_available():
                    self.signals.status_message.emit(f"Trying framework: {fw_name}")
                    return framework
            except:
                continue

        return None

    @Slot(str)
    def classify_image(self, image_source):
        """Classify image - runs in thread pool"""
        try:
            self.signals.inference_started.emit()
            self.signals.status_message.emit(f"Classifying image using {self.framework_name}")
            self.signals.progress_updated.emit(10)

            # Check if model is loaded
            if not self.is_model_loaded or self.framework is None:
                self.signals.inference_failed.emit("Model not loaded", self.framework_name or "unknown")
                return

            # Load and preprocess image
            self.signals.status_message.emit("Loading image...")
            img = self._load_image(image_source)
            if img is None:
                self.signals.inference_failed.emit("Failed to load image", self.framework_name)
                return

            self.signals.progress_updated.emit(25)
            self.signals.status_message.emit("Preprocessing image...")

            # Preprocess using framework
            input_tensor = self.framework.preprocess(img, self.input_size)

            self.signals.progress_updated.emit(50)
            self.signals.status_message.emit("Running inference...")

            # Run inference
            outputs = self.framework.run_inference(input_tensor)

            self.signals.progress_updated.emit(75)
            self.signals.status_message.emit("Postprocessing results...")

            # Postprocess
            class_id, confidence = self.framework.postprocess(outputs)

            self.signals.progress_updated.emit(100)
            self.signals.status_message.emit(f"✅ Inference complete: Class {class_id} with {confidence:.2f}% confidence")

            # Emit results
            self.signals.inference_finished.emit(class_id, confidence, self.framework_name)

        except Exception as e:
            error_msg = f"Inference failed: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            self.signals.inference_failed.emit(error_msg, self.framework_name or "unknown")

    def _load_image(self, image_source):
        """Load image from path or base64"""
        try:
            # Handle base64 images
            if isinstance(image_source, str) and image_source.startswith('data:image'):
                import base64
                base64_data = image_source.split(',')[1]
                img_data = base64.b64decode(base64_data)
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                # Handle file paths
                img = cv2.imread(image_source)
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            if img is None:
                self.signals.status_message.emit(f"❌ Failed to load image: {image_source}")

            return img
        except Exception as e:
            self.signals.status_message.emit(f"Error loading image: {e}")
            return None

    def get_available_frameworks(self):
        """Get list of available frameworks"""
        return self._detect_available_frameworks()

    def run(self):
        """QRunnable run method - required but we use Slots"""
        # This is called when the thread starts
        # We're using Slot decorators for the actual work
        pass
