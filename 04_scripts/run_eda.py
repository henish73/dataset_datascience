import pandas as pd
import numpy as np

def run_eda():
    file_path = r"s:\MISSION FIELD\AI - ALGOMA\FINAL PROJECT\DATABASE\data\output\ai_labor_paradox_ultimate_gist.csv"
    df = pd.read_csv(file_path)
    
    print("--- TASK 1: UNIVARIATE ANALYSIS ---")
    print("\n[Distribution: Sector]")
    print(df['sector'].value_counts(normalize=True))
    print("\n[Distribution: Displacement Occurred]")
    print(df['displacement_occurred'].value_counts(normalize=True))
    print("\n[Distribution: Overall Risk Category]")
    print(df['overall_risk_category'].value_counts(normalize=True))
    
    df_exposed = df[df['theoretical_exposure_pct'] > 70]
    density = df_exposed.groupby('sector').size() / df.groupby('sector').size()
    top_3_risk = density.sort_values(ascending=False).head(3)
    print("\n[Volume of Risk: Top 3 Sectors (>70% exposure density)]")
    print(top_3_risk)
    
    print("\n--- TASK 2: BIVARIATE ANALYSIS ---")
    print("\n[The Salary Paradox: Salary Bin vs Displacement]")
    df['salary_bin'] = pd.qcut(df['annual_salary_usd'], q=4, labels=['Q1(Low)', 'Q2', 'Q3', 'Q4(High)'])
    print(df.groupby('salary_bin')['displacement_occurred'].mean())
    corr_salary = df['annual_salary_usd'].corr(df['displacement_occurred'])
    print(f"Point-biserial correlation (Salary vs Displacement): {corr_salary:.4f}")
    
    print("\n[The Skill Shield: Education Mismatch vs Displacement]")
    corr_gap = df['education_mismatch_idx'].corr(df['displacement_occurred'])
    print(f"Correlation (Education Mismatch vs Displacement): {corr_gap:.4f}")
    df['gap_size'] = pd.qcut(df['education_mismatch_idx'], q=4, labels=['Low Gap', 'Mid-Low', 'Mid-High', 'High Gap'])
    print(df.groupby('gap_size')['displacement_occurred'].mean())
    
    print("\n--- TASK 3: MULTIVARIATE 'RED ZONES' ---")
    print("\n[Interaction: Remote + Codifiability -> Displacement]")
    df['high_codif'] = df['task_codifiability_score'] > 0.6
    print(df.groupby(['is_remote_eligible', 'high_codif'])['displacement_occurred'].mean())
    
    print("\n[Statistical Red Zone Calculation]")
    mask_red_zone = (df['is_remote_eligible'] == 1) & (df['skill_transferability_score'] < 0.4) & (df['org_ai_maturity_stage'] >= 4)
    if mask_red_zone.sum() > 0:
        red_zone_rate = df.loc[mask_red_zone, 'displacement_occurred'].mean()
        print(f"Red Zone Displacement Rate (Remote + Low Skill Transf + High Maturity Org): {red_zone_rate:.4f} (Count: {mask_red_zone.sum()})")
    else:
        print("No workers fall into this highly specific Red Zone criteria.")

    print("\n--- TASK 4: SYNTHESIS ---")
    print("\n[Top 5 Most Resilient Roles]")
    top_resilient = df.sort_values(by=['resilience_score', 'demand_growth_yoy_pct'], ascending=[False, False])
    print(top_resilient[['job_title', 'sector', 'resilience_score', 'demand_growth_yoy_pct', 'displacement_occurred']].drop_duplicates(subset=['job_title']).head(5).to_string(index=False))
    
    print("\n[K-Shaped Trajectory Contrasts]")
    mask_orchestrators = (df['is_senior'] == 1) & (df['annual_salary_usd'] > 120000)
    mask_middle = (df['job_zone'].isin([3, 4])) & (df['is_senior'] == 0)
    
    orch_disp = df.loc[mask_orchestrators, 'displacement_occurred'].mean()
    mid_disp = df.loc[mask_middle, 'displacement_occurred'].mean()
    print(f"Strategic Orchestrators (Senior, >$120k) Displacement Rate: {orch_disp:.4f} (Count: {mask_orchestrators.sum()})")
    print(f"Middle-Management Coordinators (Zone 3/4, non-Senior) Displacement Rate: {mid_disp:.4f} (Count: {mask_middle.sum()})")
    
    print("\n--- ANOMALIES DETECTION ---")
    anomaly_mask = (df['theoretical_exposure_pct'] > 85) & (df['displacement_occurred'] == 0)
    print(f"High Risk (>85% exposure) but not displaced: {anomaly_mask.sum()} records.")
    anomaly_df = df[anomaly_mask]
    if len(anomaly_df) > 0:
        print("Anomaly examples:")
        print(anomaly_df[['job_title', 'skills_cloud', 'skills_deep_learning', 'annual_salary_usd', 'job_zone', 'is_senior']].head(3).to_string(index=False))

if __name__ == "__main__":
    run_eda()
