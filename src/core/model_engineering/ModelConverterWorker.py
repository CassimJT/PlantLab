# This Python file uses the following encoding: utf-8
from PySide6 import QtCore
from pathlib import Path
import os
import torch
from PySide6.QtCore import QObject, Slot, QRunnable, Signal

class ModelConverterSignal(QtCore.QObject):
    progress = Signal(int)
    finished = Signal(str)
    canceled = Signal(bool)
    error = Signal(str)
    status = Signal(str)
    file_progress = Signal(str, int, int)  # filename, current, total
    conversion_step = Signal(str)  # Current conversion step

class ModelConverterTask(QRunnable):
    def __init__(self, model_path: str, from_framework: str, to_framework: str, save_path: str):
        super().__init__()
        self.signals = ModelConverterSignal()
        self.model_path = model_path
        self.from_framework = from_framework
        self.to_framework = to_framework
        self.save_path = save_path
        self._canceled = False
        self._current_save_path = ""

        # Set default save path if none provided
        if not save_path:
            # Default to Documents/plantlab/models
            home = str(Path.home())
            self.save_path = os.path.join(home, "Documents", "plantlab", "models")

        # Create the base directory if it doesn't exist
        os.makedirs(self.save_path, exist_ok=True)
        self.signals.status.emit(f"Base directory: {self.save_path}")

    def cancel(self):
        self._canceled = True
        self.signals.canceled.emit(True)

    def _convert_to_onnx(self, model, example_input, model_name):
        """Convert PyTorch model to ONNX format"""
        self.signals.conversion_step.emit("Exporting to ONNX...")
        onnx_path = os.path.join(self.save_path, f"{model_name}.onnx")

        torch.onnx.export(
            model,
            example_input,
            onnx_path,
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={'input': {0: 'batch_size'},
                         'output': {0: 'batch_size'}}
        )
        return onnx_path

    def _convert_to_torchscript(self, model, example_input, model_name):
        """Convert PyTorch model to TorchScript (LibTorch compatible)"""
        self.signals.conversion_step.emit("Tracing model for TorchScript...")

        # Use tracing for LibTorch compatibility
        traced_model = torch.jit.trace(model, example_input)
        ts_path = os.path.join(self.save_path, f"{model_name}_traced.pt")
        traced_model.save(ts_path)

        return ts_path

    def _convert_to_executorch(self, model, example_input, model_name):
        """Convert PyTorch model to ExecuTorch format (.pte)"""
        self.signals.conversion_step.emit("Exporting to ExecuTorch...")

        try:
            # Check if executorch is available
            import executorch.exir as exir

            # Export to ExecuTorch format
            pte_path = os.path.join(self.save_path, f"{model_name}.pte")

            # Basic ExecuTorch export
            exported_program = exir.capture(
                model,
                example_input,
                exir.CaptureConfig()
            ).to_edge(
                exir.EdgeCompileConfig()
            ).to_executorch()

            # Save the .pte file
            with open(pte_path, "wb") as f:
                f.write(exported_program.buffer)

            return pte_path

        except ImportError:
            self.signals.error.emit("Executorch package not installed. Run: pip install executorch")
            return None

    def _convert_to_tensorflow(self, model, example_input, model_name):
        """Convert PyTorch model to TensorFlow format"""
        self.signals.conversion_step.emit("Converting to TensorFlow (requires onnx-tf)...")

        try:
            import onnx
            import onnx_tf

            # First convert to ONNX
            temp_onnx = os.path.join(self.save_path, f"{model_name}_temp.onnx")
            torch.onnx.export(
                model, example_input, temp_onnx,
                opset_version=11
            )

            # Then convert ONNX to TensorFlow
            onnx_model = onnx.load(temp_onnx)
            tf_rep = onnx_tf.backend.prepare(onnx_model)

            # Save TensorFlow model
            tf_path = os.path.join(self.save_path, f"{model_name}_tf")
            tf_rep.export_graph(tf_path)

            # Clean up temp file
            os.remove(temp_onnx)

            return tf_path

        except ImportError:
            self.signals.error.emit("onnx-tf not installed. Run: pip install onnx onnx-tf")
            return None

    @Slot()
    def run(self):
        try:
            self.signals.status.emit(f"Starting conversion from {self.from_framework} to {self.to_framework}")
            self.signals.progress.emit(10)

            if self._canceled:
                return

            # Check if model file exists
            if not os.path.exists(self.model_path):
                self.signals.error.emit(f"Model file not found: {self.model_path}")
                return

            # Load model based on source framework
            self.signals.conversion_step.emit(f"Loading {self.from_framework} model...")

            if self.from_framework.lower() == "pytorch":
                # Load PyTorch model
                if self.model_path.endswith('.pt') or self.model_path.endswith('.pth'):
                    try:
                        # Try loading with torch.jit first (for traced models)
                        model = torch.jit.load(self.model_path)
                        model.eval()
                    except:
                        # Fall back to regular PyTorch load
                        model = torch.load(self.model_path, map_location='cpu')
                        if isinstance(model, dict):
                            # Handle checkpoint files
                            self.signals.error.emit("Checkpoint file detected. Please provide a full model file (.pt)")
                            return
                        model.eval()
                else:
                    self.signals.error.emit("Unsupported PyTorch file format")
                    return
            else:
                self.signals.error.emit(f"Source framework {self.from_framework} not yet supported")
                return

            self.signals.progress.emit(30)

            if self._canceled:
                return

            # Generate example input based on model type
            self.signals.conversion_step.emit("Generating example input...")

            # Try to infer input shape (simplified - you may need more sophisticated detection)
            example_input = torch.randn(1, 3, 224, 224)  # Default for image models

            # If model has specific input requirements, try to detect
            if hasattr(model, 'example_inputs') and model.example_inputs:
                example_input = model.example_inputs
            elif hasattr(model, 'dummy_inputs') and model.dummy_inputs:
                example_input = model.dummy_inputs

            self.signals.progress.emit(50)

            if self._canceled:
                return

            # Convert based on target framework
            model_name = Path(self.model_path).stem
            output_path = None

            self.signals.conversion_step.emit(f"Converting to {self.to_framework}...")

            if self.to_framework.lower() == "onnx":
                output_path = self._convert_to_onnx(model, example_input, model_name)

            elif self.to_framework.lower() == "libtorch":
                output_path = self._convert_to_torchscript(model, example_input, model_name)

            elif self.to_framework.lower() == "executorch":
                output_path = self._convert_to_executorch(model, example_input, model_name)

            elif self.to_framework.lower() == "tensorflow":
                output_path = self._convert_to_tensorflow(model, example_input, model_name)

            elif self.to_framework.lower() == "opencv":
                # OpenCV uses ONNX format
                self.signals.conversion_step.emit("Converting to ONNX for OpenCV...")
                onnx_path = self._convert_to_onnx(model, example_input, model_name)
                output_path = onnx_path
                self.signals.status.emit("ONNX model ready for OpenCV DNN module")

            else:
                self.signals.error.emit(f"Target framework {self.to_framework} not supported")
                return

            self.signals.progress.emit(90)

            if self._canceled:
                return

            if output_path:
                self.signals.status.emit(f"Conversion completed successfully!")
                self.signals.conversion_step.emit("Conversion complete")
                self.signals.progress.emit(100)
                self.signals.finished.emit(output_path)
            else:
                self.signals.error.emit("Conversion failed - no output generated")

        except Exception as e:
            self.signals.error.emit(f"Conversion failed: {str(e)}")
            self.signals.progress.emit(0)
