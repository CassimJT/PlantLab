# frameworks/tensorflow_framework.py
import numpy as np
import warnings
from .base import BaseFramework, FrameworkFactory

class TensorFlowFramework(BaseFramework):
    """TensorFlow/Keras framework implementation"""

    def __init__(self, model_path=None):
        self.model = None
        self.model_path = model_path
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.is_tflite = False

        if model_path:
            self.load_model(model_path)

    @classmethod
    def is_available(cls) -> bool:
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import tensorflow as tf
                # Just check import, don't initialize anything
                return True
        except ImportError:
            return False
        except Exception as e:
            print(f"Unexpected error checking TensorFlow: {e}")
            return False

    def load_model(self, model_path: str) -> bool:
        try:
            import tensorflow as tf

            # Check if it's a TFLite model
            if model_path.endswith('.tflite'):
                self.interpreter = tf.lite.Interpreter(model_path=model_path)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
                self.is_tflite = True
                print(f"TensorFlow Lite model loaded")
            else:
                # Load regular SavedModel or H5
                self.model = tf.keras.models.load_model(model_path)
                print(f"TensorFlow/Keras model loaded")

            self.model_path = model_path
            return True
        except Exception as e:
            print(f"Failed to load TensorFlow model: {e}")
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

        # Add batch dimension
        batched = np.expand_dims(normalized, axis=0)

        return batched

    def run_inference(self, input_tensor):
        if self.is_tflite:
            self.interpreter.set_tensor(self.input_details[0]['index'], input_tensor)
            self.interpreter.invoke()
            output = self.interpreter.get_tensor(self.output_details[0]['index'])
            return output
        else:
            return self.model.predict(input_tensor, verbose=0)

    def postprocess(self, outputs) -> tuple:
        if outputs.ndim == 2:
            outputs = outputs[0]  # Remove batch if present

        # Apply softmax if needed
        if outputs.ndim == 1:
            probs = outputs
        else:
            exp_outputs = np.exp(outputs - np.max(outputs))
            probs = exp_outputs / np.sum(exp_outputs)

        class_id = int(np.argmax(probs))
        confidence = float(probs[class_id] * 100.0)

        return class_id, confidence

    def get_framework_name(self) -> str:
        return "TensorFlow"

# Register the framework
FrameworkFactory.register('tensorflow', TensorFlowFramework)
FrameworkFactory.register('tf', TensorFlowFramework)
FrameworkFactory.register('keras', TensorFlowFramework)
FrameworkFactory.register('tflite', TensorFlowFramework)
