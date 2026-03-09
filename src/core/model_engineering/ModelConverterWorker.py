# This Python file uses the following encoding: utf-8
from PySide6 import QtCore
from pathlib import Path
import os
import tf2onnx
import tensorflow as tf
import onnx
import torch
import executorch
import shutil
from pathlib import Path
import traceback
from PySide6.QtCore import QObject, Slot, QRunnable, Signal

# Try importing ultralytics for YOLO model support
try:
    from ultralytics import YOLO
    import ultralytics.nn.tasks
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False


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
        self.setAutoDelete(False)  # Manage worker lifecycle manually

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

    def _load_pytorch_model(self, model_path):
        """Load PyTorch model with support for YOLO/Ultralytics and regular models"""
        self.signals.conversion_step.emit("Loading PyTorch model...")

        # Try loading as YOLO model first if ultralytics is available
        if ULTRALYTICS_AVAILABLE and (model_path.endswith('.pt') or model_path.endswith('.pth')):
            try:
                self.signals.status.emit("Attempting to load as YOLO model...")
                yolo_model = YOLO(model_path)
                # Extract the underlying PyTorch model
                if hasattr(yolo_model, 'model'):
                    model = yolo_model.model
                    model.eval()
                    self.signals.status.emit("Successfully loaded YOLO model")
                    return model
            except Exception as e:
                self.signals.status.emit(f"Not a YOLO model or failed to load: {str(e)}")

        # Try loading with torch.jit first (for traced models)
        try:
            self.signals.status.emit("Attempting to load as TorchScript model...")
            model = torch.jit.load(model_path, map_location='cpu')
            model.eval()
            self.signals.status.emit("Successfully loaded TorchScript model")
            return model
        except Exception:
            pass

        # Try loading with weights_only=False for regular PyTorch models
        # This is safe because user selected the file locally
        try:
            self.signals.status.emit("Attempting to load as regular PyTorch model...")
            # Use weights_only=False for custom classes like YOLO
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)

            # Handle different checkpoint formats
            if isinstance(checkpoint, dict):
                self.signals.status.emit("Checkpoint dictionary detected, extracting model...")

                # Try different common keys for the model
                if 'model' in checkpoint:
                    model = checkpoint['model']
                elif 'ema' in checkpoint:  # YOLO often stores EMA model
                    model = checkpoint['ema']
                elif 'state_dict' in checkpoint:
                    # Just the state dict, we need to create a model first
                    self.signals.error.emit("State dict only - need full model architecture")
                    return None
                else:
                    # Maybe it's the model itself wrapped in a dict?
                    for key in checkpoint:
                        if hasattr(checkpoint[key], 'eval'):
                            model = checkpoint[key]
                            break
                    else:
                        self.signals.error.emit("Could not find model in checkpoint")
                        return None
            else:
                model = checkpoint

            # Ensure it's a torch.nn.Module
            if not hasattr(model, 'eval'):
                self.signals.error.emit("Loaded object is not a PyTorch model")
                return None

            model.eval()
            self.signals.status.emit("Successfully loaded PyTorch model")
            return model

        except Exception as e:
            self.signals.error.emit(f"Failed to load PyTorch model: {str(e)}")
            return None

    def _get_example_input(self, model):
        """Try to determine appropriate example input shape for the model"""
        self.signals.conversion_step.emit("Determining input shape...")

        # Default for image models
        default_input = torch.randn(1, 3, 224, 224)

        # Try to get input shape from model metadata
        try:
            # Check if model has example_inputs attribute (common in some models)
            if hasattr(model, 'example_inputs') and model.example_inputs is not None:
                if isinstance(model.example_inputs, torch.Tensor):
                    return model.example_inputs
                elif isinstance(model.example_inputs, (list, tuple)) and len(model.example_inputs) > 0:
                    return model.example_inputs[0]

            # Check for dummy_inputs
            if hasattr(model, 'dummy_inputs') and model.dummy_inputs is not None:
                if isinstance(model.dummy_inputs, torch.Tensor):
                    return model.dummy_inputs

            # Try to infer from first parameter
            first_param = next(model.parameters(), None)
            if first_param is not None:
                # Assume input shape based on parameter shape (rough heuristic)
                param_shape = first_param.shape
                if len(param_shape) == 4:  # CNN
                    return torch.randn(1, param_shape[1], 224, 224)
                elif len(param_shape) == 2:  # Linear
                    return torch.randn(1, param_shape[1])

        except Exception as e:
            self.signals.status.emit(f"Could not determine input shape, using default: {str(e)}")

        return default_input

    def _convert_to_onnx(self, model, example_input, model_name):
        """Convert PyTorch model to ONNX format"""
        self.signals.conversion_step.emit("Exporting to ONNX...")
        onnx_path = os.path.join(self.save_path, f"{model_name}.onnx")

        try:
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
        except Exception as e:
            self.signals.error.emit(f"ONNX export failed: {str(e)}")
            return None

    def _convert_to_torchscript(self, model, example_input, model_name):
        """Convert PyTorch model to TorchScript (LibTorch compatible)"""
        self.signals.conversion_step.emit("Tracing model for TorchScript...")

        try:
            # Use tracing for LibTorch compatibility
            traced_model = torch.jit.trace(model, example_input)
            ts_path = os.path.join(self.save_path, f"{model_name}_traced.pt")
            traced_model.save(ts_path)
            return ts_path
        except Exception as e:
            self.signals.error.emit(f"TorchScript export failed: {str(e)}")
            return None

    def _convert_to_executorch(self, model, example_input, model_name):
        """Convert PyTorch model to ExecuTorch format with multiple fallback strategies"""
        self.signals.conversion_step.emit("Exporting to ExecuTorch...")

        try:
            # First try: Use Ultralytics built-in export (for YOLO models)
            if ULTRALYTICS_AVAILABLE:
                try:
                    self.signals.status.emit("Trying Ultralytics ExecuTorch export...")
                    from ultralytics import YOLO

                    # Save model temporarily
                    temp_path = os.path.join(self.save_path, f"{model_name}_temp.pt")
                    if hasattr(model, 'state_dict'):
                        torch.save(model.state_dict(), temp_path)
                    else:
                        torch.save(model, temp_path)

                    # Load and export
                    yolo_model = YOLO(temp_path)
                    export_dir = yolo_model.export(format="executorch", imgsz=[224, 224])

                    # Clean up
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                    # Find .pte file
                    pte_files = list(Path(export_dir).glob("*.pte"))
                    if pte_files:
                        self.signals.status.emit("Ultralytics ExecuTorch export successful")
                        return str(pte_files[0])
                except Exception as e:
                    self.signals.status.emit(f"Ultralytics export failed, trying fallback: {str(e)}")

            # Second try: Manual ExecuTorch export
            self.signals.status.emit("Attempting manual ExecuTorch export...")

            # Ensure schema files exist
            self._ensure_executorch_schema_files()

            import executorch.exir as exir
            from executorch.backends.xnnpack.partition.xnnpack_partitioner import XnnpackPartitioner
            from executorch.exir import EdgeCompileConfig, ExecutorchBackendConfig
            from torch.export import export

            # Ensure example_input is a tuple
            if not isinstance(example_input, tuple):
                example_input = (example_input,)

            # Export using torch.export
            self.signals.conversion_step.emit("Running torch.export...")
            try:
                exported_program = export(model, example_input)
            except Exception as e:
                self.signals.status.emit(f"torch.export failed, trying with dynamo=False")
                # Fallback for older models
                exported_program = torch.export.export(model, example_input, strict=False)

            # Convert to Edge dialect
            self.signals.conversion_step.emit("Converting to Edge dialect...")
            edge_program = exir.to_edge(
                exported_program,
                compile_config=EdgeCompileConfig(
                    _check_ir_validity=False,
                )
            )

            # Apply XNNPACK backend
            edge_program = edge_program.to_backend(XnnpackPartitioner())

            # Generate ExecuTorch program
            self.signals.conversion_step.emit("Generating ExecuTorch program...")
            executorch_program = edge_program.to_executorch(
                ExecutorchBackendConfig()
            )

            # Save the .pte file
            pte_path = os.path.join(self.save_path, f"{model_name}.pte")
            with open(pte_path, "wb") as f:
                f.write(executorch_program.buffer)

            return pte_path

        except ImportError as e:
            self.signals.error.emit(f"Executorch package not properly installed: {str(e)}")
            return None
        except Exception as e:
            self.signals.error.emit(f"ExecuTorch export failed: {str(e)}")
            return None

    def _ensure_executorch_schema_files(self):
        """Ensure required schema files exist for ExecuTorch export"""
        try:

            exec_path = Path(executorch.__file__).parent
            schema_dir = exec_path / "exir" / "_serialize"
            schema_dir.mkdir(exist_ok=True, parents=True)

            program_fbs = schema_dir / "program.fbs"
            scalar_type_fbs = schema_dir / "scalar_type.fbs"

            if not program_fbs.exists() or not scalar_type_fbs.exists():
                source_dir = exec_path / "schema"
                if source_dir.exists():
                    if (source_dir / "program.fbs").exists() and not program_fbs.exists():
                        shutil.copy(source_dir / "program.fbs", program_fbs)
                    if (source_dir / "scalar_type_fbs").exists() and not scalar_type_fbs.exists():
                        shutil.copy(source_dir / "scalar_type_fbs", scalar_type_fbs)
        except Exception:
            pass
    # =======================================================================================
    # _convert_to_tensorflow
    # ======================================================================================
    def _convert_to_tensorflow(self, model, example_input, model_name):
        """Convert PyTorch model to ONNX (TensorFlow compatible via ONNX Runtime)"""
        self.signals.conversion_step.emit("Converting to ONNX (TensorFlow compatible)...")

        try:
            # Convert to ONNX
            onnx_path = os.path.join(self.save_path, f"{model_name}.onnx")

            self.signals.status.emit("Exporting PyTorch to ONNX...")

            torch.onnx.export(
                model,
                example_input,
                onnx_path,
                opset_version=11,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes={'input': {0: 'batch_size'},
                             'output': {0: 'batch_size'}}
            )

            self.signals.status.emit(f"ONNX model saved to: {onnx_path}")
            self.signals.status.emit("TensorFlow can load this using onnxruntime or tf2onnx")

            # Also create a small info file
            info_path = os.path.join(self.save_path, f"{model_name}_tf_info.txt")
            with open(info_path, 'w') as f:
                f.write("To use this model in TensorFlow:\n")
                f.write("1. Install onnxruntime: pip install onnxruntime\n")
                f.write("2. Use onnxruntime to load and run the model\n")
                f.write("3. Or convert to TensorFlow: python -m tf2onnx.convert --input model.onnx --output model.pb\n")

            return onnx_path

        except Exception as e:
            self.signals.error.emit(f"Export failed: {str(e)}")
            return None

    @Slot()
    def run(self):
        try:
            self.signals.status.emit(f"Starting conversion from {self.from_framework} to {self.to_framework}")
            self.signals.progress.emit(10)

            if self._canceled:
                self.signals.canceled.emit(True)
                return

            # Check if model file exists
            if not os.path.exists(self.model_path):
                self.signals.error.emit(f"Model file not found: {self.model_path}")
                return

            # Load model based on source framework
            if self.from_framework.lower() == "pytorch":
                model = self._load_pytorch_model(self.model_path)
                if model is None:
                    return
            else:
                self.signals.error.emit(f"Source framework {self.from_framework} not yet supported")
                return

            self.signals.progress.emit(30)

            if self._canceled:
                return

            # Generate example input
            example_input = self._get_example_input(model)
            self.signals.status.emit(f"Using example input shape: {tuple(example_input.shape)}")

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
                output_path = self._convert_to_onnx(model, example_input, model_name)
                if output_path:
                    self.signals.status.emit("ONNX model ready for OpenCV DNN module")

            else:
                self.signals.error.emit(f"Target framework {self.to_framework} not supported")
                return

            self.signals.progress.emit(90)

            if self._canceled:
                return

            if output_path:
                self.signals.status.emit("Conversion completed successfully!")
                self.signals.conversion_step.emit("Conversion complete")
                self.signals.progress.emit(100)
                self.signals.finished.emit(output_path)
            else:
                self.signals.error.emit("Conversion failed - no output generated")

        except Exception as e:
            error_msg = f"Conversion failed: {str(e)}\n{traceback.format_exc()}"
            self.signals.error.emit(error_msg)
            self.signals.progress.emit(0)
        finally:
            # Disconnect signals to prevent memory leaks
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
