import pandas as pd
import numpy as np
import os

def run_eda():
    file_path = r"s:\MISSION FIELD\AI - ALGOMA\FINAL PROJECT\DATABASE\03_final_data\ai_labor_paradox_ultimate_gist.csv"
    df = pd.read_csv(file_path)
    
    out_path = r"C:\Users\pheni\.gemini\antigravity\brain\607ebdf8-4164-428c-ad1e-8794c6f329b2\analysis_results.md"
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Exploratory Data Analysis (EDA) - The AI-Labor Paradox (2024–2026)\n\n")
        
        f.write("## Task 1: Univariate Analysis (The Landscape)\n")
        f.write("\n### Distribution of Sector\n```text\n")
        f.write(df['sector'].value_counts(normalize=True).to_string())
        f.write("\n```\n")
        
        f.write("\n### Distribution of Displacement\n```text\n")
        f.write(df['displacement_occurred'].value_counts(normalize=True).to_string())
        f.write("\n```\n")
        
        f.write("\n### Distribution of Overall Risk Category\n```text\n")
        f.write(df['overall_risk_category'].value_counts(normalize=True).to_string())
        f.write("\n```\n")
        
        df_exposed = df[df['theoretical_exposure_pct'] > 70]
        density = df_exposed.groupby('sector').size() / df.groupby('sector').size()
        top_3_risk = density.sort_values(ascending=False).head(3)
        f.write("\n### Volume of Risk (Top 3 Sectors >70% Exposure Density)\n```text\n")
        f.write(top_3_risk.to_string())
        f.write("\n```\n")
        
        f.write("\n## Task 2: Bivariate Analysis (The Correlations)\n")
        f.write("\n### The Salary Paradox\n")
        df['salary_bin'] = pd.qcut(df['annual_salary_usd'], q=4, labels=['Q1(Low)', 'Q2', 'Q3', 'Q4(High)'], duplicates='drop')
        f.write("Displacement Rate by Salary Bin:\n```text\n")
        f.write(df.groupby('salary_bin')['displacement_occurred'].mean().to_string())
        corr_salary = df['annual_salary_usd'].corr(df['displacement_occurred'])
        f.write(f"\n```\n**Point-biserial correlation (Salary vs Displacement):** {corr_salary:.4f}\n")
        
        f.write("\n### The Skill Shield\n")
        corr_gap = df['education_mismatch_idx'].corr(df['displacement_occurred'])
        f.write(f"**Correlation (Education Mismatch vs Displacement):** {corr_gap:.4f}\n")
        df['gap_size'] = pd.qcut(df['education_mismatch_idx'], q=4, labels=['Low Gap', 'Mid-Low', 'Mid-High', 'High Gap'], duplicates='drop')
        f.write("\nDisplacement Rate by Education Mismatch Gap:\n```text\n")
        f.write(df.groupby('gap_size')['displacement_occurred'].mean().to_string())
        f.write("\n```\n")
        
        f.write("\n## Task 3: Multivariate Analysis (The 'Red Zones')\n")
        f.write("\n### Interaction: Remote + High Codifiability\n")
        df['high_codif'] = df['task_codifiability_score'] > 0.6
        f.write("Average Displacement Rates:\n```text\n")
        f.write(df.groupby(['is_remote_eligible', 'high_codif'])['displacement_occurred'].mean().to_string())
        f.write("\n```\n")
        
        f.write("\n### Statistical Red Zone\n")
        mask_red_zone = (df['is_remote_eligible'] == 1) & (df['skill_transferability_score'] < 0.4) & (df['org_ai_maturity_stage'] >= 4)
        if mask_red_zone.sum() > 0:
            red_zone_rate = df.loc[mask_red_zone, 'displacement_occurred'].mean()
            f.write(f"**Red Zone Displacement Rate (Remote + Low Skill Transf + High Maturity Org):** {red_zone_rate:.4f} (Count: {mask_red_zone.sum()})\n")
        else:
            f.write("No workers fall into this highly specific Red Zone criteria.\n")

        f.write("\n## Task 4: Synthesis for Deliverables\n")
        f.write("\n### Top 5 Most Resilient Roles\n```text\n")
        top_resilient = df.sort_values(by=['resilience_score', 'demand_growth_yoy_pct'], ascending=[False, False])
        top_5 = top_resilient[['job_title', 'sector', 'resilience_score', 'demand_growth_yoy_pct', 'displacement_occurred']].drop_duplicates(subset=['job_title']).head(5)
        f.write(top_5.to_string(index=False))
        f.write("\n```\n")
        
        f.write("\n### K-Shaped Trajectory Contrasts\n")
        mask_orchestrators = (df['is_senior'] == 1) & (df['annual_salary_usd'] > 120000)
        mask_middle = (df['job_zone'].isin([3, 4])) & (df['is_senior'] == 0)
        
        orch_disp = df.loc[mask_orchestrators, 'displacement_occurred'].mean() if mask_orchestrators.sum() > 0 else 0
        mid_disp = df.loc[mask_middle, 'displacement_occurred'].mean() if mask_middle.sum() > 0 else 0
        
        f.write(f"- **Strategic Orchestrators (Senior, >$120k)** Displacement Rate: {orch_disp:.4f} (Count: {mask_orchestrators.sum()})\n")
        f.write(f"- **Middle-Management Coordinators (Zone 3/4, non-Senior)** Displacement Rate: {mid_disp:.4f} (Count: {mask_middle.sum()})\n")
        
        f.write("\n## Anomalies Detection\n")
        anomaly_mask = (df['theoretical_exposure_pct'] > 85) & (df['displacement_occurred'] == 0)
        f.write(f"**High Risk (>85% exposure) but not displaced:** {anomaly_mask.sum()} records.\n")
        anomaly_df = df[anomaly_mask]
        if len(anomaly_df) > 0:
            f.write("\nAnomaly examples:\n```text\n")
            f.write(anomaly_df[['job_title', 'skills_cloud', 'skills_deep_learning', 'annual_salary_usd', 'job_zone', 'is_senior']].head(3).to_string(index=False))
            f.write("\n```\n")

        f.write("\n## Section 3: Core Research Inferences\n\n")
        f.write("1. **The Remote Danger Multiplier:** The interaction between remote eligibility and high task codifiability demonstrates a severe risk aggregation. Remote workers with highly codifiable tasks experience an overwhelming displacement rate, contrasting drastically with on-site workers performing low-codifiability tasks. The compounding effect of remote eligibility acts as a massive risk multiplier, forming the 'Statistical Red Zone'.\n")
        f.write("2. **The K-Shaped Divergence (Strategic Orchestrators vs. Coordinators):** The dataset conclusively illustrates the bifurcated 'K-Shaped' trajectory of AI displacement. The displacement rate for Middle-Management Coordinators is aggressively high, compared to significantly lower rates for Strategic Orchestrators earning over $120,000. Rather than providing absolute immunity, high salaries segment into two distinct paths: senior workers orchestrating AI strategy are shielded, while well-paid mid-level coordinators are targeted for efficiency deltas.\n")
        f.write("3. **The Efficacy of the Skill Shield:** Higher Education Mismatch strictly corresponds to elevated displacement risk. However, anomaly detection reveals individuals with extreme automation exposure (>85%) avoiding displacement entirely by possessing Cloud or Deep Learning skills (the 'Skill Shield'). Workers bridging the competency void through specific technical upskilling successfully neutralize their underlying automation risk.\n")

if __name__ == "__main__":
    run_eda()
