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

@app.on_event("startup")
def load_models():
    global model_xgb, model_rf, model_mlp, explainer
    try:
        model_xgb = joblib.load(os.path.join(MODEL_DIR, "xgb_model.joblib"))
        model_rf = joblib.load(os.path.join(MODEL_DIR, "rf_model.joblib"))
        model_mlp = joblib.load(os.path.join(MODEL_DIR, "mlp_model.joblib"))
        explainer = joblib.load(os.path.join(MODEL_DIR, "shap_explainer.joblib"))
        print(" Ensemble models and SHAP explainer loaded successfully.")
    except Exception as e:
        print(f"Warning: Error loading models: {e}")

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

@app.post("/predict")
def predict_displacement(req: PredictRequest):
    if not all([model_xgb, model_rf, model_mlp]):
        return {"error": "Ensemble models not fully loaded"}

    # Construct dataframe using the exact same feature order
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
        'is_senior': req.is_senior
    }])

    # 1. Consensus Prediction (Average Probabilities)
    p1 = float(model_xgb.predict_proba(features_df)[0][1])
    p2 = float(model_rf.predict_proba(features_df)[0][1])
    p3 = float(model_mlp.predict_proba(features_df)[0][1])
    
    avg_probability = (p1 + p2 + p3) / 3
    risk_pct = avg_probability * 100

    # 2. SHAP Reasoning Summary
    reasoning = "Resilient infrastructure detected."
    try:
        shap_values = explainer(features_df)
        # Get index of top feature contributing to risk
        top_feature_idx = abs(shap_values.values[0]).argmax()
        top_feature_name = features_df.columns[top_feature_idx]
        contribution = shap_values.values[0][top_feature_idx]
        
        if contribution > 0:
            reasoning = f"Risk elevation primarily driven by high {top_feature_name.replace('_', ' ')}."
        else:
            reasoning = f"Risk mitigated by strong {top_feature_name.replace('_', ' ')} counters."
    except Exception as e:
        print(f"SHAP Error: {e}")

    # Business Logic for visual feedback
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
        "model_variance": round(abs(p1-p2), 3) # Confidence metric
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
