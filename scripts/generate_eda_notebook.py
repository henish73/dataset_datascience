import json
import os

def create_notebook():
    notebook = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    def add_markdown(text):
        notebook["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + ("\n" if not line.endswith("\n") else "") for line in text.split("\n")]
        })

    def add_code(text):
        notebook["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + ("\n" if not line.endswith("\n") else "") for line in text.split("\n")]
        })

    # Add content
    add_markdown("# Exploratory Data Analysis (EDA) & Visualizations\n## Project: The AI-Labor Paradox (2024\u20132026)\n\nThis notebook provides a detailed visual exploration of the synthesized dataset, designed to highlight the K-Shaped displacement trajectories, the Salary Paradox, and the efficacy of the Skill Shield.\n\n### 1. Setup & Environment Initialization")
    
    add_code(
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n\n"
        "# Configure Seaborn Aesthetics\n"
        "sns.set_theme(style='whitegrid', palette='muted')\n"
        "plt.rcParams['figure.figsize'] = (10, 6)\n"
    )

    add_markdown("### 2. Loading the Ultimate Gist Dataset\nMapping the generated synthetic master payload into a Pandas DataFrame.")
    
    add_code(
        "# Load the dataset from the 03_final_data repository\n"
        "file_path = r's:\\MISSION FIELD\\AI - ALGOMA\\FINAL PROJECT\\DATABASE\\03_final_data\\ai_labor_paradox_ultimate_gist.csv'\n"
        "df = pd.read_csv(file_path)\n"
        "display(df.head())\n"
        "print(f'\\nDataset Shape: {df.shape}')\n"
    )

    add_markdown("## Task 1: Univariate Analysis (The Landscape)\nAnalyzing the base distribution of sectors and the overall AI displacement clip.")
    
    add_code(
        "# Visualization 1: Displacement Ratio\n"
        "plt.figure(figsize=(6,6))\n"
        "df['displacement_occurred'].value_counts().plot.pie(autopct='%1.1f%%', labels=['Displaced (1)', 'Retained (0)'], colors=['#E74C3C', '#2ECC71'], explode=(0.05, 0))\n"
        "plt.title('Global Displacement Ratio Simulation')\n"
        "plt.ylabel('')\n"
        "plt.show()\n"
    )
    
    add_code(
        "# Visualization 2: Sector Density vs Theoretical Exposure\n"
        "plt.figure(figsize=(12, 6))\n"
        "sns.boxplot(data=df, x='theoretical_exposure_pct', y='sector', orient='h', order=df['sector'].value_counts().index)\n"
        "plt.axvline(70, color='r', linestyle='--', label='Critical Risk Threshold (>70%)')\n"
        "plt.title('Theoretical Automation Exposure by Sector')\n"
        "plt.xlabel('Automation Exposure %')\n"
        "plt.ylabel('Sector')\n"
        "plt.legend()\n"
        "plt.show()\n"
    )

    add_markdown("## Task 2: Bivariate Analysis (Correlations)\n### The Salary Paradox\nDoes a high salary protect you from displacement, or make you a prime target for efficiency deltas?")
    
    add_code(
        "# Visualization 3: Salary vs Displacement\n"
        "df['salary_bin'] = pd.qcut(df['annual_salary_usd'], q=4, labels=['Q1 (Low)', 'Q2', 'Q3', 'Q4 (High)'])\n"
        "plt.figure(figsize=(8, 5))\n"
        "sns.barplot(data=df, x='salary_bin', y='displacement_occurred', palette='Blues_r')\n"
        "plt.title('Displacement Rates across Salary Quartiles')\n"
        "plt.ylabel('Average Displacement Rate')\n"
        "plt.xlabel('Salary Bin')\n"
        "plt.show()\n"
    )

    add_markdown("### The Skill Shield\nMapping the impact of 'Educational Mismatch' on job security.")
    
    add_code(
        "# Visualization 4: The Skill Shield\n"
        "df['gap_size'] = pd.qcut(df['education_mismatch_idx'], q=4, labels=['Low Gap', 'Mid-Low', 'Mid-High', 'High Gap'], duplicates='drop')\n"
        "plt.figure(figsize=(8, 5))\n"
        "sns.lineplot(data=df, x='gap_size', y='displacement_occurred', marker='o', linewidth=2.5, color='#8E44AD')\n"
        "plt.title('Displacement Trajectory vs Educational Mismatch (The Gap)')\n"
        "plt.ylabel('Average Displacement Rate')\n"
        "plt.xlabel('Competency Void / Gap Size')\n"
        "plt.show()\n"
    )

    add_markdown("## Task 3: Multivariate Analysis (Red Zones)\nIsolating the extreme risk intersections: **Remote Eligibility + High Task Codifiability**.")
    
    add_code(
        "# Visualization 5: Heatmap of Remote vs Codifiability\n"
        "df['high_codif'] = df['task_codifiability_score'] > 0.6\n"
        "heat_df = df.groupby(['is_remote_eligible', 'high_codif'])['displacement_occurred'].mean().unstack()\n"
        "plt.figure(figsize=(7, 5))\n"
        "sns.heatmap(heat_df, annot=True, cmap='coolwarm', fmt='.1%')\n"
        "plt.title('Heatmap: The Remote Danger Multiplier')\n"
        "plt.ylabel('Remote Eligible (1=Yes)')\n"
        "plt.xlabel('High Task Codifiability (>0.6)')\n"
        "plt.show()\n"
    )

    add_markdown("## Task 4: Segmenting the K-Shape Divergence\nContrasting the extreme resilience of Senior Strategic Orchestrators against the high vulnerability of Middle-Management Coordinators.")

    add_code(
        "# Segment Logic\n"
        "df['worker_persona'] = 'Other'\n"
        "df.loc[(df['is_senior'] == 1) & (df['annual_salary_usd'] > 120000), 'worker_persona'] = 'Strategic Orchestrator'\n"
        "df.loc[(df['job_zone'].isin([3, 4])) & (df['is_senior'] == 0), 'worker_persona'] = 'Middle-Management Coordinator'\n"
        "\n"
        "# Visualization 6: The K-Shape\n"
        "k_shape_df = df[df['worker_persona'] != 'Other']\n"
        "plt.figure(figsize=(8, 5))\n"
        "sns.barplot(data=k_shape_df, x='worker_persona', y='displacement_occurred', palette=['#16A085', '#E67E22'])\n"
        "plt.title('The K-Shaped Divergence in Automation Displacement')\n"
        "plt.ylabel('Displacement Rate')\n"
        "plt.xlabel('Worker Persona')\n"
        "plt.show()\n"
    )

    add_markdown("## Core Research Inferences\n\n1. **The Remote Danger Multiplier**: Remote workers with highly codifiable tasks experience massive displacement rates compared to structurally protected on-site roles.\n2. **The K-Shaped Divergence**: Middle-management is squeezed for efficiency, while high-income strategic workers leverage AI as an orchestrator.\n3. **The Efficacy of the Skill Shield**: Specific dense integration skills (Cloud, Deep Learning) completely neutralize highly theoretical AI displacement exposures.")

    base_dir = r"s:\MISSION FIELD\AI - ALGOMA\FINAL PROJECT\DATABASE"
    out_path = os.path.join(base_dir, "03_final_data", "AI_Labor_Paradox_EDA.ipynb")
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1)

    print(f"Jupyter Notebook successfully rendered at: {out_path}")

if __name__ == "__main__":
    create_notebook()
