"""
Fetch ISO country code mappings from GeoNames.

This script fetches comprehensive country data from GeoNames countryInfo.txt
and saves it as a CSV file for use in data preprocessing pipelines.
"""

import io
from pathlib import Path

import httpx
import pandas as pd


def fetch_country_mappings(save_raw=True):
    """
    Fetch country code mappings from GeoNames.

    Args:
        save_raw: Whether to save raw data file to data/input

    Returns:
        pd.DataFrame: DataFrame with country information from GeoNames
    """
    # Fetch countryInfo.txt from GeoNames
    geonames_url = "https://download.geonames.org/export/dump/countryInfo.txt"

    with httpx.Client() as client:
        response = client.get(geonames_url)
        response.raise_for_status()
        content = response.text

    # Save raw file to data/input for reference
    if save_raw:
        input_dir = Path("../data/input")
        input_dir.mkdir(parents=True, exist_ok=True)

        raw_path = input_dir / "geonames_countryInfo.txt"
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(content)

    # Extract column names from the last comment line
    lines = content.split("\n")
    header_line = [line for line in lines if line.startswith("#")][-1]
    column_names = header_line[1:].split("\t")  # Remove # and split by tab

    # Parse the tab-separated file
    # keep_default_na=False to prevent "NA" (Namibia) from becoming NaN
    df = pd.read_csv(
        io.StringIO(content),
        sep="\t",
        comment="#",
        header=None,  # No header row in the data
        keep_default_na=False,  # Don't interpret "NA" as NaN (needed for Namibia)
        na_values=[""],  # Only treat empty strings as NaN
        names=column_names,  # Use the column names from the comment
    )

    # Rename columns to our standard format
    df = df.rename(
        columns={"ISO": "iso_alpha_2", "ISO3": "iso_alpha_3", "Country": "country_name"}
    )

    return df


def create_country_dataframe(geonames_df):
    """
    Create a cleaned DataFrame with country codes and names.

    Args:
        geonames_df: DataFrame from GeoNames with all country information

    Returns:
        pd.DataFrame: DataFrame with columns [iso_alpha_2, iso_alpha_3, country_name]
    """
    # Select only the columns we need
    df = geonames_df[["iso_alpha_2", "iso_alpha_3", "country_name"]].copy()

    # Sort by country name for consistency
    df = df.sort_values("country_name").reset_index(drop=True)

    return df


def save_country_codes(output_path="../data/intermediate/iso_country_codes.csv"):
    """
    Fetch country codes from GeoNames and save to CSV.

    Args:
        output_path: Path to save the CSV file
    """
    # Fetch full GeoNames data
    geonames_df = fetch_country_mappings()

    # Create cleaned DataFrame with just the columns we need
    df = create_country_dataframe(geonames_df)

    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Save to CSV
    df.to_csv(output_file, index=False)

    return df


if __name__ == "__main__":
    # Fetch and save country codes
    df = save_country_codes()
