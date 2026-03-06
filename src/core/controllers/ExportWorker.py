import os
import csv
import json
import cv2
from PySide6.QtCore import QObject, Signal, QRunnable, Slot, QDateTime


class ExportWorkerSignals(QObject):
    """Signals for the export worker"""
    progress = Signal(int)          # 0-100 progress (percentage)
    finished = Signal(str)          # Emits the output file path
    error = Signal(str)             # Error message
    status = Signal(str)            # Status updates (scanning, writing, etc.)
    file_found = Signal(int)        # Number of files found (to set progress range)


class ExportTask(QRunnable):
    """
    QRunnable that performs dataset export in background thread.
    """
    def __init__(self, export_format: str, target_dir: str):
        super().__init__()
        self.signals = ExportWorkerSignals()
        self.format = export_format
        self.target_dir = target_dir
        self._canceled = False

    def cancel(self):
        self._canceled = True

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    @Slot()
    def run(self):
        try:
            self.signals.status.emit(f"Scanning for PNG files in {self.target_dir}...")

            # ── Phase 0: Count total PNG files ───────────────────────────────
            total_files = 0
            for root, _, files in os.walk(self.target_dir):
                if self._canceled:
                    return
                for file in files:
                    if file.lower().endswith('.png'):
                        total_files += 1

            if total_files == 0:
                self.signals.error.emit(f"No PNG files found in {self.target_dir}")
                return

            self.signals.file_found.emit(total_files)
            self.signals.status.emit(f"Found {total_files} images. Collecting metadata...")
            self.signals.progress.emit(0)

            # Decide how much of the progress bar metadata collection should take
            # JSON writing is very fast   → metadata gets most of the bar
            # CSV writing takes longer    → more balanced split
            if self.format == "JSON":
                metadata_weight = 92      # almost full bar during heavy metadata phase
            else:
                metadata_weight = 45      # leave ~55% for CSV writing

            # ── Phase 1: Collect metadata (the slow part) ─────────────────────
            image_files = []
            processed = 0
            update_interval_meta = max(1, total_files // 80)   # ~80 updates max

            for root, _, files in os.walk(self.target_dir):
                if self._canceled:
                    return
                for file in files:
                    if self._canceled:
                        return
                    if file.lower().endswith('.png'):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, self.target_dir)

                        img = cv2.imread(full_path)
                        if img is not None:
                            h, w = img.shape[:2]
                            channels = img.shape[2] if len(img.shape) > 2 else 1
                        else:
                            w, h, channels = 0, 0, 0

                        file_size_bytes = os.path.getsize(full_path)
                        size_str = self._format_file_size(file_size_bytes)

                        image_files.append({
                            "path": full_path,
                            "rel_path": rel_path,
                            "filename": file,
                            "folder": os.path.basename(os.path.dirname(full_path)),
                            "size": size_str,
                            "size_bytes": file_size_bytes,
                            "width": w,
                            "height": h,
                            "channels": channels
                        })

                        processed += 1

                        # Update progress less frequently to reduce signal spam
                        if processed % update_interval_meta == 0 or processed == total_files:
                            progress = int((processed / total_files) * metadata_weight)
                            self.signals.progress.emit(progress)
                            self.signals.status.emit(f"Collected metadata for {processed}/{total_files} images")

            if self._canceled:
                return

            self.signals.status.emit(f"Generating {self.format} file...")
            self.signals.progress.emit(metadata_weight)  # small visual step before writing

            # ── Phase 2: Write output file ────────────────────────────────────
            timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
            folder_name = os.path.basename(self.target_dir)
            output_path = None

            update_interval_write = max(1, total_files // 60)  # aim for ~60 updates during write

            if self.format == "CSV with paths":
                filename = f"{folder_name}_paths_{timestamp}.csv"
                output_path = os.path.join(self.target_dir, filename)
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['absolute_path', 'relative_path', 'filename', 'folder', 'file_size'])

                    for i, img in enumerate(image_files):
                        if self._canceled:
                            return
                        writer.writerow([
                            img['path'],
                            img['rel_path'],
                            img['filename'],
                            img['folder'],
                            img['size']
                        ])
                        if (i + 1) % update_interval_write == 0 or (i + 1) == total_files:
                            progress = metadata_weight + int(((i + 1) / total_files) * (100 - metadata_weight))
                            self.signals.progress.emit(progress)

            elif self.format == "CSV with metadata":
                filename = f"{folder_name}_metadata_{timestamp}.csv"
                output_path = os.path.join(self.target_dir, filename)
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['filename', 'folder', 'width', 'height', 'channels', 'file_size', 'file_format'])

                    for i, img in enumerate(image_files):
                        if self._canceled:
                            return
                        writer.writerow([
                            img['filename'],
                            img['folder'],
                            img['width'],
                            img['height'],
                            img['channels'],
                            img['size'],
                            'PNG'
                        ])
                        if (i + 1) % update_interval_write == 0 or (i + 1) == total_files:
                            progress = metadata_weight + int(((i + 1) / total_files) * (100 - metadata_weight))
                            self.signals.progress.emit(progress)

            elif self.format == "JSON":
                filename = f"{folder_name}_dataset_{timestamp}.json"
                output_path = os.path.join(self.target_dir, filename)

                dataset_info = {
                    "name": folder_name,
                    "total_images": total_files,
                    "format": "PNG",
                    "export_date": QDateTime.currentDateTime().toString(),
                    "images": image_files
                }

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(dataset_info, f, indent=2, ensure_ascii=False)

                # JSON write is fast → just jump to 100%
                self.signals.progress.emit(100)

            if output_path and not self._canceled:
                self.signals.status.emit(f"Export complete: {os.path.basename(output_path)}")
                self.signals.finished.emit(output_path)

        except Exception as e:
            self.signals.error.emit(f"Export failed: {str(e)}")
