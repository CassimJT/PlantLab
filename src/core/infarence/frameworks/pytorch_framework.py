# frameworks/pytorch_framework.py
import numpy as np
import torch
import torch.nn.functional as F
from .base import BaseFramework, FrameworkFactory

class PyTorchFramework(BaseFramework):
    """PyTorch framework implementation"""

    def __init__(self, model_path=None):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path: str) -> bool:
        try:
            # Try loading as TorchScript first
            try:
                self.model = torch.jit.load(model_path, map_location=self.device)
            except:
                # Fallback to regular PyTorch model
                self.model = torch.load(model_path, map_location=self.device)

            self.model.eval()
            self.model_path = model_path
            print(f"PyTorch model loaded on {self.device}")
            return True
        except Exception as e:
            print(f"Failed to load PyTorch model: {e}")
            return False

    def preprocess(self, image: np.ndarray, input_size: int = 224):
        # Convert to RGB if needed
        if len(image.shape) == 2:
            image = np.stack([image] * 3, axis=-1)
        elif image.shape[2] == 4:
            image = image[:, :, :3]

        # Resize and normalize
        import cv2
        resized = cv2.resize(image, (input_size, input_size))

        # Convert to tensor
        tensor = torch.from_numpy(resized).float()
        tensor = tensor.permute(2, 0, 1)  # HWC to CHW
        tensor = tensor / 255.0  # Normalize to [0, 1]

        # Add batch dimension
        tensor = tensor.unsqueeze(0)

        # Move to device
        tensor = tensor.to(self.device)

        return tensor

    def run_inference(self, input_tensor):
        with torch.no_grad():
            outputs = self.model(input_tensor)

        # Convert to numpy and return
        if isinstance(outputs, torch.Tensor):
            return outputs.cpu().numpy()
        return outputs

    def postprocess(self, outputs) -> tuple:
        if isinstance(outputs, torch.Tensor):
            outputs = outputs.cpu().numpy()

        # Apply softmax
        if outputs.ndim == 2:
            outputs = outputs[0]  # Remove batch if present

        exp_outputs = np.exp(outputs - np.max(outputs))
        probs = exp_outputs / np.sum(exp_outputs)

        class_id = int(np.argmax(probs))
        confidence = float(probs[class_id] * 100.0)

        return class_id, confidence

    def get_framework_name(self) -> str:
        return "PyTorch"

# Register the framework
FrameworkFactory.register('pytorch', PyTorchFramework)
FrameworkFactory.register('torch', PyTorchFramework)
