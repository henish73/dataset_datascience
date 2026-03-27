"""
Preprocess GDP data for economic analysis.

This script downloads and processes GDP data from:
1. IMF API for country-level GDP data
2. BEA (Bureau of Economic Analysis) for US state-level GDP data

Output files:
- gdp_YYYY_country.csv (e.g., gdp_2024_country.csv): Country-level total GDP
- gdp_YYYY_us_state.csv (e.g., gdp_2024_us_state.csv): US state-level total GDP
"""

import io
import json
import warnings
from pathlib import Path

import httpx
import pandas as pd

# Global configuration
YEAR = 2024
DATA_INPUT_DIR = Path("../data/input")
DATA_INTERMEDIATE_DIR = Path("../data/intermediate")


# Countries where Claude AI service is not available
# These will be excluded from all GDP data
EXCLUDED_COUNTRIES = [
    "AFG",
    "BLR",
    "COD",
    "CAF",
    "CHN",
    "CUB",
    "ERI",
    "ETH",
    "HKG",
    "IRN",
    "PRK",
    "LBY",
    "MLI",
    "MMR",
    "MAC",
    "NIC",
    "RUS",
    "SDN",
    "SOM",
    "SSD",
    "SYR",
    "VEN",
    "YEM",
]


def check_existing_files():
    """Check if processed GDP files already exist."""
    gdp_country_path = DATA_INTERMEDIATE_DIR / f"gdp_{YEAR}_country.csv"
    gdp_state_path = DATA_INTERMEDIATE_DIR / f"gdp_{YEAR}_us_state.csv"

    if gdp_country_path.exists() and gdp_state_path.exists():
        print("✅ GDP files already exist:")
        print(f"  - {gdp_country_path}")
        print(f"  - {gdp_state_path}")
        print("Skipping GDP preprocessing. Delete these files if you want to re-run.")
        return True
    return False


def load_country_gdp_data():
    """
    Load country-level GDP data from cache or IMF API.

    Returns:
        dict: Raw GDP data from IMF API, or None if fetch fails
    """
    # Check if raw data already exists
    raw_gdp_path = DATA_INPUT_DIR / f"imf_gdp_raw_{YEAR}.json"
    if raw_gdp_path.exists():
        print("Loading cached IMF GDP data...")
        with open(raw_gdp_path) as f:
            return json.load(f)

    # Download if not cached
    imf_total_gdp_url = "https://www.imf.org/external/datamapper/api/v1/NGDPD"  # IMF returns GDP in billions USD

    print("Fetching GDP data from IMF API...")
    try:
        with httpx.Client() as client:
            response = client.get(imf_total_gdp_url, timeout=30)
            response.raise_for_status()
            gdp_data = response.json()
            print("✓ Successfully fetched total GDP data from IMF API")

            # Save raw data for future use
            with open(raw_gdp_path, "w") as f:
                json.dump(gdp_data, f, indent=2)
            print(f"✓ Saved raw GDP data to {raw_gdp_path}")

            return gdp_data
    except Exception as e:
        raise ConnectionError(f"Failed to fetch data from IMF API: {e}") from e


def process_country_gdp_data(gdp_data):
    """
    Process IMF GDP data into standardized format.

    Args:
        gdp_data: Raw IMF API response

    Returns:
        pd.DataFrame: Processed country GDP data (excluding countries where service is not available)
    """
    # Extract GDP data for target year
    # Structure: {"values": {"NGDPD": {"countryiso3code": {"year": value}}}}
    gdp_values = gdp_data.get("values", {}).get("NGDPD", {})

    # Build records for target year data only
    gdp_records = []
    target_year = str(YEAR)
    missing_countries = []

    for countryiso3code, years_data in gdp_values.items():
        if isinstance(years_data, dict):
            if target_year in years_data and years_data[target_year]:
                gdp_value = years_data[target_year]
                # Convert from billions to actual dollars
                gdp_records.append(
                    {
                        "iso_alpha_3": countryiso3code,
                        "gdp_total": float(gdp_value)
                        * 1e9,  # Convert billions to dollars
                        "year": YEAR,
                    }
                )
            else:
                missing_countries.append(countryiso3code)

    if missing_countries:
        warnings.warn(
            f"{len(missing_countries)} countries missing {YEAR} GDP data. "
            f"Examples: {missing_countries[:5]}",
            UserWarning,
            stacklevel=2,
        )

    df_gdp = pd.DataFrame(gdp_records)

    if df_gdp.empty:
        raise ValueError(f"No GDP data available for year {YEAR}")

    # Apply country code mappings for mismatches between IMF and ISO3
    country_code_mappings = {
        "UVK": "XKX",  # Kosovo
        # Add more mappings as needed
    }

    for imf_code, iso3_code in country_code_mappings.items():
        df_gdp.loc[df_gdp["iso_alpha_3"] == imf_code, "iso_alpha_3"] = iso3_code

    # Filter to only keep countries with valid ISO-3 codes
    # This removes regional aggregates like ADVEC, AFQ, etc.
    iso_codes_path = DATA_INTERMEDIATE_DIR / "iso_country_codes.csv"
    df_iso = pd.read_csv(iso_codes_path, keep_default_na=False, na_values=[""])
    valid_iso3_codes = set(df_iso["iso_alpha_3"].unique())

    initial_aggregate_count = len(df_gdp)
    df_gdp = df_gdp[df_gdp["iso_alpha_3"].isin(valid_iso3_codes)]
    filtered_aggregates = initial_aggregate_count - len(df_gdp)

    if filtered_aggregates > 0:
        print(
            f"  Filtered out {filtered_aggregates} non-country codes (regional aggregates)"
        )

    # Filter out excluded countries (now using 3-letter codes directly)
    initial_count = len(df_gdp)
    df_gdp = df_gdp[~df_gdp["iso_alpha_3"].isin(EXCLUDED_COUNTRIES)]
    excluded_count = initial_count - len(df_gdp)

    if excluded_count > 0:
        print(f"  Excluded {excluded_count} countries where service is not available")

    # Save processed GDP data
    processed_gdp_path = DATA_INTERMEDIATE_DIR / f"gdp_{YEAR}_country.csv"
    df_gdp.to_csv(processed_gdp_path, index=False)

    print(f"✓ Saved processed GDP data to {processed_gdp_path}")
    print(f"  Countries with {YEAR} GDP data: {len(df_gdp)}")
    print(f"  Countries excluded (service not available): {len(EXCLUDED_COUNTRIES)}")
    print(f"  Total global GDP: ${df_gdp['gdp_total'].sum() / 1e12:.2f} trillion")

    return df_gdp


def load_state_gdp_data():
    """
    Load US state GDP data from BEA file.

    Returns:
        pd.DataFrame: Raw state GDP data, or None if file not found
    """
    state_gdp_raw_path = DATA_INPUT_DIR / f"bea_us_state_gdp_{YEAR}.csv"

    if not state_gdp_raw_path.exists():
        error_msg = f"""
State GDP data not found at: {state_gdp_raw_path}

To obtain this data:
1. Go to: https://apps.bea.gov/itable/?ReqID=70&step=1
2. Select: SASUMMARY State annual summary statistics (area = "United States", statistic = Gross domestic product (GDP), unit of measure = "Levels")
3. Download the CSV file for year {YEAR}
4. Save it as: bea_us_state_gdp_{YEAR}.csv
5. Place it in your data input directory
"""
        raise FileNotFoundError(error_msg)

    print("Loading US state GDP data...")
    # Parse CSV skipping the first 3 rows (BEA metadata)
    df_state_gdp_raw = pd.read_csv(state_gdp_raw_path, skiprows=3)
    df_state_gdp_raw.columns = ["GeoFips", "State", f"gdp_{YEAR}_millions"]

    return df_state_gdp_raw


def process_state_gdp_data(df_state_gdp_raw):
    """
    Process BEA state GDP data into standardized format.

    Args:
        df_state_gdp_raw: Raw BEA data

    Returns:
        pd.DataFrame: Processed state GDP data
    """

    # Remove the US total row (GeoFips = "00000")
    df_state_gdp = df_state_gdp_raw[df_state_gdp_raw["GeoFips"] != "00000"].copy()

    # Remove all rows starting from empty line before "Legend/Footnotes" marker
    # BEA files have footer information after the data, with an empty line before
    legend_index = (
        df_state_gdp[
            df_state_gdp["GeoFips"].str.contains("Legend", case=False, na=False)
        ].index[0]
        - 1
    )
    df_state_gdp = df_state_gdp.iloc[:legend_index].copy()
    print(f"  Removed footer rows starting from 'Legend/Footnotes'")

    # Convert GDP from millions to actual dollars
    df_state_gdp["gdp_total"] = df_state_gdp[f"gdp_{YEAR}_millions"] * 1e6

    # Clean state names
    df_state_gdp["State"] = df_state_gdp["State"].str.strip()

    # Get state codes
    state_code_dict = get_state_codes()
    df_state_gdp["state_code"] = df_state_gdp["State"].map(state_code_dict)

    # Check for missing state codes
    missing_codes = df_state_gdp[df_state_gdp["state_code"].isna()]
    if not missing_codes.empty:
        raise ValueError(
            f"Could not find state codes for: {missing_codes['State'].tolist()}\n"
            f"All BEA state names should match Census state codes after filtering."
        )

    # Select and rename columns
    df_state_gdp_final = df_state_gdp[
        ["state_code", "State", "gdp_total", f"gdp_{YEAR}_millions"]
    ].copy()
    df_state_gdp_final.columns = [
        "state_code",
        "state_name",
        "gdp_total",
        "gdp_millions",
    ]
    df_state_gdp_final["year"] = YEAR

    # Save processed state GDP data
    processed_state_gdp_path = DATA_INTERMEDIATE_DIR / f"gdp_{YEAR}_us_state.csv"
    df_state_gdp_final.to_csv(processed_state_gdp_path, index=False)

    print(
        f"✓ Processed state GDP data for {len(df_state_gdp_final)} states/territories"
    )
    print(
        f"  Total US GDP: ${df_state_gdp_final['gdp_total'].sum() / 1e12:.2f} trillion"
    )
    print(f"✓ Saved to {processed_state_gdp_path}")

    return df_state_gdp_final


def get_state_codes():
    """
    Get US state codes from Census Bureau.

    Returns:
        dict: Mapping of state names to abbreviations
    """
    state_codes_path = DATA_INPUT_DIR / "census_state_codes.txt"

    if state_codes_path.exists():
        print("  Loading cached state codes...")
        df_state_codes = pd.read_csv(state_codes_path, sep="|")
    else:
        print("  Downloading state codes from Census Bureau...")
        response = httpx.get("https://www2.census.gov/geo/docs/reference/state.txt")
        response.raise_for_status()

        # Save for future use
        with open(state_codes_path, "w") as f:
            f.write(response.text)
        print(f"  Cached state codes to {state_codes_path}")

        df_state_codes = pd.read_csv(io.StringIO(response.text), sep="|")

    # Create mapping dictionary
    state_code_dict = dict(
        zip(df_state_codes["STATE_NAME"], df_state_codes["STUSAB"], strict=True)
    )

    return state_code_dict


def main():
    """Main function to run GDP preprocessing."""
    # Check if files already exist
    if check_existing_files():
        return

    print("=" * 60)
    print(f"PROCESSING {YEAR} GDP DATA")
    print("=" * 60)

    # Process country-level GDP from IMF
    print(f"\n=== Country-Level GDP (IMF) - Year {YEAR} ===")
    gdp_data = load_country_gdp_data()
    df_gdp_country = process_country_gdp_data(gdp_data)

    # Process US state-level GDP from BEA
    print(f"\n=== US State-Level GDP (BEA) - Year {YEAR} ===")
    df_state_gdp_raw = load_state_gdp_data()
    df_gdp_state = process_state_gdp_data(df_state_gdp_raw)

    # Final status
    print(f"\n✅ {YEAR} GDP data preprocessing complete!")
    print("\n=== Summary Statistics ===")
    if df_gdp_country is not None:
        print(f"Countries processed: {len(df_gdp_country)}")
        print(f"Countries excluded (service not available): {len(EXCLUDED_COUNTRIES)}")
        print(
            f"Total global GDP: ${df_gdp_country['gdp_total'].sum() / 1e12:.2f} trillion"
        )
    if df_gdp_state is not None:
        print(f"US states processed: {len(df_gdp_state)}")
        print(f"Total US GDP: ${df_gdp_state['gdp_total'].sum() / 1e12:.2f} trillion")


if __name__ == "__main__":
    main()
