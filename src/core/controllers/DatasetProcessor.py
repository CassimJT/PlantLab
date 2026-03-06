import os
from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
    Property,
    QDir,
    QDirIterator,
    QThreadPool,
    QDateTime,
    QFileInfo
)

# Import OpenCV
import cv2

# Import the workers
from src.core.controllers.NormalizationWorker import NormalizationTask
from src.core.controllers.ExportWorker import ExportTask


class DatasetProcessor(QObject):
    # ─── Processing signals ───────────────────────────────────────
    normalizationStarted = Signal(str)
    normalizationProgress = Signal(int)
    normalizationCompleted = Signal(str)
    normalizationFailed = Signal(str)
    normalizationCanceled = Signal()
    normalizationResult = Signal(dict)

    # ─── Export signals ──────────────────────────────────────────────
    exportStarted = Signal(str, str)
    exportProgress = Signal(int)
    exportCompleted = Signal(str)
    exportFailed = Signal(str)
    exportStatus = Signal(str)           # New signal for status updates
    csvWithPathsGenerated = Signal(str)
    csvWithMetadataGenerated = Signal(str)
    jsonGenerated = Signal(str)

    # ─── Properties ───────────────────────────────────────────────
    isProcessingChanged = Signal()
    progressValueChanged = Signal()
    totalImagesToProcessChanged = Signal()

    def __init__(self, fileSystemController=None, parent=None):
        super().__init__(parent)
        self._is_processing = False
        self._progress_value = 0
        self._total_images = 0
        self._default_save_path = QDir.homePath() + "/Documents/plantlab"
        self._file_system_controller = fileSystemController

        self._normalization_task = None    # keep reference to cancel if needed
        self._export_task = None            # keep reference to cancel if needed
        self._current_input_dir = ""
        self._last_normalized_folder = ""    # Store the last normalized folder path
        self._last_normalized_folder_name = ""  # Store just the folder name

        print(f"DatasetProcessor initialized with OpenCV version: {cv2.__version__}")
        print(f"Default save path: {self._default_save_path}")

    # ─── Properties ───────────────────────────────────────────────
    @Property(bool, notify=isProcessingChanged)
    def isProcessing(self):
        return self._is_processing

    @Property(int, notify=progressValueChanged)
    def progressValue(self):
        return self._progress_value

    @Property(int, notify=totalImagesToProcessChanged)
    def totalImagesToProcess(self):
        return self._total_images

    def _set_is_processing(self, value: bool):
        if self._is_processing != value:
            self._is_processing = value
            self.isProcessingChanged.emit()

    def _set_progress_value(self, value: int):
        if self._progress_value != value:
            self._progress_value = value
            self.progressValueChanged.emit()

    def _set_total_images(self, value: int):
        if self._total_images != value:
            self._total_images = value
            self.totalImagesToProcessChanged.emit()

    # ─── Helper: count images ─────────────────────────────────────
    def _count_images_in_directory(self, path: str) -> int:
        if self._file_system_controller:
            return self._file_system_controller.countImagesInDirectory(path)
        # fallback
        count = 0
        iterator = QDirIterator(path, ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"],
                                QDir.Files, QDirIterator.Subdirectories)
        while iterator.hasNext():
            iterator.next()
            count += 1
        return count

    # ─── Helper: get all image paths ─────────────────────────────
    def _get_all_image_paths(self, path: str) -> list:
        if self._file_system_controller:
            return self._file_system_controller.getImagePaths(path)
        # fallback
        image_paths = []
        iterator = QDirIterator(path, ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"],
                                QDir.Files, QDirIterator.Subdirectories)
        while iterator.hasNext():
            image_paths.append(iterator.next())
        return image_paths

    # ─── Public slot: start normalization ─────────────────────────
    @Slot(int, bool, str, str, str)
    def applyNormalization(self, targetSize: int, grayscale: bool, normalization: str,
                           dirPath: str, fileName: str):
        if self._is_processing:
            self.normalizationFailed.emit("Already processing")
            return

        total = self._count_images_in_directory(dirPath)
        if total == 0:
            self.normalizationFailed.emit("No images found in the selected directory")
            return

        self._current_input_dir = dirPath
        self._set_is_processing(True)
        self._set_total_images(total)
        self._set_progress_value(0)

        # Emit initial progress to set QML progress bar to 0
        self.normalizationProgress.emit(0)

        output_dir = os.path.join(self._default_save_path, fileName)
        os.makedirs(output_dir, exist_ok=True)

        # Store the last normalized folder for export
        self._last_normalized_folder = output_dir
        self._last_normalized_folder_name = fileName

        self.normalizationStarted.emit(f"Starting normalization of {total} images...")

        # Create and start task
        self._normalization_task = NormalizationTask(
            input_dir=dirPath,
            output_dir=output_dir,
            target_size=targetSize,
            grayscale=grayscale,
            norm_type=normalization
        )

        # Connect signals
        self._normalization_task.signals.progress.connect(self._on_normalization_progress)
        self._normalization_task.signals.finished.connect(self._on_normalization_finished)
        self._normalization_task.signals.error.connect(self._on_normalization_error)
        self._normalization_task.signals.canceled.connect(self._on_normalization_canceled)
        self._normalization_task.signals.result.connect(self._on_normalization_result)

        QThreadPool.globalInstance().start(self._normalization_task)

    @Slot()
    def cancelProcessing(self):
        """Cancel current processing operation"""
        print("Cancel requested")
        if self._normalization_task:
            print("Canceling normalization task")
            self._normalization_task.cancel()
            self._normalization_task = None
            self.normalizationCanceled.emit()

        if self._export_task:
            print("Canceling export task")
            self._export_task.cancel()
            self._export_task = None
            self.exportFailed.emit("Export canceled")

        # Force state reset
        self._set_is_processing(False)
        self._set_progress_value(0)
        self._set_total_images(0)

    # ─── Methods to get last normalized folder ────────────────────
    @Slot(result=str)
    def getLastNormalizedFolder(self):
        """Return the path of the last normalized folder"""
        return self._last_normalized_folder

    @Slot(result=str)
    def getLastNormalizedFolderName(self):
        """Return the name of the last normalized folder"""
        return self._last_normalized_folder_name

    # ─── Method to set a custom folder for export ─────────────────
    @Slot(str)
    def setExportFolder(self, folderPath: str):
        """Set a custom folder path to export from"""
        if os.path.exists(folderPath) and os.path.isdir(folderPath):
            self._last_normalized_folder = folderPath
            self._last_normalized_folder_name = os.path.basename(folderPath)
            print(f"Export folder set to: {folderPath}")
        else:
            print(f"Invalid folder path: {folderPath}")

    # ─── Normalization internal handlers ──────────────────────────
    def _on_normalization_progress(self, value: int):
        self._set_progress_value(value)
        self.normalizationProgress.emit(value)

    def _on_normalization_finished(self):
        self._set_is_processing(False)
        self._normalization_task = None

    def _on_normalization_result(self, summary: dict):
        """Handle the result summary from the worker"""
        self.normalizationCompleted.emit(
            f"Processed {summary['successful']} of {summary['total']} images successfully"
        )
        if summary['failed'] > 0:
            print(f"Failed to process {summary['failed']} images")
            for failed in summary['failed_paths']:
                print(f"  - {failed['path']}: {failed['error']}")
        self.normalizationResult.emit(summary)

    def _on_normalization_error(self, msg: str):
        self._set_is_processing(False)
        self._normalization_task = None
        self.normalizationFailed.emit(msg)

    def _on_normalization_canceled(self):
        self._set_is_processing(False)
        self._normalization_task = None
        self.normalizationCanceled.emit()

    # ─── Export methods ───────────────────────────────────────────
    @Slot(str, str)
    def exportDataset(self, format: str, folderPath: str):
        """Export dataset in specified format from the given folder path"""
        if self._is_processing:
            self.exportFailed.emit("Already processing")
            return

        # Resolve target directory
        target_dir = folderPath
        if not os.path.isabs(target_dir):
            target_dir = os.path.join(self._default_save_path, target_dir)
        target_dir = os.path.normpath(target_dir)

        if not os.path.exists(target_dir):
            self.exportFailed.emit(f"Directory does not exist: {target_dir}")
            return

        self._set_is_processing(True)
        self._set_progress_value(0)
        self.exportProgress.emit(0)
        self.exportStarted.emit(format, target_dir)

        # Create and start export task
        self._export_task = ExportTask(format, target_dir)

        # Connect signals
        self._export_task.signals.progress.connect(self._on_export_progress)
        self._export_task.signals.finished.connect(self._on_export_finished)
        self._export_task.signals.error.connect(self._on_export_error)
        self._export_task.signals.status.connect(self._on_export_status)
        self._export_task.signals.file_found.connect(self._on_export_files_found)

        QThreadPool.globalInstance().start(self._export_task)
    def _on_export_progress(self, value: int):
        """Handle progress updates from export worker"""
        print(f"Export progress: {value}%")  # Debug
        self._set_progress_value(value)
        self.exportProgress.emit(value)

    def _on_export_files_found(self, total: int):
        """Set the total images for the progress bar"""
        print(f"📊 Export files found: {total}")  # Debug
        self._set_total_images(total)  # Keep this as the actual count (54305)
        self.exportStatus.emit(f"Found {total} images to export")
        self._set_progress_value(0)
        self.exportProgress.emit(0)

    def _on_export_finished(self, output_path: str):
        self._set_is_processing(False)
        self._set_progress_value(0)
        self._export_task = None

        # Emit the appropriate signal based on file extension and content
        filename = os.path.basename(output_path)
        if filename.endswith('.csv'):
            if 'paths' in filename:
                self.csvWithPathsGenerated.emit(output_path)
            else:
                self.csvWithMetadataGenerated.emit(output_path)
        elif filename.endswith('.json'):
            self.jsonGenerated.emit(output_path)

        self.exportCompleted.emit(f"Export completed: {filename}")

    def _on_export_error(self, error_msg: str):
        self._set_is_processing(False)
        self._set_progress_value(0)
        self._export_task = None
        self.exportFailed.emit(error_msg)

    def _on_export_status(self, status_msg: str):
        """Handle status updates from export worker"""
        print(f"Export status: {status_msg}")
        self.exportStatus.emit(status_msg)

    @Slot()
    def cancelExport(self):
        """Cancel the current export operation"""
        if self._export_task:
            self._export_task.cancel()
            self._export_task = None
            self._set_is_processing(False)
            self.exportFailed.emit("Export canceled")

    @Slot(result=str)
    def getDefaultExportPath(self):
        """Get default export path"""
        return self._default_save_path

    @Slot(result='QVariantList')
    def listNormalizedFolders(self):
        """List all folders in the default save path that might contain normalized images"""
        folders = []
        try:
            if os.path.exists(self._default_save_path):
                for item in os.listdir(self._default_save_path):
                    item_path = os.path.join(self._default_save_path, item)
                    if os.path.isdir(item_path):
                        # Check if it contains PNG files
                        has_png = False
                        for root, _, files in os.walk(item_path):
                            if any(f.lower().endswith('.png') for f in files):
                                has_png = True
                                break
                        if has_png:
                            folders.append({
                                "name": item,
                                "path": item_path,
                                "modified": QDateTime.fromSecsSinceEpoch(int(os.path.getmtime(item_path))).toString()
                            })
        except Exception as e:
            print(f"Error listing folders: {e}")
        return folders
