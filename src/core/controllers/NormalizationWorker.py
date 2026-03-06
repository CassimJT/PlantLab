import os
import cv2
import numpy as np
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QRunnable, Slot


class NormalizationWorkerSignals(QObject):
    """Helper class to define signals used by the worker"""
    progress = Signal(int)              # current progress (0 to total)
    finished = Signal()                 # all done successfully
    error = Signal(str)                  # error message
    canceled = Signal()                  # user canceled
    # ADD THIS LINE
    result = Signal(dict)                 # summary of results


class NormalizationTask(QRunnable):
    """
    QRunnable that performs image normalization in background thread(s).
    One task = process all images in the folder (you can later split per image if desired).
    """
    def __init__(self,
                 input_dir: str,
                 output_dir: str,
                 target_size: int,
                 grayscale: bool,
                 norm_type: str,
                 image_extensions: list = None):
        super().__init__()
        self.signals = NormalizationWorkerSignals()

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.target_size = target_size
        self.grayscale = grayscale
        self.norm_type = norm_type
        self.image_extensions = image_extensions or [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

        self._canceled = False

    def cancel(self):
        self._canceled = True

    @Slot()
    def run(self):
        try:
            # Collect all image paths
            image_paths = []
            for root, _, files in os.walk(self.input_dir):
                for file in files:
                    if Path(file).suffix.lower() in self.image_extensions:
                        image_paths.append(os.path.join(root, file))

            total = len(image_paths)
            if total == 0:
                self.signals.error.emit("No images found in directory")
                return

            self.signals.progress.emit(0)

            # ADD THESE VARIABLES for tracking
            successful = 0
            failed = 0
            failed_paths = []

            for idx, img_path in enumerate(image_paths, 1):
                if self._canceled:
                    self.signals.canceled.emit()
                    return

                result = self._normalize_single_image(img_path)
                if result["success"]:
                    successful += 1
                else:
                    failed += 1
                    failed_paths.append({
                        "path": img_path,
                        "error": result.get("error", "Unknown error")
                    })

                # Report progress
                self.signals.progress.emit(idx)

            # ADD THIS SECTION: Emit summary
            summary = {
                "total": total,
                "successful": successful,
                "failed": failed,
                "failed_paths": failed_paths,
                "output_dir": self.output_dir,
                "input_dir": self.input_dir
            }
            self.signals.result.emit(summary)
            self.signals.finished.emit()

        except Exception as e:
            self.signals.error.emit(str(e))

    def _normalize_single_image(self, image_path: str) -> dict:
        try:
            # Read image
            if self.grayscale:
                img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    return {"success": False, "error": "Failed to read image"}
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            else:
                img = cv2.imread(image_path, cv2.IMREAD_COLOR)
                if img is None:
                    return {"success": False, "error": "Failed to read image"}

            # Resize with aspect ratio preserved
            h, w = img.shape[:2]
            scale = min(self.target_size / h, self.target_size / w)
            new_h, new_w = int(h * scale), int(w * scale)
            resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

            # Create square canvas
            canvas = np.zeros((self.target_size, self.target_size, 3), dtype=np.uint8)
            y_offset = (self.target_size - new_h) // 2
            x_offset = (self.target_size - new_w) // 2
            canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized

            # RGB for normalization
            canvas_rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)

            # Apply chosen normalization
            if self.norm_type == "Scale (0-1)":
                normalized = canvas_rgb.astype(np.float32) / 255.0
            elif self.norm_type == "Standardize (mean=0, std=1)":
                normalized = canvas_rgb.astype(np.float32) / 255.0
                mean = np.mean(normalized)
                std = np.std(normalized)
                if std > 0:
                    normalized = (normalized - mean) / std
                else:
                    normalized = normalized - mean
            else:  # "None (0-255)"
                normalized = canvas_rgb.astype(np.float32)

            # Prepare output path (preserve subfolder structure)
            rel_path = os.path.relpath(image_path, self.input_dir)
            rel_path = os.path.splitext(rel_path)[0] + ".png"
            output_path = os.path.join(self.output_dir, rel_path)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Convert back for saving
            if normalized.dtype != np.uint8:
                if self.norm_type != "None (0-255)":
                    saved_img = (normalized * 255).clip(0, 255).astype(np.uint8)
                else:
                    saved_img = normalized.astype(np.uint8)
            else:
                saved_img = normalized

            saved_img_bgr = cv2.cvtColor(saved_img, cv2.COLOR_RGB2BGR)
            success = cv2.imwrite(output_path, saved_img_bgr, [cv2.IMWRITE_PNG_COMPRESSION, 3])

            return {
                "success": success,
                "path": output_path if success else None,
                "original": image_path
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
