import numpy as np
import cv2
import warnings
from .base import BaseFramework, FrameworkFactory

class OpenCVFramework(BaseFramework):
    """OpenCV framework – with ONNX Runtime fallback for modern ONNX models"""

    def __init__(self, model_path=None, config_path=None):
        self.net = None
        self.session = None  # for ONNX Runtime
        self.input_name = None
        self.model_path = model_path
        self.config_path = config_path
        self.input_size = 640  # ← change to your YOLO input size (e.g. 640 for YOLOv11)
        if model_path:
            self.load_model(model_path, config_path)

    @classmethod
    def is_available(cls) -> bool:
        try:
            import cv2
            import onnxruntime  # check both
            return True
        except ImportError:
            return False

    def load_model(self, model_path: str, config_path: str = None) -> bool:
        try:
            print(f"Attempting to load ONNX model: {model_path}")

            # Prefer ONNX Runtime for modern YOLO ONNX (fixes kernel_shape issue)
            if model_path.endswith('.onnx'):
                try:
                    import onnxruntime as ort
                    self.session = ort.InferenceSession(
                        model_path,
                        providers=['CPUExecutionProvider']  # add 'CUDAExecutionProvider' if you have GPU
                    )
                    self.input_name = self.session.get_inputs()[0].name
                    print("Loaded successfully with ONNX Runtime (recommended)")
                    return True
                except Exception as ort_e:
                    print(f"ONNX Runtime failed: {ort_e} – falling back to OpenCV DNN")

            # Fallback to OpenCV DNN (your original code)
            if model_path.endswith('.onnx'):
                self.net = cv2.dnn.readNetFromONNX(model_path)
            # ... (keep your other formats: Caffe, TF, Darknet)

            # Set backend/target
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

            print("OpenCV DNN model loaded")
            return True

        except Exception as e:
            print(f"Failed to load model: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def preprocess(self, image: np.ndarray, input_size: int = 640):  # ← update to YOLO size
        # For ONNX Runtime: return numpy array in NCHW
        # For OpenCV: return blob
        if hasattr(self, 'session'):  # ONNX Runtime path
            # Resize, normalize, transpose to CHW, add batch
            img = cv2.resize(image, (input_size, input_size))
            img = img.astype(np.float32) / 255.0
            img = img.transpose(2, 0, 1)  # HWC → CHW
            img = np.expand_dims(img, axis=0)  # add batch
            return img
        else:  # OpenCV DNN path
            return cv2.dnn.blobFromImage(
                image,
                scalefactor=1.0/255.0,
                size=(input_size, input_size),
                mean=(0,0,0),  # YOLO usually no mean/std subtract
                swapRB=True,
                crop=False
            )

    def run_inference(self, input_tensor):
        if hasattr(self, 'session'):  # ONNX Runtime
            outputs = self.session.run(None, {self.input_name: input_tensor})
            return outputs[0]  # usually first output is detections
        else:  # OpenCV DNN
            self.net.setInput(input_tensor)
            return self.net.forward()

    # postprocess: adapt for YOLO format (e.g. parse bounding boxes, classes, confs)
    # YOLO ONNX output is usually [batch, num_boxes, 4+1+num_classes] or similar
    def postprocess(self, outputs) -> tuple:
        # Simple example – adjust based on your model's output shape
        # For classification-style: argmax on flattened probs
        outputs = np.asarray(outputs)
        if outputs.ndim == 2:
            outputs = outputs[0]
        # Softmax + argmax (if classification head)
        exp = np.exp(outputs - np.max(outputs))
        probs = exp / np.sum(exp)
        class_id = int(np.argmax(probs))
        confidence = float(probs[class_id] * 100.0)
        return class_id, confidence

    def get_framework_name(self) -> str:
        return "OpenCV"  # or "ONNX Runtime" if you want to distinguish