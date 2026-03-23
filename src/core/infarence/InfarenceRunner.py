# InfarenceRunner.py
import os
from PySide6.QtCore import QObject, Signal, Slot, Property, QThreadPool
from PySide6.QtCore import QUrl, QStandardPaths

from .DiseaseInfoManager import DiseaseInfoManager, InfoCategory
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
    category_changed = Signal(str)
    model_path_changed = Signal()  # Add this signal for model path changes

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
        self._current_category = "disease"

        # Store loaded framework instance for reuse across threads
        self._loaded_framework = None
        self._loaded_framework_name = None
        self._loaded_model_path = None

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

    @Property(str, notify=category_changed)
    def current_category(self):
        return self._current_category

    @Property(str, notify=model_path_changed)  # Fixed: changed from is_model_loaded_changed to model_path_changed
    def model_loaded_path(self):
        return self._loaded_model_path

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

    def _set_current_category(self, value):
        """Set current category (disease/pest)"""
        if self._current_category != value:
            self._current_category = value
            self.category_changed.emit(value)
            print(f"Category set to: {value}")

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
        print("\n=== Starting Framework Detection ===")

        # Import here to avoid circular imports
        from .frameworks import FrameworkFactory

        # Get all registered frameworks
        all_frameworks = list(FrameworkFactory._frameworks.keys())
        print(f"Registered frameworks: {all_frameworks}")

        # Test each framework directly
        available = []
        main_frameworks = []

        for fw_name in all_frameworks:
            try:
                framework_class = FrameworkFactory._frameworks.get(fw_name)
                if framework_class:
                    print(f"Checking {fw_name}...")
                    is_avail = framework_class.is_available()
                    print(f"  → {fw_name} available: {is_avail}")
                    if is_avail:
                        available.append(fw_name)
                        # Collect main framework names
                        if fw_name in ['pytorch', 'tensorflow', 'opencv', 'executorch']:
                            if fw_name not in main_frameworks:
                                main_frameworks.append(fw_name)
            except Exception as e:
                print(f"  → {fw_name} error: {e}")

        print(f"All detected frameworks: {available}")
        print(f"Main frameworks: {main_frameworks}")
        print("=== End Detection ===\n")

        self._available_frameworks = main_frameworks
        self.available_frameworks_changed.emit(main_frameworks)
        self.frameworks_detected.emit(available)

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

    @Slot(str)
    def set_category(self, category):
        """Set the category (disease or pest)"""
        category = category.lower()
        if category in ["disease", "pest"]:
            self._set_current_category(category)
            # Refresh current results if any
            if self._class_index >= 0:
                self._update_disease_info(self._class_index)

    @Slot(str, str)
    def load_model(self, model_path: str = "", framework: str = ""):
        """Load the ML model for different frameworks"""
        # Handle empty model_path - try to auto-find
        if model_path == "" or model_path is None:
            model_path = self._find_model_file()
            if model_path is None:
                error_msg = "No model file found in standard locations"
                print(error_msg)
                self._is_model_loaded = False
                self.is_model_loaded_changed.emit()
                self.inference_failed.emit(error_msg)
                return

        # Validate model exists
        if not os.path.exists(model_path):
            error_msg = f"Model file not found: {model_path}"
            print(error_msg)
            self._is_model_loaded = False
            self.is_model_loaded_changed.emit()
            self.inference_failed.emit(error_msg)
            return

        # Use current framework if not specified
        if framework == "" or framework is None:
            framework = self._current_framework

        # Store model path for potential reload
        self._model_path = model_path

        # Emit signal that loading is starting
        self.model_load_started.emit(model_path)

        # Create the worker task
        task = InfarenceRunnerTask()

        # Connect signals
        task.signals.model_load_finished.connect(self._on_model_load_finished)
        task.signals.model_load_failed.connect(self._on_model_load_failed)
        task.signals.status_message.connect(self.status_message)

        # Store reference to current task
        self.current_task = task

        # Start loading in thread pool
        task.load_model(model_path, framework)
        self.thread_pool.start(task)

        print(f"Started loading model with framework: {framework} at path: {model_path}")

    def _find_model_file(self):
        """Find model file in standard locations"""
        search_paths = []

        # Get project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../.."))

        # Get user's home directory
        home_dir = os.path.expanduser("~")

        # 1. Your Documents/plantlab/models directory (highest priority)
        documents_models = os.path.join(home_dir, "Documents", "plantlab", "models")
        search_paths.append(os.path.join(documents_models, "model.pt"))
        search_paths.append(os.path.join(documents_models, "model.pte"))
        search_paths.append(os.path.join(documents_models, "model.tflite"))
        search_paths.append(os.path.join(documents_models, "model.onnx"))
        search_paths.append(os.path.join(documents_models, "best.pt"))
        search_paths.append(os.path.join(documents_models, "last.pt"))

        # 2. Plantlab project models directory
        models_dir = os.path.join(project_root, "plantlab", "models")
        search_paths.append(os.path.join(models_dir, "model.pt"))
        search_paths.append(os.path.join(models_dir, "model.pte"))
        search_paths.append(os.path.join(models_dir, "model.tflite"))
        search_paths.append(os.path.join(models_dir, "model.onnx"))

        # 3. App data directory
        app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        search_paths.append(os.path.join(app_data, "model.pt"))
        search_paths.append(os.path.join(app_data, "model.pte"))
        search_paths.append(os.path.join(app_data, "model.tflite"))

        # 4. Infarence directory
        search_paths.append(os.path.join(current_dir, "model.pt"))
        search_paths.append(os.path.join(current_dir, "model.pte"))

        # 5. Resources directory
        search_paths.append(os.path.join(current_dir, "..", "resources", "model.pt"))

        print("\n=== Searching for model in these locations ===")
        for path in search_paths:
            exists = "✓" if os.path.exists(path) else "✗"
            print(f"{exists} {path}")
            if os.path.exists(path):
                print(f"Model found at: {path}")
                return path

        print("No model file found in any location")
        return None

    def _on_model_load_finished(self, framework_name, success):
        """Handle model load finished - store the loaded framework"""
        self._is_model_loaded = success
        self._current_framework = framework_name.lower()

        # Store the loaded framework from the task for reuse
        if success and self.current_task:
            self._loaded_framework = self.current_task.framework
            self._loaded_framework_name = self.current_task.framework_name
            self._loaded_model_path = self.current_task.model_path
            self.model_path_changed.emit()  # Emit the model path changed signal
            print(f"✓ Stored loaded framework: {self._loaded_framework_name}")

        self.is_model_loaded_changed.emit()
        self.framework_changed.emit(self._current_framework)
        self.model_load_finished.emit(framework_name, success)

        if success:
            print(f"Model loaded with {framework_name}")
        else:
            print(f"Failed to load model with {framework_name}")

    def _on_model_load_failed(self, error, framework_name):
        """Handle model load failed"""
        self._is_model_loaded = False
        self._loaded_framework = None
        self._loaded_framework_name = None
        self._loaded_model_path = None
        self.model_path_changed.emit()  # Emit the model path changed signal
        self.is_model_loaded_changed.emit()
        self.model_load_failed.emit(error, framework_name)
        self.inference_failed.emit(f"Model load failed: {error}")

    @Slot(str)
    def classify_image(self, image_source):
        """Classify an image from path or base64"""
        # Use the stored loaded framework instance
        if not self._is_model_loaded or self._loaded_framework is None:
            self.inference_failed.emit("Model not loaded")
            return

        self._clear_results()
        self.inference_started.emit()

        # Create inference task
        task = InfarenceRunnerTask()

        # Pass the already loaded framework to the inference task
        task.framework = self._loaded_framework
        task.framework_name = self._loaded_framework_name
        task.is_model_loaded = True

        # Connect signals
        task.signals.inference_finished.connect(self._on_inference_finished)
        task.signals.inference_failed.connect(self._on_inference_failed)
        task.signals.progress_updated.connect(self.progress_updated)
        task.signals.status_message.connect(self.status_message)

        # Start inference in thread pool
        task.classify_image(image_source)
        self.thread_pool.start(task)

    @Slot(str)
    # InfarenceRunner.py - Fix classify_image_from_file method

    @Slot(str)
    def classify_image_from_file(self, file_path):
        """Classify image from file path"""
        print(f"Original file_path: {file_path}")

        # Handle different URL formats
        if file_path.startswith('file://'):
            # Convert file:// URL to local path
            file_path = QUrl(file_path).toLocalFile()
        elif file_path.startswith('qrc://') or file_path.startswith(':/'):
            # Handle Qt resource paths
            file_path = file_path
        else:
            # It might already be a local path
            file_path = file_path

        print(f"Converted file_path: {file_path}")

        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File does not exist: {file_path}")
            self.inference_failed.emit(f"File does not exist: {file_path}")
            return

        # Call classify_image with the correct path
        self.classify_image(file_path)

    def _on_inference_finished(self, class_id, confidence, framework_name):
        """Handle inference completion"""
        self._set_confidence(confidence)
        self._set_class_index(class_id)

        # Get disease/pest info from manager based on current category
        self._update_disease_info(class_id)

        print(f"Inference completed using {framework_name}")
        self.inference_finished.emit()

    def _on_inference_failed(self, error, framework_name):
        """Handle inference failure"""
        print(f"Inference failed with {framework_name}: {error}")
        self.inference_failed.emit(error)

    def _update_disease_info(self, class_id):
        """Update disease/pest info from manager based on current category"""
        if self._current_category == "disease":
            info = self._info_manager.get_disease_info(class_id)
        else:
            info = self._info_manager.get_pest_info(class_id)

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

    # Category management
    def available_categories(self):
        """Get list of available categories"""
        return ["disease", "pest"]

    def get_category_stats(self):
        """Get statistics about loaded categories"""
        return self._info_manager.get_category_stats()

    # Thread pool management
    def active_thread_count(self):
        """Get number of active threads"""
        return self.thread_pool.activeThreadCount()

    def shutdown(self):
        """Shutdown thread pool gracefully"""
        self.thread_pool.waitForDone()