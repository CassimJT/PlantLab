# frameworks/opencv_framework.py
import numpy as np
import cv2
import warnings
from .base import BaseFramework, FrameworkFactory

class OpenCVFramework(BaseFramework):
    """OpenCV framework implementation (for DNN models)"""

    def __init__(self, model_path=None, config_path=None):
        self.net = None
        self.model_path = model_path
        self.config_path = config_path
        self.input_size = 224
        self.mean = [0.485, 0.456, 0.406]  # ImageNet mean
        self.std = [0.229, 0.224, 0.225]   # ImageNet std

        if model_path:
            self.load_model(model_path, config_path)

    @classmethod
    def is_available(cls) -> bool:
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import cv2
                # OpenCV is usually available if import works
                return True
        except ImportError:
            return False
        except Exception as e:
            print(f"Unexpected error checking OpenCV: {e}")
            return False

    def load_model(self, model_path: str, config_path: str = None) -> bool:
        try:
            if model_path.endswith('.onnx'):
                self.net = cv2.dnn.readNetFromONNX(model_path)
            elif model_path.endswith('.caffemodel') and config_path:
                self.net = cv2.dnn.readNetFromCaffe(config_path, model_path)
            elif model_path.endswith('.pb') and config_path:
                self.net = cv2.dnn.readNetFromTensorflow(model_path, config_path)
            elif model_path.endswith('.weights') and config_path:
                self.net = cv2.dnn.readNetFromDarknet(config_path, model_path)
            else:
                self.net = cv2.dnn.readNet(model_path)

            # Try to use GPU if available (but don't fail if not)
            try:
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            except:
                pass

            print(f"OpenCV DNN model loaded")
            return True
        except Exception as e:
            print(f"Failed to load OpenCV model: {e}")
            return False

    def preprocess(self, image: np.ndarray, input_size: int = 224):
        # OpenCV's blobFromImage handles preprocessing
        blob = cv2.dnn.blobFromImage(
            image,
            scalefactor=1.0/255.0,
            size=(input_size, input_size),
            mean=self.mean,
            swapRB=True,
            crop=False
        )
        return blob

    def run_inference(self, input_tensor):
        self.net.setInput(input_tensor)
        outputs = self.net.forward()
        return outputs

    def postprocess(self, outputs) -> tuple:
        if outputs.ndim == 2:
            outputs = outputs[0]

        exp_outputs = np.exp(outputs - np.max(outputs))
        probs = exp_outputs / np.sum(exp_outputs)

        class_id = int(np.argmax(probs))
        confidence = float(probs[class_id] * 100.0)

        return class_id, confidence

    def get_framework_name(self) -> str:
        return "OpenCV"

# Register the framework
FrameworkFactory.register('opencv', OpenCVFramework)
FrameworkFactory.register('cv2', OpenCVFramework)
FrameworkFactory.register('dnn', OpenCVFramework)
