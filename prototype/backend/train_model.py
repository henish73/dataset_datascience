import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def train_and_save_model():
    print("Loading AI-Labor Paradox dataset...")
    base_dir = r"s:\MISSION FIELD\AI - ALGOMA\FINAL PROJECT\DATABASE"
    data_path = os.path.join(base_dir, "03_final_data", "ai_labor_paradox_ultimate_gist.csv")
    
    df = pd.read_csv(data_path)
    
    # Top 10 features as requested
    features = [
        'theoretical_exposure_pct',
        'annual_salary_usd',
        'education_mismatch_idx',
        'is_remote_eligible',
        'task_codifiability_score',
        'skill_transferability_score',
        'org_ai_maturity_stage',
        'chance_of_automation_onet',
        'resilience_score',
        'is_senior'
    ]
    
    target = 'displacement_occurred'
    
    print(f"Dataset shape: {df.shape}")
    print("Extracting features and handling nulls...")
    
    X = df[features].fillna(0)
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=2026)
    
    print("Training XGBoost Classifier...")
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        eval_metric='logloss',
        random_state=2026,
        use_label_encoder=False
    )
    
    model.fit(X_train, y_train)
    
    print("Evaluating Model...")
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Accuracy: {acc:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, preds))
    
    model_out = os.path.join(base_dir, "05_simulator_prototype", "backend", "xgboost_model.joblib")
    joblib.dump(model, model_out)
    print(f"\nModel successfully saved to {model_out}")

if __name__ == '__main__':
    train_and_save_model()
