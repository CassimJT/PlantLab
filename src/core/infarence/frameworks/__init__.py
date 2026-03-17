# frameworks/__init__.py
"""
ML Framework Adapters Module
"""

from .base import BaseFramework, FrameworkFactory

# Import all frameworks to register them
from .pytorch_framework import PyTorchFramework
from .executorch_framework import ExecuTorchFramework
from .tensorflow_framework import TensorFlowFramework
from .opencv_framework import OpenCVFramework

# Print registration status
print("Registering frameworks...")
print(f"  - PyTorch: {PyTorchFramework}")
print(f"  - TensorFlow: {TensorFlowFramework}")
print(f"  - ExecuTorch: {ExecuTorchFramework}")
print(f"  - OpenCV: {OpenCVFramework}")

__all__ = [
    'BaseFramework',
    'FrameworkFactory',
    'PyTorchFramework',
    'ExecuTorchFramework',
    'TensorFlowFramework',
    'OpenCVFramework',
]
