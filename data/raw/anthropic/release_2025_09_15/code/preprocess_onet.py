"""
Preprocess O*NET and SOC data for economic analysis.

This script downloads and processes occupational data from:
1. O*NET Resource Center for task statements
2. O*NET Resource Center for SOC structure

Output files:
- onet_task_statements.csv: O*NET task statements with SOC major groups
- soc_structure.csv: SOC occupational classification structure
"""

import io
import os
import tempfile
from pathlib import Path

import httpx
import pandas as pd

# Global configuration
DATA_INPUT_DIR = Path("../data/input")
DATA_INTERMEDIATE_DIR = Path("../data/intermediate")


def check_existing_files():
    """Check if processed O*NET/SOC files already exist."""
    onet_task_statements_path = DATA_INTERMEDIATE_DIR / "onet_task_statements.csv"
    soc_structure_path = DATA_INTERMEDIATE_DIR / "soc_structure.csv"

    if onet_task_statements_path.exists() and soc_structure_path.exists():
        print("✅ SOC/O*NET files already exist:")
        print(f"  - {onet_task_statements_path}")
        print(f"  - {soc_structure_path}")
        print("Skipping SOC preprocessing. Delete these files if you want to re-run.")
        return True
    return False


def load_task_data():
    """
    Load O*NET Task Statements from cache or O*NET Resource Center.

    Returns:
        pd.DataFrame: O*NET task statements data
    """
    # Check if raw data already exists
    raw_onet_path = DATA_INPUT_DIR / "onet_task_statements_raw.xlsx"
    if raw_onet_path.exists():
        df_onet = pd.read_excel(raw_onet_path)
        return df_onet

    # Download if not cached
    # O*NET Database version 20.1
    onet_url = "https://www.onetcenter.org/dl_files/database/db_20_1_excel/Task%20Statements.xlsx"

    print("Downloading O*NET task statements...")
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(onet_url, timeout=60)
            response.raise_for_status()
            excel_content = response.content
            # Save raw data for future use
            with open(raw_onet_path, "wb") as f:
                f.write(excel_content)

            # Save to temporary file for pandas to read
            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
                tmp_file.write(excel_content)
                tmp_path = tmp_file.name

            try:
                df_onet = pd.read_excel(tmp_path)
                return df_onet
            finally:
                os.unlink(tmp_path)

    except Exception as e:
        raise ConnectionError(f"Failed to download O*NET data: {e}") from e


def process_task_data(df_tasks):
    """
    Process task statements data.

    Args:
        df_tasks: Raw task data

    Returns:
        pd.DataFrame: Processed O*NET data with SOC major groups
    """
    # Extract SOC major group from O*NET-SOC Code (first 2 digits)
    df_tasks["soc_major_group"] = df_tasks["O*NET-SOC Code"].str[:2]

    # Save processed task data
    processed_tasks_path = DATA_INTERMEDIATE_DIR / "onet_task_statements.csv"
    df_tasks.to_csv(processed_tasks_path, index=False)

    print(
        f"✓ Processed {len(df_tasks):,} task statements from {df_tasks['O*NET-SOC Code'].nunique()} occupations"
    )

    return df_tasks


def load_soc_data():
    """
    Load SOC Structure from cache or O*NET Resource Center.

    Returns:
        pd.DataFrame: SOC structure data
    """
    # Check if raw data already exists
    raw_soc_path = DATA_INPUT_DIR / "soc_structure_raw.csv"
    if raw_soc_path.exists():
        return pd.read_csv(raw_soc_path)

    # Download if not cached
    soc_url = "https://www.onetcenter.org/taxonomy/2019/structure/?fmt=csv"

    print("Downloading SOC structure...")
    try:
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(soc_url, timeout=30)
            response.raise_for_status()
            soc_content = response.text
            # Save raw data for future use
            with open(raw_soc_path, "w") as f:
                f.write(soc_content)

            # Parse the CSV
            df_soc = pd.read_csv(io.StringIO(soc_content))
            return df_soc

    except Exception as e:
        raise ConnectionError(f"Failed to download SOC structure: {e}") from e


def process_soc_data(df_soc):
    """
    Process SOC structure data.

    Args:
        df_soc: Raw SOC structure data

    Returns:
        pd.DataFrame: Processed SOC structure
    """
    # Extract the 2-digit code from Major Group (e.g., "11-0000" -> "11")
    df_soc["soc_major_group"] = df_soc["Major Group"].str[:2]

    # Save processed SOC structure
    processed_soc_path = DATA_INTERMEDIATE_DIR / "soc_structure.csv"
    df_soc.to_csv(processed_soc_path, index=False)

    print(f"✓ Processed {len(df_soc):,} SOC entries")

    return df_soc


def main():
    """Main function to run O*NET/SOC preprocessing."""
    # Check if files already exist
    if check_existing_files():
        return

    # Process Task Statements
    df_tasks_raw = load_task_data()
    process_task_data(df_tasks_raw)

    # Process SOC Structure
    df_soc_raw = load_soc_data()
    process_soc_data(df_soc_raw)

    print("\n✅ O*NET/SOC data preprocessing complete!")


if __name__ == "__main__":
    main()
