# This Python file uses the following encoding: utf-8
from PySide6 import QtCore
from pathlib import Path
import os
import tf2onnx
import tensorflow as tf
import onnx
import torch
import torch.nn as nn
import torchvision
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
        self._yolo_model = None  # Store YOLO model reference

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

    def _rebuild_mobilenetv3(self, model_type: str, num_classes: int):
        """Rebuild MobileNetV3 model architecture from type and number of classes"""
        if "mobilenetv3_small" in model_type:
            weights = torchvision.models.MobileNet_V3_Small_Weights.IMAGENET1K_V1
            model = torchvision.models.mobilenet_v3_small(weights=weights)
            in_features = model.classifier[3].in_features
            model.classifier[3] = nn.Linear(in_features, num_classes)
        elif "mobilenetv3_large" in model_type:
            weights = torchvision.models.MobileNet_V3_Large_Weights.IMAGENET1K_V1
            model = torchvision.models.mobilenet_v3_large(weights=weights)
            in_features = model.classifier[3].in_features
            model.classifier[3] = nn.Linear(in_features, num_classes)
        else:
            # Default to small
            weights = torchvision.models.MobileNet_V3_Small_Weights.IMAGENET1K_V1
            model = torchvision.models.mobilenet_v3_small(weights=weights)
            in_features = model.classifier[3].in_features
            model.classifier[3] = nn.Linear(in_features, num_classes)

        return model

    def _load_pytorch_model(self, model_path):
        """Load PyTorch model with special handling for YOLO"""
        self.signals.conversion_step.emit("Loading PyTorch model...")

        # Try loading as YOLO model first if ultralytics is available
        if ULTRALYTICS_AVAILABLE and (model_path.endswith('.pt') or model_path.endswith('.pth')):
            try:
                self.signals.status.emit("Attempting to load as YOLO model...")
                yolo_model = YOLO(model_path)

                # Store the YOLO model for later use
                self._yolo_model = yolo_model

                # For ONNX/TensorFlow/OpenCV conversion, use the YOLO object directly
                if self.to_framework.lower() in ['onnx', 'tensorflow', 'opencv']:
                    self.signals.status.emit("YOLO model loaded successfully for ONNX/TensorFlow export")
                    return yolo_model
                else:
                    # For ExecuTorch/LibTorch, we need to inform user it's not supported directly
                    self.signals.status.emit("YOLO model detected but ExecuTorch export may not be supported")
                    self.signals.status.emit("Attempting to extract model...")
                    if hasattr(yolo_model, 'model'):
                        model = yolo_model.model
                        model.eval()
                        self.signals.status.emit("YOLO model extracted for LibTorch/ExecuTorch")
                        return model
                    else:
                        return yolo_model
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
        try:
            self.signals.status.emit("Attempting to load as regular PyTorch model...")
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)

            # Handle different checkpoint formats
            if isinstance(checkpoint, dict):
                self.signals.status.emit("Checkpoint dictionary detected, extracting model...")

                # Check if this is your training checkpoint with state_dict
                if 'model_state_dict' in checkpoint:
                    self.signals.status.emit("Training checkpoint detected - rebuilding model...")

                    # Get metadata from checkpoint
                    num_classes = checkpoint.get('num_classes', 12)
                    model_type = checkpoint.get('model_type', 'mobilenetv3_small')

                    # Rebuild the model architecture
                    model = self._rebuild_mobilenetv3(model_type, num_classes)

                    # Load the state dict
                    model.load_state_dict(checkpoint['model_state_dict'])
                    model.eval()
                    self.signals.status.emit("Successfully loaded training checkpoint")
                    return model

                # Try different common keys for direct model saves
                elif 'model' in checkpoint:
                    model = checkpoint['model']
                elif 'ema' in checkpoint:  # YOLO often stores EMA model
                    model = checkpoint['ema']
                elif 'state_dict' in checkpoint:
                    # Just the state dict with no architecture info
                    self.signals.error.emit("State dict only - need model architecture information")
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

        # If it's a YOLO model, try to get input size from model
        if ULTRALYTICS_AVAILABLE and isinstance(model, YOLO):
            try:
                if hasattr(model, 'model') and hasattr(model.model, 'args'):
                    imgsz = getattr(model.model.args, 'imgsz', 224)
                    if isinstance(imgsz, (list, tuple)):
                        imgsz = imgsz[0] if imgsz else 224
                    default_input = torch.randn(1, 3, imgsz, imgsz)
                    self.signals.status.emit(f"YOLO model input size detected: {imgsz}")
            except Exception:
                pass

        # Try to get input shape from model metadata
        try:
            # Check if model has example_inputs attribute
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

    def _convert_yolo_to_format(self, yolo_model, target_format, model_name):
        """Convert YOLO model directly using Ultralytics export"""
        self.signals.status.emit(f"Using Ultralytics to export YOLO to {target_format}...")

        try:
            # Map target framework to Ultralytics format
            format_map = {
                'onnx': 'onnx',
                'tensorflow': 'saved_model',
                'executorch': 'executorch',
                'libtorch': 'torchscript',
                'opencv': 'onnx'
            }

            ultralytics_format = format_map.get(target_format.lower(), target_format.lower())

            # For ExecuTorch, check if it's supported
            if target_format.lower() == 'executorch':
                self.signals.status.emit("Note: ExecuTorch export for YOLO may have limitations")
                self.signals.status.emit("Consider using ONNX format if ExecuTorch continues to fail")

            # Export using Ultralytics
            export_path = yolo_model.export(
                format=ultralytics_format,
                imgsz=224,
                batch=1,
                opset=12 if target_format.lower() == 'onnx' else None,
                simplify=True if target_format.lower() == 'onnx' else False
            )

            # Handle return value (can be string or Path object)
            if export_path:
                export_path_str = str(export_path)
                self.signals.status.emit(f"YOLO export successful: {export_path_str}")
                return export_path_str
            else:
                self.signals.error.emit("YOLO export returned no path")
                return None

        except Exception as e:
            self.signals.status.emit(f"YOLO direct export failed: {str(e)}")
            return None

    def _convert_to_onnx(self, model, example_input, model_name):
        """Convert PyTorch model to ONNX"""
        self.signals.conversion_step.emit("Exporting to ONNX...")
        onnx_path = os.path.join(self.save_path, f"{model_name}.onnx")

        # Handle YOLO model specially
        if ULTRALYTICS_AVAILABLE and isinstance(model, YOLO):
            return self._convert_yolo_to_format(model, 'onnx', model_name)

        try:
            torch.onnx.export(
                model,
                example_input,
                onnx_path,
                export_params=True,
                opset_version=12,
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes=None
            )

            # Simplify the ONNX graph
            try:
                import onnx
                from onnxsim import simplify
                model_onnx = onnx.load(onnx_path)
                model_simp, check = simplify(model_onnx)
                if check:
                    onnx.save(model_simp, onnx_path)
                    self.signals.status.emit("ONNX model simplified successfully")
            except ImportError:
                self.signals.status.emit("onnxsim not installed – skipping simplification")
            except Exception as simp_err:
                self.signals.status.emit(f"Simplification failed: {simp_err}")

            return onnx_path
        except Exception as e:
            self.signals.error.emit(f"ONNX export failed: {str(e)}")
            return None

    def _convert_to_torchscript(self, model, example_input, model_name):
        """Convert PyTorch model to TorchScript (LibTorch compatible)"""
        self.signals.conversion_step.emit("Tracing model for TorchScript...")

        # Handle YOLO model specially
        if ULTRALYTICS_AVAILABLE and isinstance(model, YOLO):
            return self._convert_yolo_to_format(model, 'libtorch', model_name)

        try:
            # Use tracing for LibTorch compatibility
            traced_model = torch.jit.trace(model, example_input, strict=False)
            ts_path = os.path.join(self.save_path, f"{model_name}_traced.pt")
            traced_model.save(ts_path)
            return ts_path
        except Exception as e:
            self.signals.error.emit(f"TorchScript export failed: {str(e)}")
            return None

    def _convert_to_executorch(self, model, example_input, model_name):
        """Convert PyTorch model to ExecuTorch format with multiple fallback strategies"""
        self.signals.conversion_step.emit("Exporting to ExecuTorch...")

        # Special message for YOLO models
        if ULTRALYTICS_AVAILABLE and (isinstance(model, YOLO) or self._yolo_model is not None):
            self.signals.status.emit("YOLO models have limited ExecuTorch support")
            self.signals.status.emit("The model contains operations (.item()) that are incompatible with ExecuTorch")
            self.signals.status.emit("Recommendation: Use ONNX format for better compatibility")

            # Ask user if they want to continue (in a real app, you'd show a dialog)
            self.signals.status.emit("Attempting export anyway (may fail)...")

            # Try alternative: Convert to ONNX first, then provide instructions
            self.signals.status.emit("Alternative: Convert to ONNX format first, then use ONNX runtime")
            onnx_alternative = os.path.join(self.save_path, f"{model_name}.onnx")
            if os.path.exists(onnx_alternative):
                self.signals.status.emit(f"ONNX model already exists at: {onnx_alternative}")
                self.signals.status.emit("You can use this with ONNX Runtime instead of ExecuTorch")

        model.eval()
        model = model.to('cpu')

        # Try different export strategies
        strategies = [
            self._try_executorch_export_strict,
            self._try_executorch_export_non_strict,
            self._try_executorch_via_torchscript,
            self._try_executorch_via_onnx
        ]

        for i, strategy in enumerate(strategies):
            if self._canceled:
                return None

            self.signals.status.emit(f"Trying export strategy {i+1}/{len(strategies)}...")
            try:
                result = strategy(model, example_input, model_name)
                if result:
                    self.signals.status.emit(f"Export successful with strategy {i+1}")
                    return result
            except Exception as e:
                self.signals.status.emit(f"Strategy {i+1} failed: {str(e)[:100]}")
                continue

        self.signals.error.emit("All ExecuTorch export strategies failed. YOLO models are not fully compatible with ExecuTorch due to dynamic operations.")
        self.signals.error.emit("Recommendation: Export to ONNX format instead for broader compatibility.")
        return None

    def _try_executorch_export_strict(self, model, example_input, model_name):
        """Try ExecuTorch export with strict=True"""
        self.signals.status.emit("Strategy 1: torch.export with strict=True...")

        try:
            import executorch.exir as exir
            from executorch.backends.xnnpack.partition.xnnpack_partitioner import XnnpackPartitioner
            from executorch.exir import EdgeCompileConfig, ExecutorchBackendConfig
            from torch.export import export

            if not isinstance(example_input, tuple):
                example_input = (example_input,)

            exported_program = export(model, example_input, strict=True)

            edge_program = exir.to_edge(
                exported_program,
                compile_config=EdgeCompileConfig(_check_ir_validity=False)
            )

            edge_program = edge_program.to_backend(XnnpackPartitioner())

            executorch_program = edge_program.to_executorch(ExecutorchBackendConfig())

            pte_path = os.path.join(self.save_path, f"{model_name}.pte")
            with open(pte_path, "wb") as f:
                f.write(executorch_program.buffer)

            return pte_path
        except Exception as e:
            raise Exception(f"Strict export failed: {str(e)}")

    def _try_executorch_export_non_strict(self, model, example_input, model_name):
        """Try ExecuTorch export with strict=False"""
        self.signals.status.emit("Strategy 2: torch.export with strict=False...")

        try:
            import executorch.exir as exir
            from executorch.backends.xnnpack.partition.xnnpack_partitioner import XnnpackPartitioner
            from executorch.exir import EdgeCompileConfig, ExecutorchBackendConfig
            from torch.export import export

            if not isinstance(example_input, tuple):
                example_input = (example_input,)

            exported_program = export(model, example_input, strict=False)

            edge_program = exir.to_edge(
                exported_program,
                compile_config=EdgeCompileConfig(_check_ir_validity=False)
            )

            edge_program = edge_program.to_backend(XnnpackPartitioner())

            executorch_program = edge_program.to_executorch(ExecutorchBackendConfig())

            pte_path = os.path.join(self.save_path, f"{model_name}_nonstrict.pte")
            with open(pte_path, "wb") as f:
                f.write(executorch_program.buffer)

            return pte_path
        except Exception as e:
            raise Exception(f"Non-strict export failed: {str(e)}")

    def _try_executorch_via_torchscript(self, model, example_input, model_name):
        """Convert to TorchScript first, then to ExecuTorch"""
        self.signals.status.emit("Strategy 3: Convert to TorchScript first...")

        try:
            # First convert to TorchScript
            if not isinstance(example_input, tuple):
                example_input = (example_input,)

            traced_model = torch.jit.trace(model, example_input, strict=False)

            # Then convert TorchScript to ExecuTorch
            import executorch.exir as exir
            from executorch.exir import EdgeCompileConfig, ExecutorchBackendConfig

            exported_program = torch.export.export(traced_model, example_input, strict=False)

            edge_program = exir.to_edge(
                exported_program,
                compile_config=EdgeCompileConfig(_check_ir_validity=False)
            )

            executorch_program = edge_program.to_executorch(ExecutorchBackendConfig())

            pte_path = os.path.join(self.save_path, f"{model_name}_from_ts.pte")
            with open(pte_path, "wb") as f:
                f.write(executorch_program.buffer)

            return pte_path
        except Exception as e:
            raise Exception(f"TorchScript intermediate conversion failed: {str(e)}")

    def _try_executorch_via_onnx(self, model, example_input, model_name):
        """Convert to ONNX first, then provide instructions (no actual conversion)"""
        self.signals.status.emit("Strategy 4: Provide ONNX alternative...")

        # This strategy doesn't actually convert to ExecuTorch
        # It just creates an ONNX file as a recommended alternative
        onnx_path = os.path.join(self.save_path, f"{model_name}.onnx")

        if not os.path.exists(onnx_path):
            self.signals.status.emit("Creating ONNX version as recommended alternative...")
            if ULTRALYTICS_AVAILABLE and isinstance(model, YOLO):
                onnx_path = self._convert_yolo_to_format(model, 'onnx', model_name)
            else:
                self._convert_to_onnx(model, example_input, model_name)

        if os.path.exists(onnx_path):
            self.signals.status.emit(f"ONNX model created at: {onnx_path}")
            self.signals.status.emit("ExecuTorch export failed, but ONNX export succeeded")
            self.signals.status.emit("Use ONNX format with ONNX Runtime for deployment")

            # Create an info file explaining the situation
            info_path = os.path.join(self.save_path, f"{model_name}_executorch_fallback_info.txt")
            with open(info_path, 'w') as f:
                f.write("ExecuTorch Export Failed - Alternative Solution\n")
                f.write("============================================\n\n")
                f.write("The YOLO model could not be exported to ExecuTorch because it contains\n")
                f.write("operations (like .item() calls) that are not compatible with ExecuTorch's\n")
                f.write("static graph requirements.\n\n")
                f.write("Recommended Alternative:\n")
                f.write("------------------------\n")
                f.write(f"Use the ONNX model instead: {onnx_path}\n\n")
                f.write("ONNX models can be used with:\n")
                f.write("  - ONNX Runtime (Python, C++, C#, Java)\n")
                f.write("  - OpenCV DNN module\n")
                f.write("  - TensorFlow (via tf2onnx)\n")
                f.write("  - Many other frameworks and devices\n\n")
                f.write("For mobile deployment, consider:\n")
                f.write("  - Convert ONNX to Core ML for iOS\n")
                f.write("  - Convert ONNX to TFLite for Android\n")
                f.write("  - Use ONNX Runtime Mobile\n")

            # Return None to indicate failure, but we've provided an alternative
            raise Exception("ExecuTorch export not possible - ONNX alternative provided")
        else:
            raise Exception("Failed to create ONNX alternative")

    def _convert_to_tensorflow(self, model, example_input, model_name):
        """Convert PyTorch model to TensorFlow via ONNX"""
        self.signals.conversion_step.emit("Converting to TensorFlow via ONNX...")

        # Handle YOLO model specially
        if ULTRALYTICS_AVAILABLE and isinstance(model, YOLO):
            # First convert to ONNX using YOLO's exporter
            onnx_path = self._convert_yolo_to_format(model, 'onnx', model_name)
            if onnx_path and os.path.exists(onnx_path):
                # Then convert ONNX to TensorFlow
                return self._convert_onnx_to_tensorflow(onnx_path, model_name)
            return None

        try:
            # Convert to ONNX first
            onnx_path = os.path.join(self.save_path, f"{model_name}_temp.onnx")

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

            # Convert ONNX to TensorFlow
            return self._convert_onnx_to_tensorflow(onnx_path, model_name)

        except Exception as e:
            self.signals.error.emit(f"TensorFlow export failed: {str(e)}")
            return None

    def _convert_onnx_to_tensorflow(self, onnx_path, model_name):
        """Convert ONNX model to TensorFlow format"""
        try:
            self.signals.status.emit("Converting ONNX to TensorFlow...")

            # Use tf2onnx to convert ONNX to TensorFlow
            import tf2onnx
            from tf2onnx import convert

            # Load ONNX model
            onnx_model = onnx.load(onnx_path)

            # Convert to TensorFlow
            tf_path = os.path.join(self.save_path, f"{model_name}_tf_model")
            os.makedirs(tf_path, exist_ok=True)

            # Run the conversion
            tf_model = convert.from_onnx(onnx_model)

            # Save as SavedModel format
            tf.saved_model.save(tf_model, tf_path)

            # Also save as frozen graph .pb
            pb_path = os.path.join(self.save_path, f"{model_name}.pb")
            with tf.io.gfile.GFile(pb_path, 'wb') as f:
                f.write(tf_model.graph.as_graph_def().SerializeToString())

            # Create info file
            info_path = os.path.join(self.save_path, f"{model_name}_tf_info.txt")
            with open(info_path, 'w') as f:
                f.write(f"TensorFlow model saved in two formats:\n")
                f.write(f"1. SavedModel format: {tf_path}\n")
                f.write(f"2. Frozen graph: {pb_path}\n")
                f.write("\nTo load in TensorFlow:\n")
                f.write(f"  model = tf.saved_model.load('{tf_path}')\n")
                f.write(f"  or\n")
                f.write(f"  with tf.io.gfile.GFile('{pb_path}', 'rb') as f:\n")
                f.write(f"      graph_def = tf.compat.v1.GraphDef()\n")
                f.write(f"      graph_def.ParseFromString(f.read())\n")

            # Clean up temporary ONNX file
            if os.path.exists(onnx_path) and "temp" in onnx_path:
                os.remove(onnx_path)

            return pb_path

        except Exception as e:
            self.signals.error.emit(f"ONNX to TensorFlow conversion failed: {str(e)}")
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

            # For YOLO models going to certain formats, we can use direct export
            if ULTRALYTICS_AVAILABLE and isinstance(model, YOLO) and self.to_framework.lower() in ['onnx', 'tensorflow', 'opencv']:
                self.signals.progress.emit(50)
                output_path = self._convert_yolo_to_format(model, self.to_framework, Path(self.model_path).stem)
                if output_path:
                    self.signals.progress.emit(100)
                    self.signals.finished.emit(output_path)
                    return

            # Generate example input for non-YOLO models or when needed
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
            # Clean up
            self._yolo_model = None
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