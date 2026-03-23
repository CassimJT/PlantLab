# InfarenceRunnerWorker.py
import numpy as np
import cv2
import traceback
import os
from PySide6.QtCore import QRunnable, QObject, Signal, Slot, QMutex, QMutexLocker

from .frameworks import FrameworkFactory


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

    # detect available frameworks
    def _detect_available_frameworks(self):
        """Detect which frameworks are available"""
        available = []

        print("\n=== Framework Detection ===")

        # Import FrameworkFactory here to avoid circular imports
        from .frameworks import FrameworkFactory

        # Get all registered frameworks
        all_frameworks = list(FrameworkFactory._frameworks.keys())
        print(f"Registered frameworks: {all_frameworks}")

        # Suppress warnings during detection
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            # Check each framework using the class method
            for fw_name in all_frameworks:
                try:
                    framework_class = FrameworkFactory._frameworks.get(fw_name)
                    if framework_class:
                        print(f"Checking {fw_name}...")
                        is_avail = framework_class.is_available()
                        print(f"  → {fw_name} available: {is_avail}")
                        if is_avail:
                            available.append(fw_name)
                    else:
                        print(f"  → {fw_name} class not found")
                except Exception as e:
                    print(f"  → {fw_name} error: {e}")

        print(f"Detected frameworks: {available}")
        print("=== End Detection ===\n")

        self.signals.frameworks_detected.emit(available)
        self.signals.status_message.emit(f"Detected frameworks: {available}")
        return available

    def _detect_framework_from_extension(self, model_path: str) -> str:
        """Detect framework based on file extension"""
        ext = os.path.splitext(model_path)[1].lower()

        # Map extensions to frameworks
        extension_map = {
            '.pt': 'pytorch',
            '.pth': 'pytorch',
            '.pt2': 'pytorch',
            '.pkl': 'pytorch',
            '.h5': 'tensorflow',
            '.pb': 'tensorflow',
            '.tflite': 'tensorflow',
            '.keras': 'tensorflow',
            '.caffemodel': 'opencv',
            '.prototxt': 'opencv',
            '.weights': 'opencv',
            '.onnx': 'opencv',
            '.xml': 'opencv',
            '.bin': 'opencv',
            '.pte': 'executorch',
        }

        return extension_map.get(ext)

    def _try_load_with_frameworks(self, model_path: str, frameworks_to_try: list) -> bool:
        """Try loading model with multiple frameworks in order"""

        for fw_name in frameworks_to_try:
            try:
                self.signals.status_message.emit(f"Trying to load with {fw_name}...")

                # Create framework instance
                framework = FrameworkFactory.create(fw_name, model_path=model_path)

                if not framework or not framework.is_available():
                    self.signals.status_message.emit(f"  → {fw_name} not available")
                    continue

                # Try to load the model
                if framework.load_model(model_path):
                    self.framework = framework
                    self.framework_name = framework.get_framework_name()
                    self.is_model_loaded = True
                    self.signals.status_message.emit(f"  → Successfully loaded with {fw_name}")
                    return True
                else:
                    self.signals.status_message.emit(f"  → Failed to load with {fw_name}")

            except Exception as e:
                self.signals.status_message.emit(f"  → {fw_name} error: {str(e)}")
                continue

        return False

    def stop(self):
        """Stop the current task gracefully"""
        with QMutexLocker(self.mutex):
            self._is_running = False

    @Slot(str, str)
    def load_model(self, model_path: str, framework_name: str = None):
        """Load model using specified framework or auto-detect - THIS RUNS IN WORKER THREAD"""
        self.signals.model_load_started.emit(model_path)
        self.model_path = model_path

        try:
            self.signals.status_message.emit(f"Loading model from: {model_path}")

            # First, detect available frameworks
            available_frameworks = self._detect_available_frameworks()

            if not available_frameworks:
                error = "No frameworks available on this system"
                self.signals.model_load_failed.emit(error, "unknown")
                return

            # Case 1: User specified a framework
            if framework_name and framework_name != "":
                self.signals.status_message.emit(f"Using specified framework: {framework_name}")

                # Check if framework is available
                if framework_name not in available_frameworks:
                    error = f"Framework '{framework_name}' is not available. Available: {available_frameworks}"
                    self.signals.model_load_failed.emit(error, framework_name)
                    return

                # Try to load with specified framework
                if self._try_load_with_frameworks(model_path, [framework_name]):
                    self.signals.model_load_finished.emit(self.framework_name, True)
                else:
                    error = f"Failed to load model with {framework_name}"
                    self.signals.model_load_failed.emit(error, framework_name)
                return

            # Case 2: Try to detect from file extension
            detected_framework = self._detect_framework_from_extension(model_path)

            if detected_framework:
                self.signals.status_message.emit(f"Detected framework from extension: {detected_framework}")

                # Check if detected framework is available
                if detected_framework in available_frameworks:
                    if self._try_load_with_frameworks(model_path, [detected_framework]):
                        self.signals.model_load_finished.emit(self.framework_name, True)
                        return
                    else:
                        self.signals.status_message.emit(f"Detected framework {detected_framework} failed, trying others...")
                else:
                    self.signals.status_message.emit(f"Detected framework {detected_framework} not available")

            # Case 3: Try all available frameworks
            self.signals.status_message.emit("Trying all available frameworks...")

            if self._try_load_with_frameworks(model_path, available_frameworks):
                self.signals.model_load_finished.emit(self.framework_name, True)
            else:
                error = f"Failed to load model with any available framework. Tried: {available_frameworks}"
                self.signals.model_load_failed.emit(error, "unknown")

        except Exception as e:
            error_msg = f"Model loading failed: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            self.is_model_loaded = False
            self.signals.model_load_failed.emit(error_msg, framework_name or "unknown")

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
            self.signals.status_message.emit(f"Inference complete: Class {class_id} with {confidence:.2f}% confidence")

            # Emit results
            self.signals.inference_finished.emit(class_id, confidence, self.framework_name)

        except Exception as e:
            error_msg = f"Inference failed: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            self.signals.inference_failed.emit(error_msg, self.framework_name or "unknown")

    # InfarenceRunnerWorker.py - Fix _load_image method

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
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, (224, 224))
                    print(f"Image resized to: {img.shape}")
                return img
            else:
                # Handle file paths - make sure it's a string and exists
                if not isinstance(image_source, str):
                    print(f"Invalid image_source type: {type(image_source)}")
                    return None

                # Clean up the path
                file_path = image_source.strip()
                if file_path.startswith('file://'):
                    # Already handled in runner, but just in case
                    from PySide6.QtCore import QUrl
                    file_path = QUrl(file_path).toLocalFile()

                print(f"Attempting to load image from: {file_path}")

                # Check if file exists
                if not os.path.exists(file_path):
                    print(f"Image file does not exist: {file_path}")
                    return None

                # Read the image
                img = cv2.imread(file_path)
                if img is None:
                    print(f"cv2.imread failed for: {file_path}")
                    return None

                # Convert BGR to RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                print(f"Image loaded successfully: {file_path}, shape: {img.shape}")
                return img

        except Exception as e:
            print(f"Error loading image: {e}")
            traceback.print_exc()
            return None

    def get_available_frameworks(self):
        """Get list of available frameworks"""
        return self._detect_available_frameworks()

    def run(self):
        """QRunnable run method - required but we use Slots"""
        # This is called when the thread starts
        # We're using Slot decorators for the actual work
        pass