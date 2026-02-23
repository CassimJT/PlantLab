from PySide6.QtWidgets import QFileSystemModel
from PySide6.QtCore import (
    QObject, Slot, Property, Signal,
    QDir, QModelIndex, QTimer, QDirIterator, QFileInfo
)
from PySide6.QtQml import QmlElement


QML_IMPORT_NAME = "com.plantlab.controllers"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class FileSystemController(QObject):
    """
    QFileSystemModel + Image Dataset Controller
    Starts with NULL model - only creates model when user selects a folder
    """

    # =============================
    # Signals
    # =============================
    rootPathChanged = Signal(str)
    directoryLoaded = Signal(str)
    modelReset = Signal()

    imageSelected = Signal(str)
    imageListChanged = Signal()
    currentImageSizeChanged = Signal()
    modelChanged = Signal()  # New signal for when model is created

    # =============================
    # Initialization
    # =============================
    def __init__(self, parent=None):
        super().__init__(parent)

        # Image file extensions
        self._image_filters = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp", "*.gif", "*.svg"]

        # NO MODEL AT START - create only when needed
        self._model = None

        # Image dataset state - completely empty
        self._image_files = []
        self._current_image_index = -1

        # Track if we've loaded a folder yet
        self._current_root_path = ""

        print("FileSystemController initialized - NO MODEL, waiting for user to load folder")

    def _create_model(self):
        """Create the filesystem model (only called when user loads a folder)"""
        if self._model:
            return

        print("Creating QFileSystemModel")
        self._model = QFileSystemModel(self)
        self._model.setFilter(
            QDir.AllDirs |      # Show all directories
            QDir.Files |        # Show files
            QDir.NoDotAndDotDot # Hide . and ..
        )

        # Set name filters to show ONLY image files
        self._model.setNameFilters(self._image_filters)
        self._model.setNameFilterDisables(False)

        self._model.directoryLoaded.connect(self._onDirectoryLoaded)
        self._model.modelReset.connect(self.modelReset)

        # Set initial root path if we have one
        if self._current_root_path:
            self._model.setRootPath(self._current_root_path)

        self.modelChanged.emit()

    # =============================
    # Model Exposure
    # =============================
    @Property(QObject, notify=modelChanged)
    def model(self):
        return self._model

    @Property(str, notify=rootPathChanged)
    def rootPath(self):
        return self._current_root_path

    @Property(QModelIndex, notify=rootPathChanged)
    def rootIndex(self):
        if self._model and self._current_root_path:
            return self._model.index(self._current_root_path)
        return QModelIndex()

    @Property(str, constant=True)
    def homePath(self):
        """Return the user's home directory path"""
        return QDir.homePath()

    # =============================
    # Image Properties
    # =============================
    @Property(str, notify=imageSelected)
    def currentImage(self):
        if 0 <= self._current_image_index < len(self._image_files):
            return self._image_files[self._current_image_index]
        return ""

    @Property(int, notify=imageListChanged)
    def imageCount(self):
        return len(self._image_files)

    @Property(int, notify=imageSelected)
    def currentIndex(self):
        return self._current_image_index

    @Property(str, notify=currentImageSizeChanged)
    def currentImageSize(self):
        """Get formatted file size of current image"""
        if 0 <= self._current_image_index < len(self._image_files):
            path = self._image_files[self._current_image_index]
            try:
                info = QFileInfo(path)
                size = info.size()

                # Format size
                if size < 1024:
                    return f"{size} B"
                elif size < 1024 * 1024:
                    return f"{size / 1024:.1f} KB"
                elif size < 1024 * 1024 * 1024:
                    return f"{size / (1024 * 1024):.1f} MB"
                else:
                    return f"{size / (1024 * 1024 * 1024):.1f} GB"
            except Exception as e:
                print(f"Error getting file size: {e}")
                return ""
        return ""

    # =============================
    # Folder Handling
    # =============================
    @Slot(str)
    def setRootFolder(self, path: str):
        """Set the root folder - creates model if needed"""
        if not path:
            print("Cannot set empty root folder")
            return

        if path.startswith("file://"):
            from PySide6.QtCore import QUrl
            path = QUrl(path).toLocalFile()

        print(f"User loading folder: {path}")

        # Store the path
        self._current_root_path = path

        # Create model if it doesn't exist
        if not self._model:
            self._create_model()
        else:
            # Update existing model
            self._model.setRootPath(path)

        self.rootPathChanged.emit(path)

        # Collect images from this folder
        self._collectImages(path)

    def _clearModel(self):
        """Clear the model and reset all state"""
        # Clear image list
        self._image_files.clear()
        self._current_image_index = -1

        # Clear path
        self._current_root_path = ""

        # Delete model if it exists
        if self._model:
            self._model.deleteLater()
            self._model = None

        # Emit signals to update UI
        self.imageListChanged.emit()
        self.imageSelected.emit("")
        self.currentImageSizeChanged.emit()
        self.rootPathChanged.emit("")
        self.modelChanged.emit()

        print("Model cleared and deleted")

    @Slot()
    def clearImageList(self):
        """Public method to clear the image list and return to drop area"""
        self._clearModel()

    def _collectImages(self, root_path: str):
        """Recursively collect image files and auto-select first"""
        print(f"Collecting images from: {root_path}")

        self._image_files.clear()
        self._current_image_index = -1

        if not root_path or not QDir(root_path).exists():
            print(f"Invalid root path: {root_path}")
            self.imageListChanged.emit()
            return

        iterator = QDirIterator(
            root_path,
            self._image_filters,
            QDir.Files,
            QDirIterator.Subdirectories
        )

        while iterator.hasNext():
            self._image_files.append(iterator.next())

        print(f"Collected {len(self._image_files)} images")

        self.imageListChanged.emit()

        if self._image_files:
            self._current_image_index = 0
            self.imageSelected.emit(self._image_files[0])
            self.currentImageSizeChanged.emit()
        else:
            # No images found - clear preview but keep folder loaded
            self.imageSelected.emit("")
            self.currentImageSizeChanged.emit()
            print("No images found in folder")

    # =============================
    # Image Navigation
    # =============================
    @Slot()
    def nextImage(self):
        if not self._image_files:
            return

        self._current_image_index = (
            (self._current_image_index + 1) % len(self._image_files)
        )

        self.imageSelected.emit(
            self._image_files[self._current_image_index]
        )
        self.currentImageSizeChanged.emit()

    @Slot()
    def previousImage(self):
        if not self._image_files:
            return

        self._current_image_index = (
            (self._current_image_index - 1) % len(self._image_files)
        )

        self.imageSelected.emit(
            self._image_files[self._current_image_index]
        )
        self.currentImageSizeChanged.emit()

    @Slot(str)
    def setCurrentImage(self, path: str):
        """Set image from TreeView click"""
        if path in self._image_files:
            self._current_image_index = self._image_files.index(path)
            self.imageSelected.emit(path)
            self.currentImageSizeChanged.emit()

    # =============================
    # File Model Helpers
    # =============================
    @Slot(str, result=QModelIndex)
    def indexPath(self, path: str):
        if not self._model or not path:
            return QModelIndex()
        return self._model.index(path)

    @Slot(QModelIndex, result=str)
    def filePath(self, index: QModelIndex):
        if not self._model:
            return ""
        return self._model.filePath(index)

    @Slot(QModelIndex, result=str)
    def fileName(self, index: QModelIndex):
        if not self._model:
            return ""
        return self._model.fileName(index)

    @Slot(QModelIndex, result=bool)
    def isDir(self, index: QModelIndex):
        if not self._model:
            return False
        return self._model.isDir(index)

    # =============================
    # Filter Management
    # =============================
    @Slot(str)
    def addImageFilter(self, filter_pattern: str):
        """Add a new image filter pattern (e.g., '*.tiff')"""
        if filter_pattern not in self._image_filters:
            self._image_filters.append(filter_pattern)
            if self._model:
                self._model.setNameFilters(self._image_filters)

    @Slot()
    def resetToImageFilters(self):
        """Reset to default image filters"""
        self._image_filters = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp", "*.gif", "*.svg"]
        if self._model:
            self._model.setNameFilters(self._image_filters)

    # =============================
    # Navigation Helpers
    # =============================
    @Slot()
    def goUp(self):
        """Navigate to parent directory, but stop at /home (don't go to system root)"""
        if not self._model or not self._current_root_path:
            return

        current = self._current_root_path
        home = QDir.homePath()
        print(f"goUp - Current: {current}, Home: {home}")

        # Don't go up if we're already at home
        if current == home:
            print("Already at home, can't go up further")
            return

        # Check if we're in a subdirectory of home
        if current.startswith(home):
            parent = QDir(current)
            if parent.cdUp():
                new_path = parent.absolutePath()
                print(f"Parent path: {new_path}")

                # Only navigate up if we're still within home
                if new_path.startswith(home):
                    print(f"Going up to: {new_path}")
                    self.setRootFolder(new_path)
                else:
                    # This would go above home, so don't allow
                    print("Cannot go above home")
            else:
                print("Already at root?")
        else:
            # If we're outside home for some reason, go to home
            print("Outside home, going to home")
            self.setRootFolder(home)

    @Slot()
    def goHome(self):
        """Navigate to home directory"""
        self.setRootFolder(QDir.homePath())

    @Slot()
    def refresh(self):
        if not self._model or not self._current_root_path:
            return
        current = self._current_root_path
        self._model.setRootPath(current)
        self._collectImages(current)

    # =============================
    # Internal Callbacks
    # =============================
    def _onDirectoryLoaded(self, path: str):
        print(f"Directory loaded: {path}")
        self.directoryLoaded.emit(path)
