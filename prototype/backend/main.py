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

# Load the model globally at startup
MODEL_PATH = os.path.join(os.path.dirname(__file__), "xgboost_model.joblib")
model = None

@app.on_event("startup")
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("Model loaded successfully.")
    else:
        print(f"Warning: Model not found at {MODEL_PATH}")

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
    if not model:
        return {"error": "Model not loaded"}

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

    # Predict probability of class 1 (displacement occurs)
    probability = float(model.predict_proba(features_df)[0][1])
    
    # Calculate Risk percentage (0-100)
    risk_pct = probability * 100

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
        "zone": zone
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
