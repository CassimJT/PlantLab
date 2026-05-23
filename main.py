# This Python file uses the following encoding: utf-8
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType
import rc_resource


# Core controllers
from src.core.controllers.FileSystemController import FileSystemController
from src.core.controllers.DatasetProcessor import DatasetProcessor

# Model engineering
from src.core.model_engineering.ModelDownloader import ModelDownloader
from src.core.model_engineering.ModelConverter import ModelConverter
from src.core.model_engineering.ModelTrainer import ModelTrainer
from src.core.model_engineering.ModelListModel import ModelListModel
from src.core.model_engineering.ModelScanner import ModelScanner

# Device management
from src.core.devices.MQTTClient import MQTTClient
from src.core.devices.PNDDevice import PNDDevice
from src.core.devices.PNDDeviceModel import PNDDeviceModel
from src.core.devices.PNDDeviceConfigurator import PNDDeviceConfigurator
from src.core.devices.PNDTopics import PNDTopics
from src.core.devices.DeviceState import DeviceState

# Inference modules
from src.core.infarence.InfarenceRunner import InfarenceRunner
from src.core.infarence.DiseaseInfoManager import DiseaseInfoManager
from src.core.rtsp.RTSVideoOutput import RTSVideoOutput

# Researcher statistics modules
from src.core.research.ApiClient import ApiClient
from src.core.research.DataService import DataService
from src.core.research.StatisticalAnalyzer import StatisticalAnalyzer, PlotDataModel
from src.core.research.FieldDataExplorer import FieldDataExplorer
from src.core.research.FieldDataset import FieldDataset

# Appsettings
from src.core.Utils.AppSettings import AppSettings

import PySide6
import os


if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # ======================================
    # Existing Initializations
    # ======================================
    fileController = FileSystemController()
    modelDownloader = ModelDownloader()
    modelConverter = ModelConverter()
    modelTrainer = ModelTrainer()

    scanner = ModelScanner()
    model_list = ModelListModel()
    model_list.set_scanner(scanner)

    datasetProcessor = DatasetProcessor(fileSystemController=fileController)

    # ======================================
    # Device Management
    # ======================================
    mqtt_client = MQTTClient()
    device_configurator = PNDDeviceConfigurator()
    device_configurator.setMqttBroker("192.168.8.130", 1883)
    device_model = device_configurator.deviceModel

    # ======================================
    # Initialize Inference System
    # ======================================
    disease_info_manager = DiseaseInfoManager.instance()
    disease_info_manager.load_language("en")

    infarence_runner = InfarenceRunner()
    available_frameworks = infarence_runner.available_frameworks

    # ======================================
    # Researcher Statistics System
    # ======================================

    # Single source of truth for all field data
    field_dataset = FieldDataset()

    # Plot model for 3D visualizations (bar, surface, scatter)
    plot_model = PlotDataModel()

    # API client for backend communication
    researcher_api_client = ApiClient()
    researcher_api_client.setBaseUrl("https://plantdoctor-api.onrender.com/api/inference")

    # Data service for API requests/responses
    data_service = DataService(researcher_api_client)

    # Statistical analyzer - reads from FieldDataset, writes to PlotModel
    statistical_analyzer = StatisticalAnalyzer(
        fieldDataset=field_dataset,
        plotModel=plot_model
    )

    # Field data explorer for data management and export
    field_data_explorer = FieldDataExplorer(dataService=data_service)

    # ======================================
    # Signal Connections (Data Flow)
    # ======================================
    # API data flows into single source of truth
    data_service.inferencesFetched.connect(field_dataset.loadRecords)
    data_service.inferencesFetched.connect(field_data_explorer.loadFieldData)

    # Appsetting (Singleton)
    settings = AppSettings.instance()

    # Error handling
    data_service.errorOccurred.connect(lambda msg: print(f"Data Service Error: {msg}"))
    statistical_analyzer.analysisError.connect(lambda name, msg: print(f"Analysis Error ({name}): {msg}"))

    # ======================================
    # Expose Objects to QML
    # ======================================

    # Existing exports
    engine.rootContext().setContextProperty("fileController", fileController)
    engine.rootContext().setContextProperty("DatasetProcessor", datasetProcessor)
    engine.rootContext().setContextProperty("ModelDownloader", modelDownloader)
    engine.rootContext().setContextProperty("ModelTransformer", modelConverter)
    engine.rootContext().setContextProperty("ModelTrainer", modelTrainer)
    engine.rootContext().setContextProperty("ModelScanner", scanner)
    engine.rootContext().setContextProperty("ModelList", model_list)

    # Device management exports
    engine.rootContext().setContextProperty("DeviceConfigurator", device_configurator)
    engine.rootContext().setContextProperty("DeviceModel", device_model)
    engine.rootContext().setContextProperty("MQTTClient", mqtt_client)
    engine.rootContext().setContextProperty("DeviceState", DeviceState)

    # Inference system exports
    engine.rootContext().setContextProperty("InfarenceRunner", infarence_runner)
    engine.rootContext().setContextProperty("DiseaseInfoManager", disease_info_manager)
    engine.rootContext().setContextProperty("AvailableFrameworks", available_frameworks)

    # Researcher statistics exports
    engine.rootContext().setContextProperty("ResearcherApiClient", researcher_api_client)
    engine.rootContext().setContextProperty("ResearcherDataService", data_service)

    # Single source of truth
    engine.rootContext().setContextProperty("FieldDataset", field_dataset)
    engine.rootContext().setContextProperty("FieldDatasetListModel", field_dataset.listModel)

    # Statistics and visualization
    engine.rootContext().setContextProperty("StatisticalAnalyzer", statistical_analyzer)
    engine.rootContext().setContextProperty("PlotModel", plot_model)

    # Data management
    engine.rootContext().setContextProperty("FieldDataExplorer", field_data_explorer)

    # RTSP system
    qmlRegisterType(RTSVideoOutput, "RTSVideoOutput", 1, 0, "RTSVideoOutput")

    # AppSettings
    engine.rootContext().setContextProperty("AppSettings", settings)
    # ======================================
    # Load QML
    # ======================================

    qml_import_path = os.path.join(os.path.dirname(PySide6.__file__), "qml")
    engine.addImportPath(qml_import_path)

    print("QML Import Path:", qml_import_path)
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())