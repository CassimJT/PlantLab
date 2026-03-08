# This Python file uses the following encoding: utf-8
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
import  rc_resource
from src.core.controllers.FileSystemController import FileSystemController
from src.core.controllers.DatasetProcessor import DatasetProcessor
from src.core.model_engineering.ModelDownloader import ModelDownloader


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    fileController = FileSystemController()
    modelDownloader = ModelDownloader()
    # Pass fileController to DatasetProcessor
    datasetProcessor = DatasetProcessor(fileSystemController=fileController)
    engine.rootContext().setContextProperty("fileController", fileController)
    engine.rootContext().setContextProperty("DatasetProcessor", datasetProcessor)
    engine.rootContext().setContextProperty("ModelDownloader", modelDownloader)

    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
