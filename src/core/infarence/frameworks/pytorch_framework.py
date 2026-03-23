# frameworks/pytorch_framework.py
import numpy as np
import torch
import torch.nn.functional as F
import warnings
from .base import BaseFramework, FrameworkFactory

class PyTorchFramework(BaseFramework):
    """PyTorch framework implementation"""

    def __init__(self, model_path=None):
        self.model = None
        # Force CPU to avoid CUDA warnings
        self.device = torch.device('cpu')
        self.model_path = model_path
        if model_path:
            self.load_model(model_path)

    @classmethod
    # frameworks/pytorch_framework.py
    def is_available(cls) -> bool:
        """Check if PyTorch is available (ignore CUDA warnings)"""
        try:
            # Suppress all warnings
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import torch
                # Don't check CUDA, just return True if import works
                return True
        except ImportError:
            return False
        except Exception as e:
            print(f"Unexpected error checking PyTorch: {e}")
            return False

    def load_model(self, model_path: str) -> bool:
        try:
            # Suppress warnings during loading
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                # Force CPU
                checkpoint = torch.load(model_path, map_location='cpu')

                # Case 1: It's a scripted / traced model (torch.jit)
                if isinstance(checkpoint, torch.jit.ScriptModule):
                    self.model = checkpoint
                    print("Loaded TorchScript model")

                # Case 2: It's a state_dict dictionary (most common for .pth / best.pth)
                elif isinstance(checkpoint, dict):
                    # Try to find the actual state_dict key (common variations)
                    state_dict = None
                    if 'state_dict' in checkpoint:
                        state_dict = checkpoint['state_dict']
                    elif 'model' in checkpoint:
                        state_dict = checkpoint['model']
                    else:
                        # Assume the dict itself is the state_dict
                        state_dict = checkpoint

                    # You MUST know your model architecture here!
                    # Replace this with your actual MobileNetV3 creation code
                    from torchvision.models import mobilenet_v3_small  # or your custom model file

                    # Create model instance (same architecture as during training)
                    self.model = mobilenet_v3_small(num_classes=38)  # ← CHANGE TO YOUR NUM_CLASSES

                    # Load weights (handle possible "module." prefix from DataParallel)
                    state_dict = {k.replace("module.", ""): v for k, v in state_dict.items()}
                    self.model.load_state_dict(state_dict, strict=False)  # strict=False helps with mismatches

                    print("Loaded weights into fresh model instance")

                # Case 3: Direct model instance (rare)
                elif isinstance(checkpoint, torch.nn.Module):
                    self.model = checkpoint
                    print("Loaded full model instance")

                else:
                    raise ValueError(f"Unknown checkpoint type: {type(checkpoint)}")

                self.model.eval()  # now safe
                self.model.to(self.device)
                self.model_path = model_path
                print(f"PyTorch model successfully loaded on {self.device}")
                return True

        except Exception as e:
            print(f"Failed to load PyTorch model: {type(e).__name__}: {str(e)}")
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

        # Move to device (cpu)
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
