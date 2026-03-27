from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import os

app = FastAPI(title="2026 Labor Risk Navigator API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the ensemble models globally at startup
MODEL_DIR = os.path.dirname(__file__)
model_xgb = None
model_rf = None
model_mlp = None
explainer = None
ensemble_weights = None

@app.on_event("startup")
def load_models():
    global model_xgb, model_rf, model_mlp, explainer, ensemble_weights
    try:
        model_xgb = joblib.load(os.path.join(MODEL_DIR, "xgb_model.joblib"))
        model_rf = joblib.load(os.path.join(MODEL_DIR, "rf_model.joblib"))
        model_mlp = joblib.load(os.path.join(MODEL_DIR, "mlp_model.joblib"))
        explainer = joblib.load(os.path.join(MODEL_DIR, "shap_explainer.joblib"))
        
        import json
        with open(os.path.join(MODEL_DIR, "model_weights.json"), 'r') as f:
            ensemble_weights = json.load(f)
            
        print(" Ensemble models, weights, and SHAP explainer loaded successfully.")
    except Exception as e:
        print(f"Warning: Error loading models/weights: {e}")

class PredictRequest(BaseModel):
    theoretical_exposure_pct: float
    annual_salary_usd: float
    education_mismatch_idx: float
    is_remote_eligible: int
    task_codifiability_score: float
    skill_transferability_score: float
    org_ai_maturity_stage: int
    chance_of_automation_onet: float
    resilience_score: float
    is_senior: int
    skills_python: int = 0
    skills_cloud: int = 0
    skills_deep_learning: int = 0

@app.post("/predict")
def predict_displacement(req: PredictRequest):
    if not all([model_xgb, model_rf, model_mlp, ensemble_weights]):
        return {"error": "Ensemble models or weights not fully loaded"}

    # Construct dataframe with 13 features
    features_df = pd.DataFrame([{
        'theoretical_exposure_pct': req.theoretical_exposure_pct,
        'annual_salary_usd': req.annual_salary_usd,
        'education_mismatch_idx': req.education_mismatch_idx,
        'is_remote_eligible': req.is_remote_eligible,
        'task_codifiability_score': req.task_codifiability_score,
        'skill_transferability_score': req.skill_transferability_score,
        'org_ai_maturity_stage': req.org_ai_maturity_stage,
        'chance_of_automation_onet': req.chance_of_automation_onet,
        'resilience_score': req.resilience_score,
        'is_senior': req.is_senior,
        'skills_python': req.skills_python,
        'skills_cloud': req.skills_cloud,
        'skills_deep_learning': req.skills_deep_learning
    }])

    # 1. Consensus Prediction (Weighted)
    p1 = float(model_xgb.predict_proba(features_df)[0][1])
    p2 = float(model_rf.predict_proba(features_df)[0][1])
    p3 = float(model_mlp.predict_proba(features_df)[0][1])
    
    avg_probability = (p1 * ensemble_weights['xgb']) + (p2 * ensemble_weights['rf']) + (p3 * ensemble_weights['mlp'])
    risk_pct = avg_probability * 100

    # 2. SHAP Reasoning
    reasoning = "Resilient infrastructure detected."
    top_5_shap = []
    try:
        shap_values = explainer(features_df)
        
        # Extract all values for this prediction
        vals = shap_values.values[0]
        feature_names = features_df.columns
        
        # Pair features with their SHAP values and sort by absolute impact
        feature_impacts = list(zip(feature_names, vals))
        feature_impacts.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Get top 5
        for fname, val in feature_impacts[:5]:
            top_5_shap.append({
                "feature": fname,
                "contribution": float(val)
            })

        # Keep the text reasoning based on the top feature
        top_feature_name, top_contribution = feature_impacts[0]
        if top_contribution > 0:
            reasoning = f"Risk elevation primarily driven by {top_feature_name.replace('_', ' ')} exposure."
        else:
            reasoning = f"Risk mitigated by strong {top_feature_name.replace('_', ' ')} positioning."
            
    except Exception as e:
        print(f"SHAP Error: {e}")

    # Logic for visual feedback
    if risk_pct > 70:
        category = "Critical Displacement Risk"
        zone = "Red Zone"
    elif req.resilience_score > 12 or (req.is_senior == 1 and req.annual_salary_usd > 120000):
        category = "Strategic Orchestrator - Shielded"
        zone = "Green Zone"
    elif risk_pct < 40:
        category = "Safely Embedded"
        zone = "Green Zone"
    else:
        category = "Vulnerable (Middle-Management Squeeze)"
        zone = "Yellow Zone"

    return {
        "displacement_probability_pct": round(risk_pct, 1),
        "resilience_category": category,
        "zone": zone,
        "reasoning_summary": reasoning,
        "top_5_shap": top_5_shap,
        "model_variance": round(abs(p1-p2), 3)
    }

class GapRequest(BaseModel):
    soc_code: str
    current_skills: list[str]

@app.post("/analyze-gap")
def analyze_skill_gap(req: GapRequest):
    DATA_PATH = os.path.join(os.path.dirname(MODEL_DIR), "..", "data", "processed", "ai_labor_paradox_ultimate_gist.csv")
    if not os.path.exists(DATA_PATH):
        return {"error": "Dataset not found"}
    
    df = pd.read_csv(DATA_PATH)
    
    # 1. Resilience Benchmark: 90th percentile of the "Shielded" group (displacement_occurred == 0) for this SOC
    shielded = df[(df['soc_code'] == req.soc_code) & (df['displacement_occurred'] == 0)]
    
    if shielded.empty:
        # Fallback to sector average if SOC-specific shielded group is too small
        sector = df[df['soc_code'] == req.soc_code]['sector'].iloc[0] if not df[df['soc_code'] == req.soc_code].empty else "Management"
        shielded = df[(df['sector'] == sector) & (df['displacement_occurred'] == 0)]

    benchmark = {
        "skills_python": float(shielded['skills_python'].quantile(0.9)),
        "skills_cloud": float(shielded['skills_cloud'].quantile(0.9)),
        "skills_deep_learning": float(shielded['skills_deep_learning'].quantile(0.9)),
        "resilience_score": float(shielded['resilience_score'].quantile(0.9))
    }

    # 2. User Competencies Mapping
    user_competencies = {
        "skills_python": 1.0 if any("python" in s.lower() for s in req.current_skills) else 0.0,
        "skills_cloud": 1.0 if any("cloud" in s.lower() or "aws" in s.lower() or "azure" in s.lower() for s in req.current_skills) else 0.0,
        "skills_deep_learning": 1.0 if any("deep learning" in s.lower() or "neural" in s.lower() or "pytorch" in s.lower() for s in req.current_skills) else 0.0,
        "resilience_score": 5.0 # Baseline for analysis
    }

    # 3. Gap Calculation
    gaps = {k: max(0, benchmark[k] - user_competencies[k]) for k in benchmark}
    
    # 4. Salary Premium Logic (Users in sector with these 3 skills)
    sector = df[df['soc_code'] == req.soc_code]['sector'].iloc[0] if not df[df['soc_code'] == req.soc_code].empty else "Management"
    skilled_group = df[(df['sector'] == sector) & (df['skills_python'] == 1) & (df['skills_cloud'] == 1)]
    avg_salary_skilled = float(skilled_group['annual_salary_usd'].mean()) if not skilled_group.empty else 0
    base_salary_sector = float(df[df['sector'] == sector]['annual_salary_usd'].mean())
    salary_premium = max(0, avg_salary_skilled - base_salary_sector)

    # 5. Substitution Shield Logic
    # Transitioning from high codifiability to shielded roles
    avg_codifiability_shielded = float(shielded['task_codifiability_score'].mean())
    avg_codifiability_all = float(df[df['soc_code'] == req.soc_code]['task_codifiability_score'].mean()) if not df[df['soc_code'] == req.soc_code].empty else 0.5
    codifiability_reduction = max(0, (avg_codifiability_all - avg_codifiability_shielded) / avg_codifiability_all * 100) if avg_codifiability_all > 0 else 0

    # 6. Empirical Flow Logic (Sankey Grounding)
    sector_df = df[df['sector'] == sector]
    displacement_rate = float(sector_df['displacement_occurred'].mean() * 100) if not sector_df.empty else 35.0

    return {
        "benchmark": benchmark,
        "user_competencies": user_competencies,
        "gaps": gaps,
        "salary_premium": round(salary_premium, 2),
        "codifiability_reduction_pct": round(codifiability_reduction, 1),
        "sector_displacement_rate": round(displacement_rate, 1),
        "sector_context": sector
    }

@app.get("/global-risk")
def get_global_risk():
    # Since the generated dataset does not contain city/region granularity,
    # we return static, research-backed averages for the global geographic hotspots.
    hotspots = [
        { "name": "North America", "coordinates": [-100, 40], "risk": 78.0, "status": "Critical" },
        { "name": "Western Europe", "coordinates": [10, 50], "risk": 72.0, "status": "High" },
        { "name": "East Asia", "coordinates": [110, 35], "risk": 84.0, "status": "Hyper-Risk" },
        { "name": "Southeast Asia", "coordinates": [110, 15], "risk": 65.0, "status": "Vulnerable" },
        { "name": "Oceania", "coordinates": [135, -25], "risk": 45.0, "status": "Stable" },
    ]
    return {"hotspots": hotspots}

@app.get("/health")
def health_check():
    return {"status": "ok"}
