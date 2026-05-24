
# PlantLab Desktop Application

A desktop-based workbench built for agricultural researchers and administrators. **PlantLab** serves as the machine learning engineering, data curation, and analytical powerhouse of the broader **PlantDoctor (EPDDMS)** ecosystem.

While smallholder farmers use the *PlantDoctor Mobile App* for offline diagnostic field captures, **PlantLab** connects to the central **PlantDoctor API** to ingest field telemetry, evaluate localized dataset samples collected from smallholder villages,sofisticated farmer and large estate farmers , and execute model training pipelines.


              │        PlantDoctor Mobile App           │
              │   (Offline Inference & Field Capture)   │
              └────────────────────┬────────────────────┘
                                   │ (Sync Metadata)
                                   ▼
              ┌─────────────────────────────────────────┐
              │            PlantDoctor API              │
              │     (Node.js / Express / MongoDB)       │
              └────────────────────▲────────────────────┘
                                   │
                                   │ (Fetch Data / Push Models)
                                   │
              ┌────────────────────┴────────────────────┐
              │            PlantLab Desktop             │
              │        (Qt / Python ML Pipeline)        │
              └─────────────────────────────────────────┘





## Features & Capabilities

The desktop software explicitly splits actions across two target user classes defined in the system specifications:

### 1. For Agricultural Researchers
* **Field Data Exploration:** Dynamically browse, filter, and visualize synchronized field crop images and background diagnostic metadata uploaded from the field.
* **Statistical Analysis:** Execute descriptive and inferential statistical operations across region-specific crop and disease datasets.
* **Dataset Validation & Labeling:** Inspect crowd-sourced images from local villages, assign definitive diagnostic labels, and isolate high-quality training sets.
* **Training Recommendations:** Tag validated structural collections to be passed down the pipeline for future engine iterations.

### 2. For Administrators (AI Engineers)
* **Model Sourcing:** Fetch pre-trained baseline neural networks from public external model repositories such as Hugging Face.
* **Local Dataset Training:** Execute model training routines leveraging datasets vetted and flagged by researchers.
* **Mobile Compilation & Conversion:** Quantize and convert raw model checkpoints into resource-optimized, mobile-compatible file formats like ONNX and TensorFlow Lite to target local mobile storage constraints.
* **Performance Evaluation & Deployment:** Audit trained performance profiles via deep validation metrics, and remotely deploy approved weights to consumer mobile clients without requiring app reinstalls.


### Note: An agricultural Reseacher can also partake a role of an administrator
they just need to have the technical skills or know how of how to clearly train models with the appropriate data  

## Tech Stack

* **UI Framework:** Qt Framework via **Qt Quick / QML (v2.15)**.
* **Runtime Environments:** Cross-platform deployment supporting Windows, Linux (including Linux Mint), and macOS desktop systems.
* **Core Engine Integration:** Python ML Frameworks (TensorFlow, PyTorch, ONNX Runtime).
* **Ecosystem Connection:** Interfaces natively with the central **PlantDoctor API** via secure HTTP REST APIs.

## System Requirements & Performance Targets

* **Operating System:** Multi-platform target matching desktop runtimes primary in  Linux but it will be made available for OSs like windows | macOS).
* **Database Scale Performance:** Engineered to handle analytical processing across datasets of at least **100,000 unique records** without user-interface latency or degradation.
* **Operational Control Layer:** Access to deep engineering tools (Model Training, Compilations, and Deployments) is strictly limited to authorized accounts carrying administrative credential scopes.

## Workspace Setup & Installation

### Prerequisites
Before spinning up the desktop client application, verify your workspace has the underlying python dependencies, compilers, and framework runtimes installed:

```bash
# For Debian/Ubuntu/Linux Mint systems
sudo apt-get install python3 python3-pip qtdeclarative5-dev qml-module-qtquick-controls2

# Clone the main repository directory
git clone [https://github.com/YourUsername/PlantLab_Desktop.git](https://github.com/YourUsername/PlantLab_Desktop.git)
cd PlantLab_Desktop


