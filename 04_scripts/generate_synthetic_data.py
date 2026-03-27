import pandas as pd
import numpy as np
import random
import os

def generate_dataset():
    num_records = 5000
    
    # 15 placeholder sectors based on typical AI exposure research reports
    sectors = [
        {"name": "Office Support", "exp_mean": 75.5, "aug_mean": 20.0, "remote_prob": 0.8},
        {"name": "Construction", "exp_mean": 8.9, "aug_mean": 10.0, "remote_prob": 0.05},
        {"name": "Legal", "exp_mean": 44.0, "aug_mean": 40.0, "remote_prob": 0.6},
        {"name": "Architecture & Engineering", "exp_mean": 10.0, "aug_mean": 30.0, "remote_prob": 0.4},
        {"name": "Life/Physical Science", "exp_mean": 15.0, "aug_mean": 30.0, "remote_prob": 0.3},
        {"name": "Business & Financial", "exp_mean": 35.0, "aug_mean": 40.0, "remote_prob": 0.8},
        {"name": "Management", "exp_mean": 15.0, "aug_mean": 25.0, "remote_prob": 0.7},
        {"name": "Sales", "exp_mean": 20.0, "aug_mean": 35.0, "remote_prob": 0.5},
        {"name": "Technology/Computer", "exp_mean": 25.0, "aug_mean": 50.0, "remote_prob": 0.9},
        {"name": "Healthcare Practitioners", "exp_mean": 12.0, "aug_mean": 20.0, "remote_prob": 0.2},
        {"name": "Education", "exp_mean": 15.0, "aug_mean": 25.0, "remote_prob": 0.4},
        {"name": "Arts & Design", "exp_mean": 25.0, "aug_mean": 35.0, "remote_prob": 0.7},
        {"name": "Protective Service", "exp_mean": 5.0, "aug_mean": 10.0, "remote_prob": 0.05},
        {"name": "Food Service", "exp_mean": 2.0, "aug_mean": 5.0, "remote_prob": 0.01},
        {"name": "Production", "exp_mean": 15.0, "aug_mean": 15.0, "remote_prob": 0.1}
    ]

    data = []
    
    # Ensure exactly 5000 unique records
    for i in range(num_records):
        emp_id = 10001 + i
        sector_info = random.choice(sectors)
        sector = sector_info['name']
        
        # Normal distribution centered on sector means
        theo_exp = np.clip(np.random.normal(sector_info['exp_mean'], 10.0), 0.0, 100.0)
        aug_pot = np.clip(np.random.normal(sector_info['aug_mean'], 8.0), 0.0, 100.0)
        
        realized_coverage_idx = np.clip(np.random.normal(theo_exp / 100.0, 0.1), 0.0, 1.0)
        
        is_remote = np.random.rand() < sector_info['remote_prob']
        
        skill_transf = np.clip(np.random.normal(0.5, 0.2), 0.0, 1.0)
        
        org_maturity = np.random.randint(1, 6)
        
        task_cod_score = np.clip(np.random.normal(theo_exp / 100.0, 0.15), 0.0, 1.0)
        
        edu_mismatch = np.clip(np.random.normal(np.random.uniform(0.1, 0.9), 0.2), 0.0, 1.0)
        
        # Base probability calculation logic
        base_disp_prob = (theo_exp / 100.0) * 0.1  # Set a base factor, e.g. 10% max baseline
        
        # Logical Constraints:
        # The Remote Penalty: 4x higher probability
        if is_remote:
            base_disp_prob *= 4.0
            
        # The Maturity Multiplier: increase probability by 30% if org is at stage 4 or 5
        if org_maturity in [4, 5]:
            base_disp_prob *= 1.3
            
        # The Skill Shield: skill transferability > 0.7 lowers chance significantly
        if skill_transf > 0.7:
            base_disp_prob *= 0.2
            
        final_prob = np.clip(base_disp_prob, 0.0, 1.0)
        disp_occurred = bool(np.random.rand() < final_prob)
        
        data.append({
            "emp_id": emp_id,
            "sector": sector,
            "theoretical_exposure_pct": round(theo_exp, 2),
            "augmentation_potential_pct": round(aug_pot, 2),
            "realized_coverage_idx": round(realized_coverage_idx, 4),
            "is_remote_eligible": is_remote,
            "skill_transferability_score": round(skill_transf, 4),
            "org_ai_maturity_stage": org_maturity,
            "task_codifiability_score": round(task_cod_score, 4),
            "education_mismatch_idx": round(edu_mismatch, 4),
            "displacement_occurred": disp_occurred
        })
        
    df = pd.DataFrame(data)
    csv_path = "ai_labor_paradox_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"Data generated successfully at {os.path.abspath(csv_path)}")

if __name__ == "__main__":
    generate_dataset()
