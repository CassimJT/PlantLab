# DiseaseInfoManager.py
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, QLocale


@dataclass
class DiseaseInfo:
    name: str = ""
    description: str = ""
    cure: str = ""

    def is_valid(self) -> bool:
        return bool(self.name)


class DiseaseInfoManager(QObject):
    """Singleton manager for disease information in multiple languages"""

    _instance = None
    language_changed = Signal(str)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, parent=None):
        if hasattr(self, '_initialized') and self._initialized:
            return

        super().__init__(parent)
        self._initialized = True

        self._disease_info: Dict[int, DiseaseInfo] = {}
        self._current_language = "en"
        self._default_language = "en"

        # Resource search paths
        self._resource_paths = self._get_resource_paths()

        # Load default language
        self.load_language(self._default_language)

        # DiseaseInfoManager.py - updated _get_resource_paths method

    def _get_resource_paths(self) -> List[str]:
        """Get possible paths for language resources"""
        paths = []

        # Get the project root directory
        current_file = Path(__file__).resolve()  # src/core/infarence/DiseaseInfoManager.py
        project_root = current_file.parent.parent.parent.parent  # Go up to Plantlab/

        print(f"Project root: {project_root}")

        # Add all possible resource locations
        paths.extend([
            # Your assets directory (where files actually are)
            str(project_root / "assets" / "languages"),

            # Resources directory at project root
            str(project_root / "resources" / "languages"),

            # Languages directory at project root
            str(project_root / "languages"),

            # Inside the infarence module
            str(project_root / "src" / "core" / "infarence" / "resources" / "languages"),

            # Current working directory
            str(Path.cwd() / "assets" / "languages"),
            str(Path.cwd() / "resources" / "languages"),
            str(Path.cwd() / "languages"),

            # Qt resources
            ":/languages",
        ])

        # Remove empty strings
        paths = [p for p in paths if p]

        print(f"Resource search paths: {paths}")
        return paths

    def load_language(self, language_code: str) -> bool:
        """Load disease information for specified language"""
        print(f"=== Attempting to load language: {language_code} ===")

        # Try different file naming patterns
        filenames = [
            f"diseases_{language_code}.json",
            f"diseases_{language_code.upper()}.json",
            f"diseases_{language_code.lower()}.json"
        ]

        # Try each resource path
        for resource_path in self._resource_paths:
            for filename in filenames:
                file_path = os.path.join(resource_path, filename)
                print(f"Trying path: {file_path}")

                if os.path.exists(file_path):
                    print(f"File exists, attempting to open: {file_path}")
                    if self._load_from_file(file_path):
                        self._current_language = language_code
                        self.language_changed.emit(language_code)
                        print(f"Successfully loaded {len(self._disease_info)} entries from: {file_path}")
                        return True
                else:
                    # Try as Qt resource
                    qt_path = f":/languages/{filename}"
                    if self._load_from_qt_resource(qt_path):
                        self._current_language = language_code
                        self.language_changed.emit(language_code)
                        print(f"Successfully loaded from Qt resource: {qt_path}")
                        return True

        print(f"Failed to load language: {language_code}")
        return False

    def _load_from_file(self, file_path: str) -> bool:
        """Load and parse JSON from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._parse_json_data(data)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return False

    def _load_from_qt_resource(self, resource_path: str) -> bool:
        """Load and parse JSON from Qt resource"""
        from PySide6.QtCore import QFile, QIODevice

        file = QFile(resource_path)
        if not file.exists():
            return False

        if file.open(QIODevice.ReadOnly):
            data = file.readAll()
            file.close()

            try:
                json_data = json.loads(data.data().decode('utf-8'))
                return self._parse_json_data(json_data)
            except Exception as e:
                print(f"Error parsing Qt resource {resource_path}: {e}")

        return False

    def _parse_json_data(self, data) -> bool:
        """Parse JSON data into disease info map"""
        if not isinstance(data, list):
            print("JSON root is not an array")
            return False

        new_info = {}

        for item in data:
            if not isinstance(item, dict):
                continue

            class_id = item.get("class_id", -1)
            if class_id < 0:
                continue

            info = DiseaseInfo()
            info.name = item.get("name", "")

            # Handle description (can be string or list)
            description = item.get("description", "")
            if isinstance(description, list):
                info.description = " ".join(description)
            else:
                info.description = description

            # Handle cure (can be string or list)
            cure = item.get("cure", "")
            if isinstance(cure, list):
                info.cure = " ".join(cure)
            else:
                info.cure = cure

            if info.name:
                new_info[class_id] = info

        if new_info:
            self._disease_info = new_info
            return True

        return False

    def get_disease_info(self, class_id: int) -> DiseaseInfo:
        """Get disease info for class ID"""
        return self._disease_info.get(class_id, DiseaseInfo())

    def get_disease_name(self, class_id: int) -> str:
        """Get disease name for class ID"""
        return self._disease_info.get(class_id, DiseaseInfo()).name

    def get_disease_description(self, class_id: int) -> str:
        """Get disease description for class ID"""
        return self._disease_info.get(class_id, DiseaseInfo()).description

    def get_disease_cure(self, class_id: int) -> str:
        """Get disease cure for class ID"""
        return self._disease_info.get(class_id, DiseaseInfo()).cure

    def available_languages(self) -> List[str]:
        """Get list of available languages"""
        # You can scan the resources directory for available languages
        return ["en", "ny"]

    def current_language(self) -> str:
        """Get current language code"""
        return self._current_language

    @classmethod
    def instance(cls):
        """Get singleton instance"""
        return cls()
