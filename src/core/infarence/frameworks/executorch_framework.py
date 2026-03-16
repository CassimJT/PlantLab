# frameworks/executorch_framework.py
import numpy as np
from .base import BaseFramework, FrameworkFactory

class ExecuTorchFramework(BaseFramework):
    """ExecuTorch framework implementation"""

    def __init__(self, model_path=None):
        self.module = None
        self.model_path = model_path
        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path: str) -> bool:
        try:
            # Import ExecuTorch
            import executorch
            from executorch.extension.module import Module

            self.module = Module(model_path)
            print(f"ExecuTorch model loaded")
            return True
        except ImportError:
            print("ExecuTorch not available")
            return False
        except Exception as e:
            print(f"Failed to load ExecuTorch model: {e}")
            return False

    def is_available(self) -> bool:
        try:
            import executorch
            return True
        except ImportError:
            return False

    def preprocess(self, image: np.ndarray, input_size: int = 224):
        import cv2

        # Convert to RGB if needed
        if len(image.shape) == 2:
            image = np.stack([image] * 3, axis=-1)
        elif image.shape[2] == 4:
            image = image[:, :, :3]

        # Resize
        resized = cv2.resize(image, (input_size, input_size))

        # Normalize to [0, 1]
        normalized = resized.astype(np.float32) / 255.0

        # Convert to CHW format
        chw = np.transpose(normalized, (2, 0, 1))

        # Add batch dimension
        batched = np.expand_dims(chw, axis=0)

        return batched

    def run_inference(self, input_tensor):
        # Convert to appropriate format for ExecuTorch
        # This is a simplified version - actual implementation depends on ExecuTorch API
        import torch
        import executorch

        # Convert numpy to tensor
        if isinstance(input_tensor, np.ndarray):
            input_tensor = torch.from_numpy(input_tensor)

        # Run inference
        result = self.module.forward(input_tensor)

        if result.ok():
            output = result.get()
            if hasattr(output, 'numpy'):
                return output.numpy()
            return output
        else:
            raise RuntimeError("Inference failed")

    def postprocess(self, outputs) -> tuple:
        if hasattr(outputs, 'numpy'):
            outputs = outputs.numpy()

        if outputs.ndim == 2:
            outputs = outputs[0]

        exp_outputs = np.exp(outputs - np.max(outputs))
        probs = exp_outputs / np.sum(exp_outputs)

        class_id = int(np.argmax(probs))
        confidence = float(probs[class_id] * 100.0)

        return class_id, confidence

    def get_framework_name(self) -> str:
        return "ExecuTorch"

# Register the framework
FrameworkFactory.register('executorch', ExecuTorchFramework)
FrameworkFactory.register('et', ExecuTorchFramework)
