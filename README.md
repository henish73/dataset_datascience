# The AI-Labor Paradox (2024–2026)

## Abstract
The AI-Labor Paradox explores the asymmetric displacement of workers as agentic AI systems transition from task-assistance to autonomous orchestration. Our research identifies a definitive **"K-Shaped" divergence**, where high-level Strategic Orchestrators leverage AI for productivity gains while Middle-Management Coordinators face aggressive automation of their core coordination tasks. Most critically, the dataset reveals a **"Remote Danger Multiplier,"** where remote-eligible roles exhibit a 4x higher risk of displacement due to the inherent digital codifiability of their workflows.

---

## Data Dictionary (65-Column Schema)
The master dataset (`data/processed/ai_labor_paradox_ultimate_gist.csv`) contains 5,000 records grounded in O*NET occupational benchmarks. Key features include:

- **record_id**: Unique identifier for the simulated worker.
- **soc_code / job_title**: Grounded O*NET Standard Occupational Classification.
- **theoretical_exposure_pct**: Base automation risk derived from task analysis.
- **is_remote_eligible**: Boolean flag indicating if the role can be performed off-site.
- **task_codifiability_score**: Measure of how easily core job functions can be converted to AI logic.
- **displacement_occurred**: Binary target (1 = Displacement, 0 = Resilient).
- **resilience_score**: Composite metric of human-centric soft skills and AI-competency.
- **has_ai_competency**: Flag for workers who have successfully upskilled in Deep Learning/Cloud.
- **meta_features [0-48]**: Synthetic econometric variables for high-dimensional ML training.

---

## Repository Structure
- **`/data/raw/`**: Grounding datasets (O*NET, Kaggle trends, initial research data).
- **`/data/processed/`**: Finalized high-fidelity CSVs and masterpiece versions.
- **`/notebooks/`**: `01_exploratory_data_analysis.ipynb` for visual research findings.
- **`/scripts/`**: Master generation engine (`generate_synthetic_data.py`).
- **`/docs/`**: Finalized research reports (/reports) and reference papers (/references).
- **`/simulator_prototype/`**: Full-stack web dashboard ("2026 Labor Risk Navigator").

---

## Setup & Implementation

### 1. Environment Configuration
Install necessary dependencies for the ML and EDA pipelines:
```bash
pip install -r requirements.txt
```

### 2. Dataset Generation
Run the unified generator to reconstruct the 65-column master dataset using live O*NET grounding:
```bash
python scripts/generate_synthetic_data.py
```

### 3. Exploratory Data Analysis
Open the primary research notebook to visualize the K-Shaped trajectories:
```bash
jupyter notebook notebooks/01_exploratory_data_analysis.ipynb
```

---

## Technical Appendix
This project utilizes an **XGBoost Classifier** for displacement prediction, achieving high precision in identifying the "Statistical Red Zones" created by the Remote Danger Multiplier.
