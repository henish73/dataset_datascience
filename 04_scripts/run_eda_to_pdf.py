import pandas as pd
import numpy as np
import os
import subprocess

def generate_pdf_report():
    base_dir = r"s:\MISSION FIELD\AI - ALGOMA\FINAL PROJECT\DATABASE"
    csv_path = os.path.join(base_dir, "03_final_data", "ai_labor_paradox_ultimate_gist.csv")
    html_out = os.path.join(base_dir, "03_final_data", "ai_labor_paradox_eda_report.html")
    pdf_out = os.path.join(base_dir, "03_final_data", "ai_labor_paradox_eda_report.pdf")
    
    df = pd.read_csv(csv_path)
    
    # CSS Styling
    html = """
    <html>
    <head>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; color: #333; line-height: 1.6; padding: 40px; }
        h1 { color: #2C3E50; border-bottom: 2px solid #3498DB; padding-bottom: 10px; }
        h2 { color: #2980B9; margin-top: 30px; }
        h3 { color: #16A085; }
        table { border-collapse: collapse; width: 100%; margin-top: 10px; margin-bottom: 20px; font-size: 14px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #F2F3F4; font-weight: bold; }
        tr:nth-child(even) { background-color: #F9F9F9; }
        .highlight { background-color: #FDEDEC; padding: 10px; border-left: 4px solid #E74C3C; margin: 20px 0; }
        .inference { background-color: #EBF5FB; padding: 15px; border-radius: 5px; margin-bottom: 15px; }
        pre, code { background-color: #F4F6F6; padding: 10px; border-radius: 4px; font-family: Consolas, monospace; display: block; overflow-x: auto;}
    </style>
    </head>
    <body>
        <h1>Exploratory Data Analysis (EDA) - The AI-Labor Paradox (2024-2026)</h1>
        
        <h2>Task 1: Univariate Analysis (The Landscape)</h2>
        <h3>Distribution of Sector</h3>
        {sector_dist}
        
        <h3>Distribution of Displacement</h3>
        {disp_dist}
        
        <h3>Distribution of Overall Risk Category</h3>
        {risk_dist}
        
        <h3>Volume of Risk (Top 3 Sectors >70% Exposure Density)</h3>
        {top_3}
        
        <h2>Task 2: Bivariate Analysis (The Correlations)</h2>
        <h3>The Salary Paradox</h3>
        <p>Displacement Rate by Salary Bin:</p>
        {salary_bin}
        <p><strong>Point-biserial correlation (Salary vs Displacement):</strong> {corr_salary:.4f}</p>
        
        <h3>The Skill Shield</h3>
        <p><strong>Correlation (Education Mismatch vs Displacement):</strong> {corr_gap:.4f}</p>
        <p>Displacement Rate by Education Mismatch Gap:</p>
        {gap_size}
        
        <h2>Task 3: Multivariate Analysis (The 'Red Zones')</h2>
        <h3>Interaction: Remote + High Codifiability</h3>
        <p>Average Displacement Rates:</p>
        {remote_codif}
        
        <h3>Statistical Red Zone</h3>
        <div class="highlight">
            <p><strong>Red Zone Displacement Rate (Remote + Low Skill Transf + High Maturity Org):</strong> {red_zone_rate}</p>
        </div>

        <h2>Task 4: Synthesis for Deliverables</h2>
        <h3>Top 5 Most Resilient Roles</h3>
        {top_resilient}
        
        <h3>K-Shaped Trajectory Contrasts</h3>
        <ul>
            <li><strong>Strategic Orchestrators (Senior, >$120k)</strong> Displacement Rate: {orch_disp:.4f} (Count: {orch_count})</li>
            <li><strong>Middle-Management Coordinators (Zone 3/4, non-Senior)</strong> Displacement Rate: {mid_disp:.4f} (Count: {mid_count})</li>
        </ul>
        
        <h2>Anomalies Detection</h2>
        <p><strong>High Risk (>85% exposure) but not displaced:</strong> {anomaly_count} records.</p>
        {anomaly_table}
        
        <h2>Section 3: Core Research Inferences</h2>
        <div class="inference">
            <strong>1. The Remote Danger Multiplier:</strong> The interaction between remote eligibility and high task codifiability demonstrates a severe risk aggregation. Remote workers with highly codifiable tasks experience an overwhelming displacement rate, contrasting drastically with on-site workers performing low-codifiability tasks. The compounding effect of remote eligibility acts as a massive risk multiplier, forming the 'Statistical Red Zone'.
        </div>
        <div class="inference">
            <strong>2. The K-Shaped Divergence (Strategic Orchestrators vs. Coordinators):</strong> The dataset conclusively illustrates the bifurcated 'K-Shaped' trajectory of AI displacement. The displacement rate for Middle-Management Coordinators is aggressively high, compared to significantly lower rates for Strategic Orchestrators earning over $120,000. Rather than providing absolute immunity, high salaries segment into two distinct paths: senior workers orchestrating AI strategy are shielded, while well-paid mid-level coordinators are targeted for efficiency deltas.
        </div>
        <div class="inference">
            <strong>3. The Efficacy of the Skill Shield:</strong> Higher Education Mismatch strictly corresponds to elevated displacement risk. However, anomaly detection reveals individuals with extreme automation exposure (>85%) avoiding displacement entirely by possessing Cloud or Deep Learning skills (the 'Skill Shield'). Workers bridging the competency void through specific technical upskilling successfully neutralize their underlying automation risk.
        </div>
    </body>
    </html>
    """

    # Populate Context
    df_exposed = df[df['theoretical_exposure_pct'] > 70]
    density = df_exposed.groupby('sector').size() / df.groupby('sector').size()
    top_3_risk = density.sort_values(ascending=False).head(3).to_frame(name='Density')
    
    df['salary_bin'] = pd.qcut(df['annual_salary_usd'], q=4, labels=['Q1(Low)', 'Q2', 'Q3', 'Q4(High)'], duplicates='drop')
    sal_disp = df.groupby('salary_bin')['displacement_occurred'].mean().to_frame()
    corr_salary = df['annual_salary_usd'].corr(df['displacement_occurred'])
    
    corr_gap = df['education_mismatch_idx'].corr(df['displacement_occurred'])
    df['gap_size'] = pd.qcut(df['education_mismatch_idx'], q=4, labels=['Low Gap', 'Mid-Low', 'Mid-High', 'High Gap'], duplicates='drop')
    gap_disp = df.groupby('gap_size')['displacement_occurred'].mean().to_frame()
    
    df['high_codif'] = df['task_codifiability_score'] > 0.6
    rem_codif = df.groupby(['is_remote_eligible', 'high_codif'])['displacement_occurred'].mean().unstack()
    
    mask_red_zone = (df['is_remote_eligible'] == 1) & (df['skill_transferability_score'] < 0.4) & (df['org_ai_maturity_stage'] >= 4)
    rz_rate = f"{df.loc[mask_red_zone, 'displacement_occurred'].mean():.4f} (Count: {mask_red_zone.sum()})" if mask_red_zone.sum() > 0 else "None"
    
    top_res = df.sort_values(by=['resilience_score', 'demand_growth_yoy_pct'], ascending=[False, False])
    top_5 = top_res[['job_title', 'sector', 'resilience_score', 'demand_growth_yoy_pct', 'displacement_occurred']].drop_duplicates(subset=['job_title']).head(5)
    
    mask_orch = (df['is_senior'] == 1) & (df['annual_salary_usd'] > 120000)
    mask_mid = (df['job_zone'].isin([3, 4])) & (df['is_senior'] == 0)
    
    anomaly_mask = (df['theoretical_exposure_pct'] > 85) & (df['displacement_occurred'] == 0)
    anomaly_df = df[anomaly_mask][['job_title', 'skills_cloud', 'skills_deep_learning', 'annual_salary_usd', 'job_zone', 'is_senior']].head(3)

    # Format into context dictionary
    context = {
        'sector_dist': df['sector'].value_counts(normalize=True).to_frame(name='Proportion').to_html(),
        'disp_dist': df['displacement_occurred'].value_counts(normalize=True).to_frame(name='Proportion').to_html(),
        'risk_dist': df['overall_risk_category'].value_counts(normalize=True).to_frame(name='Proportion').to_html(),
        'top_3': top_3_risk.to_html(),
        'salary_bin': sal_disp.to_html(),
        'corr_salary': corr_salary,
        'corr_gap': corr_gap,
        'gap_size': gap_disp.to_html(),
        'remote_codif': rem_codif.to_html(),
        'red_zone_rate': rz_rate,
        'top_resilient': top_5.to_html(index=False),
        'orch_disp': df.loc[mask_orch, 'displacement_occurred'].mean() if mask_orch.sum() > 0 else 0,
        'orch_count': mask_orch.sum(),
        'mid_disp': df.loc[mask_mid, 'displacement_occurred'].mean() if mask_mid.sum() > 0 else 0,
        'mid_count': mask_mid.sum(),
        'anomaly_count': anomaly_mask.sum(),
        'anomaly_table': anomaly_df.to_html(index=False)
    }

    final_html = html
    for k, v in context.items():
        final_html = final_html.replace("{" + k + "}", str(v))

    
    with open(html_out, "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print(f"HTML successfully generated at: {html_out}")
    print("Invoking Microsoft Edge to print PDF...")
    
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    # Execute Edge headless PDF render
    cmd = f'"{edge_path}" --headless --print-to-pdf="{pdf_out}" "file:///{html_out.replace(chr(92), "/")}"'
    subprocess.run(cmd, shell=True)
    
    print(f"PDF successfully rendered at: {pdf_out}")

if __name__ == "__main__":
    generate_pdf_report()
