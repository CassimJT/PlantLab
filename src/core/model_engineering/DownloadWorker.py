# This Python file uses the following encoding: utf-8
import os
import shutil
import json
from pathlib import Path
from PySide6 import QtCore
from PySide6.QtCore import QObject, Slot, QRunnable, Signal
from huggingface_hub import snapshot_download, hf_hub_download, HfApi
from huggingface_hub.utils import LocalEntryNotFoundError, RepositoryNotFoundError, RevisionNotFoundError
from huggingface_hub import logging as hf_logging
import time

# Disable tqdm progress bars
hf_logging.set_verbosity_error()

class DownloadWorkerSignals(QObject):
    progress = Signal(int)
    finished = Signal(str)
    canceled = Signal(bool)
    error = Signal(str)
    status = Signal(str)
    file_progress = Signal(str, int, int)  # filename, current, total


class DownloadTask(QRunnable):
    """
    QRunnable that performs downloading model in background thread.
    Downloads to: Documents/plantlab/models/model_name/
    """
    def __init__(self, huggingface_id: str, frameworks: list, branch: str, download_path: str = None, commit_hash: str = ""):
        super().__init__()
        self.signals = DownloadWorkerSignals()
        self.hugging_face_id = huggingface_id
        self.frameworks = frameworks
        self.branch = branch
        self.commit_hash = commit_hash
        self._canceled = False
        self._current_download_path = ""

        # Set default download path if none provided
        if not download_path:
            # Default to Documents/plantlab/models
            home = str(Path.home())
            self.download_path = os.path.join(home, "Documents", "plantlab", "models")
        else:
            self.download_path = download_path

        # Create the base directory if it doesn't exist
        os.makedirs(self.download_path, exist_ok=True)
        self.signals.status.emit(f"Base directory: {self.download_path}")

    def cancel(self):
        self._canceled = True
        self.signals.canceled.emit(True)
        # Clean up partial download if exists
        if self._current_download_path and os.path.exists(self._current_download_path):
            try:
                shutil.rmtree(self._current_download_path)
            except:
                pass

    def _progress_callback(self, current, total, filename):
        """Callback for download progress"""
        if self._canceled:
            raise Exception("Download canceled by user")

        progress_percent = int((current / total) * 100) if total > 0 else 0
        self.signals.progress.emit(progress_percent)
        self.signals.file_progress.emit(filename, current, total)
        self.signals.status.emit(f"Downloading {filename}: {progress_percent}%")

    def _get_allow_patterns(self):
        """Get file patterns to include based on selected frameworks"""
        if not self.frameworks or len(self.frameworks) == 0:
            return None  # Download all files

        patterns = []

        # Common patterns for different frameworks
        framework_patterns = {
            "PyTorch": ["*.pt", "*.pth", "*.bin", "pytorch_model.bin", "*.safetensors"],
            "LibTorch": ["*.pt", "*.pth", "*.bin"],
            "TensorFlow": ["*.h5", "*.pb", "*.ckpt.*", "*.index", "saved_model.pb", "tf_model.h5"],
            "OpenCV": ["*.caffemodel", "*.prototxt", "*.weights", "*.cfg", "*.onnx"],
            "ONNX": ["*.onnx", "*.onnx_data"],
            "Executorch": [
                "*.pte",
                "*.pte.*",
                "model.pte",
                "executorch_model.pte",
                "*.pte.pt",
                "*.pte.bin",
                "*.pte.quantized",
                "*.pte.int8",
                "*.pte.fp16",
                "*.pte.int4",
                "*.pte.xnnpack",
                "*.pte.qnnpack",
                "*.pte.vulkan",
                "*.pte.metal",
                "*.pte.coreml",
                "*.pte.mps",
                "*.pte.cuda",
                "*.pte.rocm",
                "*.pte.opencl",
                "*.pte.llama",
                "*.pte.llama2",
                "*.pte.llama3",
                "*.pte.llava",
                "*.pte.mobile",
                "*.pte.embedded",
                "executorch_config.*",
                "*.pte.methods",
                "*.pte.program",
                "*.pte.segments",
                "custom_ops.*",
                "libexecutorch.*",
                "*.pte.json"
            ]
        }

        # If Executorch is selected, also include PyTorch base models
        if "Executorch" in self.frameworks:
            patterns.extend(framework_patterns["PyTorch"])

        # Add patterns for each selected framework
        for framework in self.frameworks:
            if framework in framework_patterns:
                patterns.extend(framework_patterns[framework])

        # Always include essential configuration and documentation files
        patterns.extend([
            "*.json",
            "*.txt",
            "*.model",
            "tokenizer.*",
            "config.*",
            "vocab.*",
            "merges.*",
            "*.yaml",
            "*.yml",
            "README.md",
            "LICENSE",
            "*.md",
            "*.rst"
        ])

        return list(set(patterns))  # Remove duplicates

    def _get_ignore_patterns(self):
        """Get patterns to ignore"""
        ignore_patterns = [
            ".git/*",
            ".gitattributes",
            ".gitignore",
            ".github/*",
            "*.cache",
            "*.tmp",
            "*.temp",
            "*.part",
            "__pycache__/*",
            "*.pyc",
            "*.parquet",
            "*.csv",
            "*.tsv",
            "*.arrow",
            "*.db",
            "*.sqlite",
            "tests/*",
            "test/*",
            "testing/*",
            "examples/*",
            "example/*",
            "docs/*",
            "*.html",
            "*.pdf",
            "checkpoint-*",
            "*.checkpoint",
            "*.log",
            "events.out.tfevents.*",
            "*.profile",
            "*.trace.json"
        ]

        return ignore_patterns

    def _download_with_progress(self, repo_id, **kwargs):
        """Custom download function that emits progress signals"""
        from huggingface_hub import HfFileSystem
        import tempfile

        self.signals.status.emit("Getting file list...")

        # Get list of files to download
        fs = HfFileSystem()
        all_files = fs.glob(f"{repo_id}/**", revision=kwargs.get('revision'))

        # Filter files based on patterns
        if kwargs.get('allow_patterns'):
            import fnmatch
            filtered_files = []
            for file in all_files:
                file_name = file.split('/')[-1]
                for pattern in kwargs['allow_patterns']:
                    if fnmatch.fnmatch(file_name, pattern):
                        filtered_files.append(file)
                        break
            all_files = filtered_files

        if kwargs.get('ignore_patterns'):
            import fnmatch
            filtered_files = []
            for file in all_files:
                file_name = file.split('/')[-1]
                ignore = False
                for pattern in kwargs['ignore_patterns']:
                    if fnmatch.fnmatch(file_name, pattern):
                        ignore = True
                        break
                if not ignore:
                    filtered_files.append(file)
            all_files = filtered_files

        total_files = len(all_files)
        self.signals.status.emit(f"Found {total_files} files to download")

        # Download each file with progress
        downloaded = 0
        for i, file_path in enumerate(all_files):
            if self._canceled:
                raise Exception("Download canceled by user")

            file_name = file_path.split('/')[-1]
            self.signals.status.emit(f"Downloading {file_name}...")

            # Calculate progress
            progress = int((i / total_files) * 100)
            self.signals.progress.emit(progress)

            # Download the file
            try:
                local_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=file_path.replace(f"{repo_id}/", ""),
                    revision=kwargs.get('revision'),
                    local_dir=kwargs.get('local_dir'),
                    local_dir_use_symlinks=kwargs.get('local_dir_use_symlinks', False),
                    resume_download=kwargs.get('resume_download', True)
                )
                downloaded += 1
                self.signals.file_progress.emit(file_name, downloaded, total_files)
            except Exception as e:
                self.signals.status.emit(f"Error downloading {file_name}: {str(e)}")

        # Final progress
        self.signals.progress.emit(100)
        return kwargs.get('local_dir')

    @Slot()
    def run(self):
        """
        Run the download process.
        Downloads to: Documents/plantlab/models/model_name/
        """
        try:
            self.signals.status.emit(f"Starting download of {self.hugging_face_id}...")

            # Determine revision/branch
            revision = None
            if self.commit_hash and self.commit_hash.strip():
                revision = self.commit_hash.strip()
                self.signals.status.emit(f"Using specific commit: {revision}")
            elif self.branch and self.branch.lower() != "latest":
                revision = self.branch.lower()
                self.signals.status.emit(f"Using branch: {revision}")
            else:
                revision = "main"
                self.signals.status.emit(f"Using main branch")

            # Create model-specific folder path INSIDE the download_path
            # Replace / with -- to avoid path issues
            model_name = self.hugging_face_id.replace("/", "--")
            self._current_download_path = os.path.join(self.download_path, model_name)

            # Create the model directory
            os.makedirs(self._current_download_path, exist_ok=True)

            self.signals.status.emit(f"Selected frameworks: {', '.join(self.frameworks) if self.frameworks else 'All'}")
            self.signals.status.emit(f"Downloading to: {self._current_download_path}")

            # Get patterns
            allow_patterns = self._get_allow_patterns()
            ignore_patterns = self._get_ignore_patterns()

            # Emit initial progress
            self.signals.progress.emit(0)

            # Use custom download with progress
            local_path = self._download_with_progress(
                repo_id=self.hugging_face_id,
                revision=revision,
                local_dir=self._current_download_path,
                local_dir_use_symlinks=False,
                resume_download=True,
                ignore_patterns=ignore_patterns,
                allow_patterns=allow_patterns
            )

            # Check if canceled
            if self._canceled:
                self.signals.status.emit("Download canceled")
                self.signals.progress.emit(0)
                return

            # Count downloaded files
            downloaded_files = []
            for root, dirs, files in os.walk(self._current_download_path):
                for file in files:
                    downloaded_files.append(os.path.join(root, file))

            self.signals.status.emit(f"Download completed! {len(downloaded_files)} files downloaded.")
            self.signals.progress.emit(100)
            self.signals.finished.emit(local_path)

        except RepositoryNotFoundError:
            self.signals.error.emit(f"Model '{self.hugging_face_id}' not found on Hugging Face")
        except RevisionNotFoundError:
            self.signals.error.emit(f"Revision '{revision}' not found for model '{self.hugging_face_id}'")
        except Exception as e:
            if self._canceled or "canceled" in str(e).lower():
                self.signals.canceled.emit(True)
                self.signals.status.emit("Download canceled")
                self.signals.progress.emit(0)
            else:
                self.signals.error.emit(f"Download failed: {str(e)}")
        finally:
            try:
                self.signals.progress.disconnect()
                self.signals.finished.disconnect()
                self.signals.canceled.disconnect()
                self.signals.error.disconnect()
                self.signals.status.disconnect()
                self.signals.file_progress.disconnect()
                self.signals.conversion_step.disconnect()
            except:
                pass
