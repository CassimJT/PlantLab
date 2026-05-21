
# PlantLab Desktop Application

A desktop-based workbench built for agricultural researchers and administrators. **PlantLab** serves as the machine learning engineering, data curation, and analytical powerhouse of the broader **PlantDoctor (EPDDMS)** ecosystem.

While smallholder farmers use the *PlantDoctor Mobile App* for offline diagnostic field captures, **PlantLab** connects to the central **PlantDoctor API** to ingest field telemetry, evaluate localized dataset samples collected from smallholder villages, and execute model training pipelines.


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


