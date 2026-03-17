# DiseaseInfoManager.py
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QObject, Signal, QLocale


class InfoCategory(Enum):
    DISEASE = "disease"
    PEST = "pest"


@dataclass
class DiseaseInfo:
    name: str = ""
    description: str = ""
    cure: str = ""
    category: InfoCategory = InfoCategory.DISEASE

    def is_valid(self) -> bool:
        return bool(self.name)


class DiseaseInfoManager(QObject):
    """Singleton manager for disease and pest information in multiple languages"""

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

        # Separate storage for different categories
        self._disease_info: Dict[int, DiseaseInfo] = {}
        self._pest_info: Dict[int, DiseaseInfo] = {}

        self._current_language = "en"
        self._default_language = "en"

        # Resource search paths
        self._resource_paths = self._get_resource_paths()

        # Load default language
        self.load_language(self._default_language)

    def _get_resource_paths(self) -> List[str]:
        """Get possible paths for language resources"""
        paths = []

        # Get the project root directory
        current_file = Path(__file__).resolve()  # src/core/infarence/DiseaseInfoManager.py
        project_root = current_file.parent.parent.parent.parent  # Go up to Plantlab/

        print(f"Project root: {project_root}")

        # Add all possible resource locations
        paths.extend([
            # Your assets directory
            str(project_root / "assets" / "languages"),
            str(project_root / "plantlab" / "assets" / "languages"),

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
        """Load disease and pest information for specified language"""
        print(f"=== Attempting to load language: {language_code} ===")

        # Load diseases
        disease_success = self._load_category(language_code, "diseases", self._disease_info)

        # Load pests
        pest_success = self._load_category(language_code, "pests", self._pest_info)

        if disease_success or pest_success:
            self._current_language = language_code
            self.language_changed.emit(language_code)
            print(f"Language {language_code} loaded - Diseases: {len(self._disease_info)}, Pests: {len(self._pest_info)}")
            return True

        print(f"Failed to load language: {language_code}")
        return False

    def _load_category(self, language_code: str, category: str, storage_dict: Dict) -> bool:
        """Load a specific category (diseases or pests)"""
        filenames = [
            f"{category}_{language_code}.json",
            f"{category}_{language_code.upper()}.json",
            f"{category}_{language_code.lower()}.json"
        ]

        for resource_path in self._resource_paths:
            for filename in filenames:
                file_path = os.path.join(resource_path, filename)
                print(f"Trying {category} path: {file_path}")

                if os.path.exists(file_path):
                    print(f"File exists, attempting to open: {file_path}")
                    if self._load_from_file(file_path, storage_dict, category):
                        print(f"Successfully loaded {len(storage_dict)} {category} entries")
                        return True
                else:
                    qt_path = f":/languages/{filename}"
                    if self._load_from_qt_resource(qt_path, storage_dict, category):
                        print(f"Successfully loaded {len(storage_dict)} {category} entries from Qt resource")
                        return True

        return False

    def _load_from_file(self, file_path: str, storage_dict: Dict, category: str) -> bool:
        """Load and parse JSON from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._parse_json_data(data, storage_dict, category)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return False

    def _load_from_qt_resource(self, resource_path: str, storage_dict: Dict, category: str) -> bool:
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
                return self._parse_json_data(json_data, storage_dict, category)
            except Exception as e:
                print(f"Error parsing Qt resource {resource_path}: {e}")

        return False

    def _parse_json_data(self, data, storage_dict: Dict, category: str) -> bool:
        """Parse JSON data into info map"""
        if not isinstance(data, list):
            print(f"JSON root is not an array for {category}")
            return False

        new_info = {}
        category_enum = InfoCategory.DISEASE if category == "diseases" else InfoCategory.PEST

        for item in data:
            if not isinstance(item, dict):
                continue

            class_id = item.get("class_id", -1)
            if class_id < 0:
                continue

            info = DiseaseInfo()
            info.name = item.get("name", "")
            info.category = category_enum

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
            storage_dict.update(new_info)
            return True

        return False

    def get_disease_info(self, class_id: int) -> DiseaseInfo:
        """Get disease info for class ID"""
        return self._disease_info.get(class_id, DiseaseInfo())

    def get_pest_info(self, class_id: int) -> DiseaseInfo:
        """Get pest info for class ID"""
        return self._pest_info.get(class_id, DiseaseInfo())

    def get_info(self, class_id: int, category: InfoCategory = InfoCategory.DISEASE) -> DiseaseInfo:
        """Get info for specific category"""
        if category == InfoCategory.DISEASE:
            return self._disease_info.get(class_id, DiseaseInfo())
        else:
            return self._pest_info.get(class_id, DiseaseInfo())

    def get_disease_name(self, class_id: int) -> str:
        """Get disease name for class ID"""
        return self._disease_info.get(class_id, DiseaseInfo()).name

    def get_disease_description(self, class_id: int) -> str:
        """Get disease description for class ID"""
        return self._disease_info.get(class_id, DiseaseInfo()).description

    def get_disease_cure(self, class_id: int) -> str:
        """Get disease cure for class ID"""
        return self._disease_info.get(class_id, DiseaseInfo()).cure

    def get_pest_name(self, class_id: int) -> str:
        """Get pest name for class ID"""
        return self._pest_info.get(class_id, DiseaseInfo()).name

    def get_pest_description(self, class_id: int) -> str:
        """Get pest description for class ID"""
        return self._pest_info.get(class_id, DiseaseInfo()).description

    def get_pest_cure(self, class_id: int) -> str:
        """Get pest cure for class ID"""
        return self._pest_info.get(class_id, DiseaseInfo()).cure

    def available_languages(self) -> List[str]:
        """Get list of available languages"""
        # You can scan the resources directory for available languages
        return ["en", "ny"]

    def current_language(self) -> str:
        """Get current language code"""
        return self._current_language

    def get_category_stats(self) -> Dict:
        """Get statistics about loaded categories"""
        return {
            "diseases": len(self._disease_info),
            "pests": len(self._pest_info),
            "language": self._current_language
        }

    @classmethod
    def instance(cls):
        """Get singleton instance"""
        return cls()
