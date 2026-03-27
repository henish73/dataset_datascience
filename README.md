# The AI-Labor Paradox (2024–2026)

## Abstract
The AI-Labor Paradox explores the asymmetric displacement of workers as agentic AI systems transition from task-assistance to autonomous orchestration. Our research identifies a definitive **"K-Shaped" divergence**, where high-level Strategic Orchestrators leverage AI for productivity gains while Middle-Management Coordinators face aggressive automation of their core coordination tasks. Most critically, the dataset reveals a **"Remote Danger Multiplier,"** where remote-eligible roles exhibit a 4x higher risk of displacement due to the inherent digital codifiability of their workflows.

---

## 🗺️ Directory Map (Gold Standard)
This repository is organized by lifecycle stage to ensure high-fidelity research and reproducibility.

### 📊 Data Archeology
- **`/data/raw/`**: 45+ Original O*NET CSVs, Kaggle trends, and raw market datasets. (Ground Truth)
- **`/data/processed/`**: The synthesized master dataset (`ai_labor_paradox_ultimate_gist.csv`).
- **`/data/processed/archive/`**: Safekeeping for legacy masterpieces and intermediate data versions.

### 🧪 Research & Analysis
- **`/notebooks/`**: `01_exploratory_data_analysis.ipynb` (Primary visualisation of K-Shaped trends).
- **`/scripts/`**: 
  - `main_data_generator.py`: The unified 65-column econometric grounding engine.
  - **`/scripts/utilities/`**: Auxiliary tools for header extraction, batch EDA, and report generation.

### 📝 Intelligence & Documentation
- **`/docs/research/`**: External benchmarks (StatCan 2026, WEF Future of Jobs 2025).
- **`/docs/reports/`**: Finalized Section 3 Analysis and high-resolution EDA PDF/HTML exports.

### 🚀 Implementation
- **`/prototype/`**: The "2026 Labor Risk Navigator" full-stack dashboard.

---

## ⚡ Quick Start

### 1. Build the Data Engine
Initialize the 5,000-row synthetic masterpayload:
```bash
pip install -r requirements.txt
python scripts/main_data_generator.py
```

### 2. Visualize the Paradox
Run the exploratory suite to generate risk heatmaps:
```bash
jupyter notebook notebooks/01_exploratory_data_analysis.ipynb
```

### 3. Launch the Simulator
Navigate to the prototype directory to run the React + FastAPI dashboard:
```bash
cd prototype/05_simulator_prototype
# Start Backend
python backend/main.py
# Start Frontend
cd frontend && npm run dev
```

---

## 🔍 Data Dictionary (65-Column Schema)
Key features in the `ultimate_gist.csv`:
- **theoretical_exposure_pct**: Base task-based automation risk.
- **is_remote_eligible**: Key multiplier for digital displacement.
- **task_codifiability_score**: Measure of algorithmic substitution potential.
- **displacement_occurred**: Final binary target for ML classification.
- **resilience_score**: Composite of AI-competency and cognitive shielding.
