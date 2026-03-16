# InfarenceRunner.py
import os
from PySide6.QtCore import QObject, Signal, Slot, Property, QThreadPool
from PySide6.QtCore import QUrl, QStandardPaths

from .DiseaseInfoManager import DiseaseInfoManager
from .InfarenceRunnerWorker import InfarenceRunnerTask, InfarenceRunnerSignals

class InfarenceRunner(QObject):
    """Main runner class that manages the QRunnable worker"""

    # Forward signals from worker
    inference_started = Signal()
    inference_finished = Signal()
    inference_failed = Signal(str)
    model_load_started = Signal(str)
    model_load_finished = Signal(str, bool)
    model_load_failed = Signal(str, str)
    progress_updated = Signal(int)
    frameworks_detected = Signal(list)
    status_message = Signal(str)

    # Property change signals
    disease_name_changed = Signal()
    description_changed = Signal()
    cure_changed = Signal()
    confidence_changed = Signal()
    class_index_changed = Signal()
    is_model_loaded_changed = Signal()
    language_changed = Signal(str)
    framework_changed = Signal(str)
    available_frameworks_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Properties
        self._disease_name = ""
        self._description = ""
        self._cure = ""
        self._confidence = 0.0
        self._class_index = -1
        self._is_model_loaded = False
        self._current_language = "en"
        self._current_framework = "pytorch"
        self._available_frameworks = []
        self._model_path = None

        # Get DiseaseInfoManager instance
        self._info_manager = DiseaseInfoManager.instance()

        # Connect to language changes
        self._info_manager.language_changed.connect(self._on_language_changed)

        # Thread pool for managing runnables
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(4)

        # Current task
        self.current_task = None

        print(f"InfarenceRunner initialized with {self.thread_pool.maxThreadCount()} threads")

        # Detect available frameworks
        self._detect_frameworks()

    # ============================================
    # Properties
    # ============================================

    @Property(str, notify=disease_name_changed)
    def disease_name(self):
        return self._disease_name

    @Property(str, notify=description_changed)
    def description(self):
        return self._description

    @Property(str, notify=cure_changed)
    def cure(self):
        return self._cure

    @Property(float, notify=confidence_changed)
    def confidence(self):
        return self._confidence

    @Property(int, notify=class_index_changed)
    def class_index(self):
        return self._class_index

    @Property(bool, notify=is_model_loaded_changed)
    def is_model_loaded(self):
        return self._is_model_loaded

    @Property(str, notify=framework_changed)
    def current_framework(self):
        return self._current_framework

    @Property(list, notify=available_frameworks_changed)
    def available_frameworks(self):
        return self._available_frameworks

    # ============================================
    # Private setters
    # ============================================

    def _set_disease_name(self, value):
        if self._disease_name != value:
            self._disease_name = value
            self.disease_name_changed.emit()

    def _set_description(self, value):
        if self._description != value:
            self._description = value
            self.description_changed.emit()

    def _set_cure(self, value):
        if self._cure != value:
            self._cure = value
            self.cure_changed.emit()

    def _set_confidence(self, value):
        if self._confidence != value:
            self._confidence = value
            self.confidence_changed.emit()

    def _set_class_index(self, value):
        if self._class_index != value:
            self._class_index = value
            self.class_index_changed.emit()

    def _clear_results(self):
        """Clear current results"""
        self._set_disease_name("")
        self._set_description("")
        self._set_cure("")
        self._set_confidence(0.0)
        self._set_class_index(-1)

    # ============================================
    # Framework detection
    # ============================================

    def _detect_frameworks(self):
        """Create a task to detect available frameworks"""
        task = InfarenceRunnerTask()
        task.signals.frameworks_detected.connect(self._on_frameworks_detected)
        task.signals.status_message.connect(self.status_message)

        # Run detection (quick task)
        self.thread_pool.start(task)

    def _on_frameworks_detected(self, frameworks):
        """Handle detected frameworks"""
        self._available_frameworks = frameworks
        self.available_frameworks_changed.emit(frameworks)
        print(f"Available frameworks: {frameworks}")

    # ============================================
    # Public methods
    # ============================================

    @Slot(str)
    def set_language(self, language_code):
        """Change the display language"""
        success = self._info_manager.load_language(language_code)
        if success:
            self._current_language = language_code
            self.language_changed.emit(language_code)

            # Refresh current results if any
            if self._class_index >= 0:
                self._update_disease_info(self._class_index)
        return success

    @Slot(str)
    def set_framework(self, framework_name):
        """Set the ML framework to use"""
        framework_name = framework_name.lower()
        if framework_name in self._available_frameworks:
            self._current_framework = framework_name
            self.framework_changed.emit(framework_name)
            print(f"Framework set to: {framework_name}")

            # Reload model with new framework if model is loaded
            if self._model_path and self._is_model_loaded:
                self.load_model(self._model_path)

    @Slot()
    @Slot(str)
    def load_model(self, model_path=None):
        """Load the ML model"""
        if model_path is None:
            model_path = self._find_model_file()

        if not model_path or not os.path.exists(model_path):
            print("Model not found!")
            self._is_model_loaded = False
            self.is_model_loaded_changed.emit()
            self.inference_failed.emit("Model file not found")
            return

        self._model_path = model_path
        self.model_load_started.emit(model_path)

        # Create and configure task
        task = InfarenceRunnerTask()

        # Connect signals
        task.signals.model_load_finished.connect(self._on_model_load_finished)
        task.signals.model_load_failed.connect(self._on_model_load_failed)
        task.signals.status_message.connect(self.status_message)

        # Start loading in thread pool
        task.load_model(model_path, self._current_framework)
        self.thread_pool.start(task)

    def _find_model_file(self):
        """Find model file in standard locations"""
        search_paths = []

        # App data directory
        app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        search_paths.append(os.path.join(app_data, "model.pt"))
        search_paths.append(os.path.join(app_data, "model.pte"))
        search_paths.append(os.path.join(app_data, "model.tflite"))

        # Application directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
        search_paths.append(os.path.join(app_dir, "model.pt"))
        search_paths.append(os.path.join(app_dir, "model.pte"))

        # Resources directory
        search_paths.append(os.path.join(app_dir, "..", "resources", "model.pt"))

        for path in search_paths:
            if os.path.exists(path):
                return path

        return None

    def _on_model_load_finished(self, framework_name, success):
        """Handle model load finished"""
        self._is_model_loaded = success
        self._current_framework = framework_name.lower()
        self.is_model_loaded_changed.emit()
        self.framework_changed.emit(self._current_framework)
        self.model_load_finished.emit(framework_name, success)

        if success:
            print(f"✅ Model loaded with {framework_name}")
        else:
            print(f"❌ Failed to load model with {framework_name}")

    def _on_model_load_failed(self, error, framework_name):
        """Handle model load failed"""
        self._is_model_loaded = False
        self.is_model_loaded_changed.emit()
        self.model_load_failed.emit(error, framework_name)
        self.inference_failed.emit(f"Model load failed: {error}")

    @Slot(str)
    def classify_image(self, image_source):
        """Classify an image from path or base64"""
        if not self._is_model_loaded:
            self.inference_failed.emit("Model not loaded")
            return

        self._clear_results()
        self.inference_started.emit()

        # Create and configure task
        task = InfarenceRunnerTask()

        # Connect signals
        task.signals.inference_finished.connect(self._on_inference_finished)
        task.signals.inference_failed.connect(self._on_inference_failed)
        task.signals.progress_updated.connect(self.progress_updated)
        task.signals.status_message.connect(self.status_message)

        # Set framework (use current)
        task.framework_name = self._current_framework
        task.is_model_loaded = True
        task.framework = None  # Will be loaded from model path?

        # Start inference in thread pool
        task.classify_image(image_source)
        self.thread_pool.start(task)

    @Slot(str)
    def classify_image_from_file(self, file_path):
        """Classify image from file path"""
        if file_path.startswith('file://'):
            file_path = QUrl(file_path).toLocalFile()

        self.classify_image(file_path)

    def _on_inference_finished(self, class_id, confidence, framework_name):
        """Handle inference completion"""
        self._set_confidence(confidence)
        self._set_class_index(class_id)

        # Get disease info from manager
        self._update_disease_info(class_id)

        print(f"Inference completed using {framework_name}")
        self.inference_finished.emit()

    def _on_inference_failed(self, error, framework_name):
        """Handle inference failure"""
        print(f"Inference failed with {framework_name}: {error}")
        self.inference_failed.emit(error)

    def _update_disease_info(self, class_id):
        """Update disease info from manager"""
        info = self._info_manager.get_disease_info(class_id)
        self._set_disease_name(info.name)
        self._set_description(info.description)
        self._set_cure(info.cure)

    @Slot(str)
    def _on_language_changed(self, language):
        """Handle language change from manager"""
        self._current_language = language
        self.language_changed.emit(language)

        # Refresh current results
        if self._class_index >= 0:
            self._update_disease_info(self._class_index)

    # Language management
    def available_languages(self):
        """Get list of available languages"""
        return self._info_manager.available_languages()

    def current_language(self):
        """Get current language"""
        return self._info_manager.current_language()

    # Thread pool management
    def active_thread_count(self):
        """Get number of active threads"""
        return self.thread_pool.activeThreadCount()

    def shutdown(self):
        """Shutdown thread pool gracefully"""
        self.thread_pool.waitForDone()
