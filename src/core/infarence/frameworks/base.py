# frameworks/base.py
from abc import ABC, abstractmethod
import numpy as np
from typing import Tuple, Any, Optional

class BaseFramework(ABC):
    """Abstract base class for all ML frameworks"""

    @abstractmethod
    def load_model(self, model_path: str) -> bool:
        """Load model from path"""
        pass

    @abstractmethod
    def preprocess(self, image: np.ndarray, input_size: int = 224) -> Any:
        """Preprocess image for model input"""
        pass

    @abstractmethod
    def run_inference(self, input_tensor: Any) -> np.ndarray:
        """Run inference and return raw outputs"""
        pass

    @abstractmethod
    def postprocess(self, outputs: Any) -> Tuple[int, float]:
        """Postprocess outputs to get class and confidence"""
        pass

    @abstractmethod
    def get_framework_name(self) -> str:
        """Return framework name"""
        pass

    def is_available(self) -> bool:
        """Check if framework is available"""
        return True

class FrameworkFactory:
    """Factory for creating framework instances"""

    _frameworks = {}

    @classmethod
    def register(cls, name: str, framework_class):
        """Register a framework"""
        cls._frameworks[name.lower()] = framework_class

    @classmethod
    def create(cls, name: str, **kwargs) -> Optional[BaseFramework]:
        """Create framework instance"""
        framework_class = cls._frameworks.get(name.lower())
        if framework_class:
            return framework_class(**kwargs)
        return None

    @classmethod
    def get_available_frameworks(cls) -> list:
        """Get list of available framework names"""
        available = []
        for name, framework_class in cls._frameworks.items():
            try:
                # Try to create instance to check availability
                framework = framework_class()
                if framework.is_available():
                    available.append(name)
            except:
                pass
        return available
