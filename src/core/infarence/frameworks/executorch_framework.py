# frameworks/executorch_framework.py

import numpy as np
import warnings
import os
from typing import Any, Tuple
from .base import BaseFramework, FrameworkFactory

class ExecuTorchFramework(BaseFramework):
    """ExecuTorch framework implementation – updated for 2026 main branch"""

    def __init__(self, model_path: str = None):
        self.program = None
        self.model_path = model_path
        self._import_error = None
        if model_path:
            self.load_model(model_path)

    @classmethod
    def is_available(cls) -> bool:
        """Check if ExecuTorch runtime is usable"""
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import executorch
                # Try to import the modern runtime loader
                from executorch.runtime import ExecuTorchProgram
                print("✓ Found executorch.runtime.ExecuTorchProgram")
                return True
        except ImportError as e:
            print(f"ExecuTorch runtime import failed: {e}")
            return False
        except Exception as e:
            print(f"Unexpected ExecuTorch check error: {e}")
            return False
    def load_model(self, model_path: str) -> bool:
        """Load .pte using official ExecuTorch Runtime API"""
        import os
        if not os.path.isfile(model_path):
            print(f"Model file not found: {model_path}")
            return False

        try:
            from executorch.runtime import Runtime

            print(f"Attempting official ExecuTorch load: {model_path}")

            runtime = Runtime.get()
            self.program = runtime.load_program(model_path)  # str path is supported

            print("✓ Successfully loaded via Runtime.get().load_program(path)")
            self.model_path = model_path
            return True

        except ImportError as e:
            print(f"Cannot import executorch.runtime: {e}")
        except AttributeError as e:
            print(f"Runtime missing 'load_program' method: {e}")
        except TypeError as e:
            print(f"load_program called with wrong args: {e}")
        except Exception as e:
            print(f"Load failed: {type(e).__name__}: {str(e)}")

        print("Loading failed - likely Python bindings issue in your build")
        return False

    def preprocess(self, image: np.ndarray, input_size: int = 224) -> np.ndarray:
        """Standard MobileNetV3-style preprocessing"""
        import cv2
        if image is None or image.size == 0:
            raise ValueError("Invalid input image")

        # Ensure RGB
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        # Resize & normalize
        image = cv2.resize(image, (input_size, input_size))
        image = image.astype(np.float32) / 255.0

        # NCHW
        image = np.transpose(image, (2, 0, 1))          # HWC → CHW
        image = np.expand_dims(image, axis=0)           # add batch
        return image

    def run_inference(self, input_tensor):
        if self.program is None:
            raise RuntimeError("Model not loaded")

        try:
            import torch

            if isinstance(input_tensor, np.ndarray):
                input_tensor = torch.from_numpy(input_tensor)

            # Load the "forward" method (most models have only one)
            method = self.program.load_method("forward")

            # Execute with list of inputs
            outputs = method.execute([input_tensor])

            # Handle output (usually list or single tensor)
            if isinstance(outputs, (list, tuple)):
                output = outputs[0]
            else:
                output = outputs

            if hasattr(output, 'detach'):
                return output.detach().cpu().numpy()
            return np.asarray(output)

        except Exception as e:
            raise RuntimeError(f"Inference failed: {type(e).__name__}: {e}")

    def postprocess(self, outputs: Any) -> Tuple[int, float]:
        """Simple argmax + softmax post-processing"""
        if outputs is None:
            return -1, 0.0

        # Flatten if needed
        if outputs.ndim > 1:
            outputs = outputs.flatten()

        # Softmax if logits
        if np.max(outputs) > 5 or np.min(outputs) < -5:  # rough logit detection
            exp = np.exp(outputs - np.max(outputs))
            probs = exp / exp.sum()
        else:
            probs = outputs / outputs.sum()

        class_id = int(np.argmax(probs))
        confidence = float(probs[class_id] * 100)
        return class_id, confidence

    def get_framework_name(self) -> str:
        return "ExecuTorch"

# Register (keep your original aliases)
FrameworkFactory.register('executorch', ExecuTorchFramework)
FrameworkFactory.register('et', ExecuTorchFramework)
FrameworkFactory.register('execution', ExecuTorchFramework)