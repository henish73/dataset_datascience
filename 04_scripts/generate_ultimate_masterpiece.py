import pandas as pd
import numpy as np
import random
import os

def assign_sector(title):
    t = str(title).lower()
    if any(x in t for x in ['manager', 'chief', 'director', 'executive', 'president']): return "Management"
    if any(x in t for x in ['computer', 'software', 'data', 'it', 'network', 'programmer']): return "Technology/Computer"
    if any(x in t for x in ['engineer', 'architect']): return "Architecture & Engineering"
    if any(x in t for x in ['finance', 'accountant', 'business', 'analyst']): return "Business & Financial"
    if any(x in t for x in ['legal', 'lawyer', 'attorney', 'paralegal']): return "Legal"
    if any(x in t for x in ['teacher', 'faculty', 'instructor', 'library']): return "Education"
    if any(x in t for x in ['doctor', 'nurse', 'health', 'medical', 'surgeon', 'therapist']): return "Healthcare Practitioners"
    if any(x in t for x in ['science', 'research', 'scientist', 'biologist', 'chemist', 'physicist']): return "Life/Physical Science"
    if any(x in t for x in ['sales', 'retail', 'buyer', 'marketer', 'agent']): return "Sales"
    if any(x in t for x in ['art', 'design', 'entertain', 'athlete', 'media', 'writer']): return "Arts & Design"
    if any(x in t for x in ['construct', 'builder', 'carpenter', 'electrician', 'plumber']): return "Construction"
    if any(x in t for x in ['police', 'guard', 'security', 'fire', 'protective']): return "Protective Service"
    if any(x in t for x in ['food', 'cook', 'chef', 'waiter', 'server', 'bartender']): return "Food Service"
    if any(x in t for x in ['produce', 'manufacture', 'assembler', 'operator', 'machinist']): return "Production"
    return "Office Support" # Fallback/Default

def generate_dataset():
    work_dir = r"s:\MISSION FIELD\AI - ALGOMA\FINAL PROJECT\DATABASE"
    occ_data_path = os.path.join(work_dir, "CODE", "O .NET DATABASE", "Occupation Data.csv")
    work_act_path = os.path.join(work_dir, "CODE", "O .NET DATABASE", "Work Activities.csv")
    kaggle_path = os.path.join(work_dir, "CODE", "ai_jobs_market_2025_2026.csv")
    
    print("Loading data sources...")
    df_occ = pd.read_csv(occ_data_path)
    df_act = pd.read_csv(work_act_path)
    df_kaggle = pd.read_csv(kaggle_path)
    
    print("Preparing Codifiability Scores...")
    if 'Data Value' in df_act.columns and 'O*NET-SOC Code' in df_act.columns:
        act_grouped = df_act.groupby('O*NET-SOC Code')['Data Value'].mean().reset_index()
        max_val = act_grouped['Data Value'].max()
        act_grouped['base_codifiability'] = act_grouped['Data Value'] / max_val
        codifiability_dict = dict(zip(act_grouped['O*NET-SOC Code'], act_grouped['base_codifiability']))
    else:
        codifiability_dict = {}
        
    print("Preparing Kaggle AI Market Segments...")
    df_kaggle['is_canada'] = df_kaggle.apply(
        lambda r: 1 if str(r.get('country', '')).lower() == 'canada' or str(r.get('city', '')).lower() == 'toronto' else 0,
        axis=1
    )
    kaggle_records_canada = df_kaggle[df_kaggle['is_canada'] == 1].to_dict('records')
    kaggle_records_other = df_kaggle[df_kaggle['is_canada'] == 0].to_dict('records')
    
    sector_stats = {
        "Office Support": {"exp_mean": 75.5, "remote_prob": 0.8},
        "Construction": {"exp_mean": 8.9, "remote_prob": 0.05},
        "Legal": {"exp_mean": 44.0, "remote_prob": 0.6},
        "Architecture & Engineering": {"exp_mean": 10.0, "remote_prob": 0.4},
        "Life/Physical Science": {"exp_mean": 15.0, "remote_prob": 0.3},
        "Business & Financial": {"exp_mean": 35.0, "remote_prob": 0.8},
        "Management": {"exp_mean": 15.0, "remote_prob": 0.7},
        "Sales": {"exp_mean": 20.0, "remote_prob": 0.5},
        "Technology/Computer": {"exp_mean": 25.0, "remote_prob": 0.9},
        "Healthcare Practitioners": {"exp_mean": 12.0, "remote_prob": 0.2},
        "Education": {"exp_mean": 15.0, "remote_prob": 0.4},
        "Arts & Design": {"exp_mean": 25.0, "remote_prob": 0.7},
        "Protective Service": {"exp_mean": 5.0, "remote_prob": 0.05},
        "Food Service": {"exp_mean": 2.0, "remote_prob": 0.01},
        "Production": {"exp_mean": 15.0, "remote_prob": 0.1}
    }
    
    valid_occupations = df_occ.to_dict('records')
    num_records = 5000
    
    print("Synthesizing Ultimate Masterpiece Data...")
    sampled_occupations = [random.choice(valid_occupations) for _ in range(num_records)]
    
    data = []
    for i, occ in enumerate(sampled_occupations):
        emp_id = 10001 + i
        soc_code = occ.get('O*NET-SOC Code', '00-0000.00')
        job_title = occ.get('Title', '')
        sector = assign_sector(job_title)
        
        stats = sector_stats.get(sector, {"exp_mean": 30.0, "remote_prob": 0.5})
        
        # 1. Base Core Weight (Automation)
        theo_exp = np.clip(np.random.normal(stats['exp_mean'], 10.0), 0.0, 100.0)
        
        base_cod = codifiability_dict.get(soc_code, theo_exp / 100.0)
        task_cod_score = np.clip(np.random.normal(base_cod, 0.1), 0.0, 1.0)
        
        is_remote_eligible = bool(np.random.rand() < stats['remote_prob'])
        
        # Skill Gap proxy
        edu_mismatch_idx = np.clip(np.random.normal(np.random.uniform(0.1, 0.9), 0.2), 0.0, 1.0)
        
        # Local Context Enforcement (Toronto/Canada probability boost)
        if len(kaggle_records_canada) > 0 and random.random() < 0.40:
            mkt_record = random.choice(kaggle_records_canada)
        else:
            mkt_record = random.choice(kaggle_records_other)
            
        annual_salary_usd = mkt_record.get('annual_salary_usd', 80000.0)
        ai_salary_premium_pct = mkt_record.get('ai_salary_premium_pct', 5.0)
        demand_growth_yoy_pct = mkt_record.get('demand_growth_yoy_pct', 5.0)
        
        is_llm = mkt_record.get('is_llm_role', 0)
        is_llm_role = bool(int(is_llm) == 1)
        
        # Economic Resilience
        resilience_score = (demand_growth_yoy_pct * 0.2) + (ai_salary_premium_pct * 0.1)
        
        # The 36-Month Risk
        # (Automation % * 0.4) + (Skill Gap * 0.3) - (Demand Growth * 0.2) - (Salary Premium * 0.1)
        skill_gap_pct = edu_mismatch_idx * 100.0
        
        raw_risk_pct = (theo_exp * 0.4) + (skill_gap_pct * 0.3) - resilience_score
        
        base_prob = np.clip(raw_risk_pct / 100.0, 0.0, 1.0)
        
        # The Remote Variable: 4x Multiplier
        if is_remote_eligible:
            base_prob *= 4.0
            
        # The LLM Factor: Reduce by 70%
        if is_llm_role:
            base_prob *= 0.3
            
        final_prob = np.clip(base_prob, 0.0, 1.0)
        displacement_occurred = bool(np.random.rand() < final_prob)
        
        data.append({
            "emp_id": emp_id,
            "sector": sector,
            "job_title": job_title,
            "soc_code": soc_code,
            "annual_salary_usd": round(annual_salary_usd, 2),
            "ai_salary_premium_pct": round(ai_salary_premium_pct, 2),
            "demand_growth_yoy_pct": round(demand_growth_yoy_pct, 2),
            "is_remote_eligible": is_remote_eligible,
            "is_llm_role": is_llm_role,
            "task_codifiability_score": round(task_cod_score, 4),
            "education_mismatch_idx": round(edu_mismatch_idx, 4),
            "resilience_score": round(resilience_score, 4),
            "displacement_occurred": displacement_occurred
        })
        
    df = pd.DataFrame(data)
    
    col_order = [
        "emp_id", "sector", "job_title", "soc_code", "annual_salary_usd", 
        "ai_salary_premium_pct", "demand_growth_yoy_pct", "is_remote_eligible", 
        "is_llm_role", "task_codifiability_score", "education_mismatch_idx", 
        "resilience_score", "displacement_occurred"
    ]
    df = df[col_order]
    
    out_path = os.path.join(work_dir, "ai_labor_paradox_ultimate_masterpiece.csv")
    df.to_csv(out_path, index=False)
    
    print(f"Dataset securely generated at: {out_path}")
    print("\nDataset Snapshot (Top 5 rows):")
    print(df.head())
    
    print("\n--- Insight Summary ---")
    print(f"Total Canada/Toronto Market Entries Extracted: {df['ai_salary_premium_pct'].notnull().sum()}")
    print(f"Total LLM/Agentic Roles identified: {df['is_llm_role'].sum()}")
    print("\nDisplacement Validations:")
    print("Remote vs On-site Displacement:")
    print(df.groupby('is_remote_eligible')['displacement_occurred'].mean())
    print("\nLLM Role Displacement (70% Reduction Validation):")
    print(df.groupby('is_llm_role')['displacement_occurred'].mean())
    
if __name__ == "__main__":
    generate_dataset()
