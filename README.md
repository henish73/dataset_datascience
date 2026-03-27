# 🛰️ The AI-Labor Paradox Simulator (2024–2026)
### *A Multi-Model Research Decision Support System*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-310+-blue.svg)](https://www.python.org/downloads/)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production-009688.svg)](https://fastapi.tiangolo.com/)

---

## 📖 Overview
**The AI-Labor Paradox Simulator** is a high-fidelity econometric modeling platform designed to forecast labor market displacement and resilience trends through 2026. Grounded in **O*NET** occupational data and weighted by **WEF/OECD** trends, the system leverages a **Consensus Ensemble** (XGBoost, Random Forest, MLP) to help users navigate the "K-Shaped" digital economic transition.

---

## 📂 Gold Standard Project Structure
The repository is organized following a strict **Lifecycle-Linked Taxonomy**:

```bash
├── 📁 data/
│   ├── 📁 raw/               # Original O*NET, Kaggle, and StatCan datasets
│   └── 📁 processed/         # Master econometric masterpiece (ai_labor_paradox_ultimate_gist.csv)
├── 📁 notebooks/             # Exploratory Data Analysis (EDA) and Model Training labs
├── 📁 scripts/               # Core data generators and automated econometric pipelines
├── 📁 prototype/
│   ├── 📁 backend/           # FastAPI Suite: Ensemble models + SHAP Reasoning
│   └── 📁 frontend/          # Vite/React "Command Center" Dashboard
├── 📁 docs/
│   ├── 📁 reports/           # PDF exports of Section 3 Analysis & EDA reports
│   └── 📁 research/          # Underlying WEF/StatCan academic grounding papers
└── 📄 README.md              # Project Manifesto & Navigation Guide
```

---

## 🧠 Core Engineering Architecture

### **1. Consensus Predictive Suite (Backend/Production)**
The simulator moves beyond single-point probability to a production-ready **Weighted Consensus Ensemble**:
- **Dynamic Weighting**: The `/predict` engine calculates probabilities using weighted averages derived from cross-validation precision (`XGBoost: ~41%`, `Random Forest: ~29%`, `MLP: ~29%`).
- **Explainable AI (SHAP)**: Granular, real-time "Reasoning Summaries" identifying the top 5 raw feature drivers pushing the risk percentage up or down for every prediction.
- **Production Reliability**: Ensemble weights and SHAP explainers are saved as serialized artifacts during training for lighting-fast API inference.

### **2. The Command Center (Frontend)**
A futuristic, dark-mode dashboard providing multi-dimensional insights:
- **Skill Gap Radar**: Capability benchmarking against "Strategic Orchestrator" benchmarks.
- **K-Shape Scatter Plot**: Interactive correlation between Salary, Risk, and Resilience.
- **Geographic Impact Heatmap**: Global displacement vulnerability visualizations.
- **Research Library**: A searchable context database of 2026 econometric findings.

---

## 🚀 Quick Start (Production Execution)

### **Local Deployment**
1. **Clone & Setup Environment:**
   ```bash
   git clone [repository-url]
   cd database
   pip install -r requirements.txt
   ```

2. **Run Inference Engine:**
   ```bash
   cd prototype/backend
   python main.py
   ```

3. **Launch Dashboard:**
   ```bash
   cd prototype/frontend
   npm install --legacy-peer-deps
   npm run dev
   ```

### **Docker Orchestration (Recommended)**
```bash
docker-compose up --build
```

---

## 📊 Methodology & Grounding
This project implements a **Triple-Pass Grounding** approach:
1. **O*NET Base**: 45 unique task-based datasets establishing baseline automation probability.
2. **Economic weighting**: Applying Salary and Remote-Eligibility multipliers derived from **2025 WEF Forecasts**.
3. **Synthesis**: Final econometric Masterpiece CSV incorporating the "Remote Penalty" and "Skill Shielding" logic.

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
**Developed for the 2024–2026 Labor Market Synthesis Research.**
