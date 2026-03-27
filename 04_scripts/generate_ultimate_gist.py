import pandas as pd
import numpy as np
import random
import os
import math

# 15 sectors means
SECTOR_STATS = {
    "Office Support": {"exp_mean": 75.5, "aug_mean": 20.0, "remote": 0.8},
    "Construction": {"exp_mean": 8.9, "aug_mean": 40.0, "remote": 0.05},
    "Legal": {"exp_mean": 44.0, "aug_mean": 50.0, "remote": 0.6},
    "Architecture & Engineering": {"exp_mean": 10.0, "aug_mean": 70.0, "remote": 0.4},
    "Life/Physical Science": {"exp_mean": 15.0, "aug_mean": 65.0, "remote": 0.3},
    "Business & Financial": {"exp_mean": 35.0, "aug_mean": 55.0, "remote": 0.8},
    "Management": {"exp_mean": 15.0, "aug_mean": 60.0, "remote": 0.7},
    "Sales": {"exp_mean": 20.0, "aug_mean": 45.0, "remote": 0.5},
    "Technology/Computer": {"exp_mean": 25.0, "aug_mean": 80.0, "remote": 0.9},
    "Healthcare Practitioners": {"exp_mean": 12.0, "aug_mean": 40.0, "remote": 0.2},
    "Education": {"exp_mean": 15.0, "aug_mean": 50.0, "remote": 0.4},
    "Arts & Design": {"exp_mean": 25.0, "aug_mean": 60.0, "remote": 0.7},
    "Protective Service": {"exp_mean": 5.0, "aug_mean": 20.0, "remote": 0.05},
    "Food Service": {"exp_mean": 2.0, "aug_mean": 10.0, "remote": 0.01},
    "Production": {"exp_mean": 15.0, "aug_mean": 30.0, "remote": 0.1}
}

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
    return "Office Support"

def get_risk_cat(exp):
    if exp < 25: return "Low"
    if exp < 60: return "Medium"
    if exp < 85: return "High"
    return "Critical"

def generate_ultimate_gist():
    base_dir = r"s:\MISSION FIELD\AI - ALGOMA\FINAL PROJECT\DATABASE"
    
    # Files
    kaggle1_path = os.path.join(base_dir, "01_raw_data", "kaggle", "ai_jobs_market_2025_2026.csv")
    kaggle2_path = os.path.join(base_dir, "01_raw_data", "kaggle", "AI_Job_Market_Trends_2026.csv")
    kaggle3_path = os.path.join(base_dir, "01_raw_data", "kaggle", "ai_job_trends_dataset.csv")
    onet_occ_path = os.path.join(base_dir, "01_raw_data", "onet", "Occupation Data.csv")
    onet_wage_path = os.path.join(base_dir, "01_raw_data", "anthropic", "release_2025_02_10", "wage_data.csv")

    # Load dataframes (using dropna/fillna where necessary to avoid crashes)
    k1 = pd.read_csv(kaggle1_path).to_dict('records') if os.path.exists(kaggle1_path) else []
    k2 = pd.read_csv(kaggle2_path).to_dict('records') if os.path.exists(kaggle2_path) else []
    k3 = pd.read_csv(kaggle3_path).to_dict('records') if os.path.exists(kaggle3_path) else []
    occ = pd.read_csv(onet_occ_path).to_dict('records') if os.path.exists(onet_occ_path) else [{"O*NET-SOC Code": "00-0000.00", "Title": "Generic Worker"}]
    wages = pd.read_csv(onet_wage_path).to_dict('records') if os.path.exists(onet_wage_path) else []
    
    # Ensure some fallback values
    if not k1: k1 = [{"job_category": "Tech", "experience_level": "Mid", "years_of_experience": 5, "education_required": "Bachelors", "city": "Toronto", "country": "Canada", "remote_work": "Hybrid", "company_size": "Large"}]
    if not k2: k2 = [{"skills_python": 1, "skills_sql": 1, "skills_ml": 0, "skills_deep_learning": 0, "skills_cloud": 1, "hiring_urgency": "High", "job_openings": 10}]
    if not k3: k3 = [{"Projected Openings (2030)": 5000, "Gender Diversity (%)": 45}]
    
    # Pre-process ONET dict for quick lookup
    wage_dict = {w['SOCcode']: w for w in wages} if wages else {}

    output = []
    
    print("Synthesizing 5,000 records...")
    for i in range(5000):
        o = random.choice(occ)
        soc = o.get("O*NET-SOC Code", "00-0000.00")
        title = o.get("Title", "Analyst")
        sector = assign_sector(title)
        
        # Base stats
        s_stats = SECTOR_STATS[sector]
        theo_exp = np.clip(np.random.normal(s_stats["exp_mean"], 10.0), 0.0, 100.0)
        aug_pot = np.clip(np.random.normal(s_stats["aug_mean"], 10.0), 0.0, 100.0)
        task_cod_score = np.clip(np.random.normal(theo_exp / 100.0, 0.1), 0.0, 1.0)
        skill_trans_score = np.clip(np.random.normal(0.5, 0.2), 0.0, 1.0)
        realized_cov = np.clip(theo_exp / 100.0 * np.random.uniform(0.5, 0.9), 0.0, 1.0)
        
        # Org Maturity (14.5% distribution for 4 and 5)
        # 1: 30%, 2: 35.5%, 3: 20%, 4: 10%, 5: 4.5%
        rn = random.random()
        if rn < 0.30: org_ai_maturity_stage = 1
        elif rn < 0.655: org_ai_maturity_stage = 2
        elif rn < 0.855: org_ai_maturity_stage = 3
        elif rn < 0.955: org_ai_maturity_stage = 4
        else: org_ai_maturity_stage = 5
        
        # O*NET Metadata mapping
        w_rec = wage_dict.get(soc, {})
        job_zone = w_rec.get("JobZone", random.choice([1, 2, 3, 4, 5]))
        med_salary_onet = w_rec.get("MedianSalary", 60000)
        chance_auto_onet = w_rec.get("ChanceAuto", theo_exp / 100)
        job_forecast_onet = w_rec.get("JobForecast", "Average")
        is_bright = w_rec.get("isBright", 0)
        is_green = w_rec.get("isGreen", 0)

        # Kaggle randomly chosen records
        k1_rec = random.choice(k1)
        k2_rec = random.choice(k2)
        k3_rec = random.choice(k3)

        job_cat = k1_rec.get("job_category", sector)
        industry = k1_rec.get("industry", sector)
        exp_lvl = k1_rec.get("experience_level", "Mid-Level")
        years_exp = k1_rec.get("years_of_experience", 5)
        edu_req = k1_rec.get("education_required", "Bachelor's Degree")
        city = k1_rec.get("city", "Toronto")
        country = k1_rec.get("country", "Canada")
        is_rem_elig = bool(random.random() < s_stats["remote"])
        rem_type = "Remote" if is_rem_elig else "On-site"
        is_rem_friendly = 1 if is_rem_elig else 0
        comp_size = k1_rec.get("company_size", "100-500")

        # Salary logic
        annual_sal = float(k1_rec.get("annual_salary_usd", med_salary_onet))
        if pd.isna(annual_sal): annual_sal = float(med_salary_onet)
        sal_min = annual_sal * 0.8
        sal_max = annual_sal * 1.2
        sal_tier = k1_rec.get("salary_tier", ("High" if annual_sal > 120000 else "Medium"))
        ai_sal_prem = k1_rec.get("ai_salary_premium_pct", random.uniform(0, 15))
        
        # Skills
        s_py = int(k2_rec.get("skills_python", 0))
        s_sql = int(k2_rec.get("skills_sql", 0))
        s_ml = int(k2_rec.get("skills_ml", 0))
        s_dl = int(k2_rec.get("skills_deep_learning", 0))
        s_cl = int(k2_rec.get("skills_cloud", 0))
        req_sk_count = s_py + s_sql + s_ml + s_dl + s_cl + random.randint(1, 4)
        is_llm = 1 if (s_ml == 1 or s_dl == 1) else k1_rec.get("is_llm_role", 0)
        
        # Market Demands
        demand_sc = k1_rec.get("demand_score", random.uniform(40, 100))
        demand_gr = k1_rec.get("demand_growth_yoy_pct", random.uniform(-10, 30))
        hire_urg = k2_rec.get("hiring_urgency", "Normal")
        j_open = k2_rec.get("job_openings", random.randint(1, 100))
        proj_open = k3_rec.get("Projected Openings (2030)", random.randint(100, 10000))
        ben_sc = k1_rec.get("benefits_score_10", random.uniform(5, 10))
        post_y = k1_rec.get("posting_year", 2024)
        post_m = k1_rec.get("posting_month", random.randint(1, 12))
        is_sen = 1 if ("senior" in exp_lvl.lower() or "exec" in exp_lvl.lower()) else 0
        gen_div = k3_rec.get("Gender Diversity (%)", random.uniform(20, 80))

        # Anthropic distributions
        plat_prod = "Claude API" if random.random() > 0.5 else "ChatGPT API"
        clu_name = "Tech_Automation"
        g_name = "North America"
        bls_base = random.randint(10000, 2000000)
        w_age_pop = random.randint(1000000, 50000000)
        s_gdp = random.uniform(1e10, 5e11)
        c_gdp = random.uniform(1e12, 2.5e13)
        cl_ai_idx = np.clip(np.random.normal(50, 15), 0, 100)
        api_idx = np.clip(np.random.normal(45, 20), 0, 100)
        
        t_think = np.random.uniform(0.1, 0.7)
        t_val = np.random.uniform(0.05, 0.3)
        t_learn = np.random.uniform(0.05, 0.2)
        t_dir = np.random.uniform(0.05, 0.3)
        t_iter = np.random.uniform(0.05, 0.4)
        t_feed = np.random.uniform(0.05, 0.2)

        # Ensure fractions sum roughly to 1
        sum_f = t_think + t_val + t_learn + t_dir + t_iter + t_feed
        t_think /= sum_f; t_val /= sum_f; t_learn /= sum_f; t_dir /= sum_f; t_iter /= sum_f; t_feed /= sum_f

        # Engineered
        edu_mis_idx = np.clip(np.random.normal(0.4, 0.2), 0.0, 1.0)
        res_score = (demand_gr * 0.2) + (ai_sal_prem * 0.1)
        ai_impact = get_risk_cat(theo_exp)
        overall_cat = "High Risk" if theo_exp > 60 else ("Medium Risk" if theo_exp > 30 else "Low Risk")

        # target variable Displacement
        # 1. Base prob
        base_prob = np.clip(theo_exp / 100.0, 0.0, 1.0)
        
        # 2. Remote penalty
        if is_rem_elig: base_prob = np.clip(base_prob * 4.0, 0.0, 1.0)
        
        # 3. Coordination Gap
        if int(job_zone) in [3, 4] and is_sen == 0:
            base_prob = np.clip(base_prob * 1.5, 0.0, 1.0)
            
        # 4. Skill Shield
        if s_dl == 1 or s_cl == 1 or is_llm == 1:
            base_prob *= 0.7
            edu_mis_idx = np.clip(edu_mis_idx - 0.2, 0.0, 1.0)
            
        # 5. Salary Paradox
        if annual_sal > 140000 and theo_exp > 70:
            if is_sen == 1 or int(job_zone) == 5:
                # Strategic orchestrator
                base_prob *= 0.3
            else:
                base_prob = np.clip(base_prob * 1.2, 0.0, 1.0)
                
        # 6. Hiring Signal
        if hire_urg == "Low" and theo_exp > 70:
            base_prob = np.clip(0.95 + random.uniform(0, 0.05), 0.0, 1.0)
            
        displacement = int(random.random() < base_prob)

        output.append({
            "emp_id": 10001 + i,
            "sector": sector,
            "soc_code": soc,
            "job_title": title,
            "job_category": job_cat,
            "experience_level": exp_lvl,
            "years_of_experience": int(years_exp) if not pd.isna(years_exp) else 5,
            "education_required": edu_req,
            "city": city,
            "country": country,
            "is_remote_eligible": int(is_rem_elig),
            "remote_type": rem_type,
            "is_remote_friendly": int(is_rem_friendly),
            "company_size": comp_size,
            "annual_salary_usd": round(annual_sal, 2),
            "salary_min_usd": round(sal_min, 2),
            "salary_max_usd": round(sal_max, 2),
            "salary_tier": sal_tier,
            "ai_salary_premium_pct": round(ai_sal_prem, 2),
            "skills_python": s_py,
            "skills_sql": s_sql,
            "skills_ml": s_ml,
            "skills_deep_learning": s_dl,
            "skills_cloud": s_cl,
            "required_skills_count": req_sk_count,
            "is_llm_role": int(is_llm),
            "demand_score": round(demand_sc, 2),
            "demand_growth_yoy_pct": round(demand_gr, 2),
            "hiring_urgency": hire_urg,
            "job_openings": int(j_open),
            "projected_openings_2030": int(proj_open),
            "benefits_score_10": round(ben_sc, 2),
            "posting_year": int(post_y) if not pd.isna(post_y) else 2024,
            "posting_month": int(post_m) if not pd.isna(post_m) else 1,
            "is_senior": is_sen,
            "gender_diversity_pct": round(gen_div, 2),
            "ai_impact_level": ai_impact,
            "theoretical_exposure_pct": round(theo_exp, 2),
            "augmentation_potential_pct": round(aug_pot, 2),
            "realized_coverage_idx": round(realized_cov, 4),
            "task_codifiability_score": round(task_cod_score, 4),
            "skill_transferability_score": round(skill_trans_score, 4),
            "org_ai_maturity_stage": org_ai_maturity_stage,
            "education_mismatch_idx": round(edu_mis_idx, 4),
            "resilience_score": round(res_score, 4),
            "job_zone": int(job_zone) if pd.notna(job_zone) and str(job_zone).isdigit() else 3,
            "median_salary_onet": round(float(med_salary_onet), 2) if not pd.isna(med_salary_onet) else 60000.0,
            "chance_of_automation_onet": round(float(chance_auto_onet), 4) if not pd.isna(chance_auto_onet) else 0.5,
            "bls_employment_baseline": bls_base,
            "working_age_pop_baseline": w_age_pop,
            "claude_ai_adoption_index": round(cl_ai_idx, 2),
            "api_adoption_index": round(api_idx, 2),
            "task_thinking_fraction": round(t_think, 4),
            "task_validation_fraction": round(t_val, 4),
            "task_learning_fraction": round(t_learn, 4),
            "task_directive_fraction": round(t_dir, 4),
            "task_iteration_fraction": round(t_iter, 4),
            "task_feedback_loop_fraction": round(t_feed, 4),
            "job_forecast_onet": job_forecast_onet if not pd.isna(job_forecast_onet) else "Average",
            "is_bright_outlook_onet": int(is_bright) if not pd.isna(is_bright) else 0,
            "is_green_onet": int(is_green) if not pd.isna(is_green) else 0,
            "state_gdp_baseline": round(s_gdp, 2),
            "country_gdp_baseline": round(c_gdp, 2),
            "overall_risk_category": overall_cat,
            "displacement_occurred": displacement
        })

    df = pd.DataFrame(output)
    
    # Validation constraints
    assert len(df) == 5000, "Should generate exactly 5000 records"
    assert len(df.columns) == 65, f"Should generate exactly 65 columns, got {len(df.columns)}"
    
    out_path = os.path.join(base_dir, "03_final_data", "ai_labor_paradox_ultimate_gist.csv")
    df.to_csv(out_path, index=False)
    
    print(df.head())
    print(f"Generated successfully to {out_path}")
    print("Maturity Stages distribution:")
    print(df['org_ai_maturity_stage'].value_counts(normalize=True))

if __name__ == "__main__":
    generate_ultimate_gist()
