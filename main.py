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

# NEW: Researcher statistics modules
from src.core.research.ApiClient import ApiClient
from src.core.research.DataService import DataService
from src.core.research.StatisticalAnalyzer import StatisticalAnalyzer
from src.core.research.FieldDataExplorer import FieldDataExplorer

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

    # Create the scanner
    scanner = ModelScanner()

    # Create the list model
    model_list = ModelListModel()
    model_list.set_scanner(scanner)

    # Pass fileController to DatasetProcessor
    datasetProcessor = DatasetProcessor(fileSystemController=fileController)

    # ======================================
    # Device Management
    # ======================================
    # Create MQTT client (optional - can be created via configurator)
    mqtt_client = MQTTClient()

    # Create device configurator (main device manager)
    device_configurator = PNDDeviceConfigurator()
    device_configurator.setMqttBroker("192.168.8.130", 1883)
    # Set credentials if needed
    # device_configurator.setMqttCredentials("username", "password")

    # Get the device model for QML
    device_model = device_configurator.deviceModel

    # ======================================
    # Initialize Inference System
    # ======================================

    # Initialize DiseaseInfoManager (loads language files)
    disease_info_manager = DiseaseInfoManager.instance()

    # Load default language (English)
    disease_info_manager.load_language("en")

    # Create InfarenceRunner instance
    infarence_runner = InfarenceRunner()

    # Get available frameworks for UI
    available_frameworks = infarence_runner.available_frameworks
    print(f"Available ML frameworks: {available_frameworks}")

    # ======================================
    # NEW: Initialize Researcher Statistics System
    # ======================================

    # Create API client for researcher
    researcher_api_client = ApiClient()

    # Set the base URL for your inference server
    researcher_api_client.setBaseUrl("http://192.168.8.130:5000/api/inference")

    # Create data service with the API client
    data_service = DataService(researcher_api_client)

    # Create statistical analyzer
    statistical_analyzer = StatisticalAnalyzer()

    # Create field data explorer
    field_data_explorer = FieldDataExplorer()

    # Connect data service to analyzer (when data is fetched, load into analyzer)
    data_service.inferencesFetched.connect(statistical_analyzer.loadInferences)

    # Connect data service to field data explorer
    data_service.inferencesFetched.connect(field_data_explorer.loadFieldData)

    # Optional: Connect error handling
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

    # NEW: Researcher statistics exports
    engine.rootContext().setContextProperty("ResearcherApiClient", researcher_api_client)
    engine.rootContext().setContextProperty("ResearcherDataService", data_service)
    engine.rootContext().setContextProperty("StatisticalAnalyzer", statistical_analyzer)
    engine.rootContext().setContextProperty("InferenceListModel", statistical_analyzer.listModel)
    engine.rootContext().setContextProperty("FieldDataExplorer", field_data_explorer)
    engine.rootContext().setContextProperty("FieldDataset", field_data_explorer.dataset)

    # RTSP system
    qmlRegisterType(RTSVideoOutput, "RTSVideoOutput", 1, 0, "RTSVideoOutput")

    # ======================================
    # Load QML
    # ======================================
    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())