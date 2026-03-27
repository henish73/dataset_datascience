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

def is_coordinator(title):
    t = str(title).lower()
    # middle-management / coordinators
    return any(x in t for x in ['manager', 'coordinator', 'supervisor', 'lead', 'head'])

def is_orchestrator(title):
    t = str(title).lower()
    # senior "orchestrators"
    return any(x in t for x in ['director', 'executive', 'chief', 'president', 'vp', 'partner', 'principal'])

def generate_master_dataset():
    work_dir = r"s:\MISSION FIELD\AI - ALGOMA\FINAL PROJECT\DATABASE"
    occ_data_path = os.path.join(work_dir, "CODE", "O .NET DATABASE", "Occupation Data.csv")
    work_act_path = os.path.join(work_dir, "CODE", "O .NET DATABASE", "Work Activities.csv")

    print("Loading O*NET data...")
    try:
        df_occ = pd.read_csv(occ_data_path)
    except FileNotFoundError:
        print(f"File not found: {occ_data_path}")
        return

    try:
        df_act = pd.read_csv(work_act_path)
    except FileNotFoundError:
        print(f"File not found: {work_act_path}")
        return

    # Process Work Activities to create a base task_codifiability_score for each SOC code
    # Focus on 'Data Value' to represent some intensity. We'll group by SOC Code and average the Data Values.
    # To be realistic to "codifiability", we will filter by activities that sound computer/rule based.
    # But since we don't know the exact element names, taking the average of all Data Values and normalizing to [0,1] works as a proxy.
    print("Processing Work Activities...")
    if 'Data Value' in df_act.columns and 'O*NET-SOC Code' in df_act.columns:
        act_grouped = df_act.groupby('O*NET-SOC Code')['Data Value'].mean().reset_index()
        # Normalize Data Value (O*NET usually uses 1-5 or 1-7 scale)
        max_val = act_grouped['Data Value'].max()
        act_grouped['base_codifiability'] = act_grouped['Data Value'] / max_val
        codifiability_dict = dict(zip(act_grouped['O*NET-SOC Code'], act_grouped['base_codifiability']))
    else:
        codifiability_dict = {}

    print("Synthesizing records...")
    num_records = 5000
    
    # 15 placeholder sectors based on previous prompt + averages
    sector_stats = {
        "Office Support": {"exp_mean": 75.5, "aug_mean": 20.0, "remote_prob": 0.8},
        "Construction": {"exp_mean": 8.9, "aug_mean": 10.0, "remote_prob": 0.05},
        "Legal": {"exp_mean": 44.0, "aug_mean": 40.0, "remote_prob": 0.6},
        "Architecture & Engineering": {"exp_mean": 10.0, "aug_mean": 30.0, "remote_prob": 0.4},
        "Life/Physical Science": {"exp_mean": 15.0, "aug_mean": 30.0, "remote_prob": 0.3},
        "Business & Financial": {"exp_mean": 35.0, "aug_mean": 40.0, "remote_prob": 0.8},
        "Management": {"exp_mean": 15.0, "aug_mean": 25.0, "remote_prob": 0.7},
        "Sales": {"exp_mean": 20.0, "aug_mean": 35.0, "remote_prob": 0.5},
        "Technology/Computer": {"exp_mean": 25.0, "aug_mean": 50.0, "remote_prob": 0.9},
        "Healthcare Practitioners": {"exp_mean": 12.0, "aug_mean": 20.0, "remote_prob": 0.2},
        "Education": {"exp_mean": 15.0, "aug_mean": 25.0, "remote_prob": 0.4},
        "Arts & Design": {"exp_mean": 25.0, "aug_mean": 35.0, "remote_prob": 0.7},
        "Protective Service": {"exp_mean": 5.0, "aug_mean": 10.0, "remote_prob": 0.05},
        "Food Service": {"exp_mean": 2.0, "aug_mean": 5.0, "remote_prob": 0.01},
        "Production": {"exp_mean": 15.0, "aug_mean": 15.0, "remote_prob": 0.1}
    }

    # Use valid O*NET codes 
    valid_occupations = df_occ.to_dict('records')
    sampled_occupations = [random.choice(valid_occupations) for _ in range(num_records)]

    data = []
    
    for i, occ in enumerate(sampled_occupations):
        emp_id = 10001 + i
        soc_code = occ.get('O*NET-SOC Code', '00-0000.00')
        title = occ.get('Title', '')
        
        sector = assign_sector(title)
        stats = sector_stats[sector]
        
        # Determine organizational maturity stage using Canadian context (~14.5% plan adoption = stages 4 or 5)
        # We will make 4 and 5 comprise ~14.5% of total.
        mat_rand = np.random.rand()
        if mat_rand < 0.145:
            org_maturity = np.random.choice([4, 5])
        else:
            org_maturity = np.random.choice([1, 2, 3])
            
        # Sector averages for exposure and augmentation
        theo_exp = np.clip(np.random.normal(stats['exp_mean'], 10.0), 0.0, 100.0)
        aug_pot = np.clip(np.random.normal(stats['aug_mean'], 8.0), 0.0, 100.0)
        realized_coverage_idx = np.clip(np.random.normal(theo_exp / 100.0, 0.1), 0.0, 1.0)
        
        # Derived from Work Activities dict, or fallback
        base_cod = codifiability_dict.get(soc_code, theo_exp / 100.0)
        task_cod_score = np.clip(np.random.normal(base_cod, 0.1), 0.0, 1.0)
        
        is_remote = np.random.rand() < stats['remote_prob']
        edu_mismatch = np.clip(np.random.normal(np.random.uniform(0.1, 0.9), 0.2), 0.0, 1.0)
        
        # Skill Transferability 
        skill_transf = np.clip(np.random.normal(0.5, 0.25), 0.0, 1.0)
        
        # Construct baseline displacement probability
        # Base factor max ~30% for high theoretical exposure
        base_disp_prob = (theo_exp / 100.0) * 0.3 
        
        # 1. Remote Penalty: If is_remote_eligible is TRUE, risk must be 4x higher.
        if is_remote:
            base_disp_prob *= 4.0
            
        # 2. The Coordination Gap
        # Roles serving as middle-management/coordinators must show higher displacement than senior "orchestrators".
        if is_coordinator(title) and not is_orchestrator(title):
            base_disp_prob *= 1.5  # Positive multiplier for coordinators
        elif is_orchestrator(title):
            base_disp_prob *= 0.5  # Negative multiplier (shield) for orchestrators
            
        # 3. The Skill Shield: High transferability must reduce displacement risk by at least 50%
        # Let's say high is > 0.70
        if skill_transf > 0.70:
            base_disp_prob *= 0.5  # Reduces by 50%

        final_prob = np.clip(base_disp_prob, 0.0, 1.0)
        disp_occurred = bool(np.random.rand() < final_prob)
        
        data.append({
            "emp_id": emp_id,
            "sector": sector,
            "soc_code": soc_code,
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
    csv_path = os.path.join(work_dir, "ai_labor_paradox_masterpiece.csv")
    df.to_csv(csv_path, index=False)
    
    # Assertions and sanity checks
    assert len(df) == num_records, "Row count is incorrect."
    assert len(df.columns) == 12, "Column count is incorrect."
    
    print(f"Data successfully synthesized to {csv_path}")
    print("\nDataset Sample:")
    print(df.head())
    
    print("\nSanity Check: Average Displacement by Remote Status")
    print(df.groupby('is_remote_eligible')['displacement_occurred'].mean())

if __name__ == "__main__":
    generate_master_dataset()
