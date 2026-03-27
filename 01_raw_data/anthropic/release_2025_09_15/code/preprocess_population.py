"""
Preprocess population data for economic analysis.

This script downloads and processes working-age population data (ages 15-64) from:
1. World Bank API for country-level data
2. Taiwan National Development Council for Taiwan data (not in World Bank)
3. US Census Bureau for US state-level data

Output files:
- working_age_pop_YYYY_country.csv (e.g., working_age_pop_2024_country.csv): Country-level working age population
- working_age_pop_YYYY_us_state.csv (e.g., working_age_pop_2024_us_state.csv): US state-level working age population
"""

import io
import warnings
from pathlib import Path

import httpx
import pandas as pd

# Global configuration
YEAR = 2024
DATA_INPUT_DIR = Path("../data/input")
DATA_INTERMEDIATE_DIR = Path("../data/intermediate")

# Countries where Claude AI service is not available
# These will be excluded from all population data
EXCLUDED_COUNTRIES = [
    "AF",  # Afghanistan
    "BY",  # Belarus
    "CD",  # Democratic Republic of the Congo
    "CF",  # Central African Republic
    "CN",  # China
    "CU",  # Cuba
    "ER",  # Eritrea
    "ET",  # Ethiopia
    "HK",  # Hong Kong
    "IR",  # Iran
    "KP",  # North Korea
    "LY",  # Libya
    "ML",  # Mali
    "MM",  # Myanmar
    "MO",  # Macau
    "NI",  # Nicaragua
    "RU",  # Russia
    "SD",  # Sudan
    "SO",  # Somalia
    "SS",  # South Sudan
    "SY",  # Syria
    "VE",  # Venezuela
    "YE",  # Yemen
]


def check_existing_files():
    """Check if processed population files already exist."""
    processed_country_pop_path = (
        DATA_INTERMEDIATE_DIR / f"working_age_pop_{YEAR}_country.csv"
    )
    processed_state_pop_path = (
        DATA_INTERMEDIATE_DIR / f"working_age_pop_{YEAR}_us_state.csv"
    )

    if processed_country_pop_path.exists() and processed_state_pop_path.exists():
        print("✅ Population files already exist:")
        print(f"  - {processed_country_pop_path}")
        print(f"  - {processed_state_pop_path}")
        print(
            "Skipping population preprocessing. Delete these files if you want to re-run."
        )
        return True
    return False


def load_world_bank_population_data():
    """
    Load country-level working age population data from cache or World Bank API.

    Returns:
        pd.DataFrame: Raw population data from World Bank
    """
    # Check if raw data already exists
    raw_country_pop_path = DATA_INPUT_DIR / f"working_age_pop_{YEAR}_country_raw.csv"
    if raw_country_pop_path.exists():
        print("Loading cached country population data...")
        return pd.read_csv(raw_country_pop_path, keep_default_na=False, na_values=[""])

    # Download if not cached
    url = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.1564.TO"
    params = {"format": "json", "date": str(YEAR), "per_page": "1000"}

    print("Downloading country population data from World Bank API...")
    response = httpx.get(url, params=params)
    response.raise_for_status()

    # World Bank API returns [metadata, data] structure
    data = response.json()[1]
    df_raw = pd.json_normalize(data)

    return df_raw


def filter_to_country_level_data(df_raw):
    """
    Filter World Bank data to exclude regional aggregates and keep only countries.

    The World Bank data starts with regional aggregates (Arab World, Caribbean small states, etc.)
    followed by actual countries starting with Afghanistan (AFG).

    Args:
        df_raw: Raw World Bank data

    Returns:
        pd.DataFrame: Filtered data with only country-level records
    """
    # Find Afghanistan (AFG) - the first real country after aggregates
    afg_index = df_raw[df_raw["countryiso3code"] == "AFG"].index[0]

    # Keep everything from AFG onwards
    df_filtered = df_raw.iloc[afg_index:].copy()
    print(f"Filtered to {len(df_filtered)} countries (excluding regional aggregates)")

    return df_filtered


def process_country_population_data(df_raw):
    """
    Process raw World Bank population data.

    Args:
        df_raw: Raw data from World Bank API

    Returns:
        pd.DataFrame: Processed country population data (excluding countries where service is not available)
    """
    # Filter to country level only
    df_country = filter_to_country_level_data(df_raw)

    # Select and rename columns
    df_processed = df_country[
        ["countryiso3code", "date", "value", "country.id", "country.value"]
    ].copy()

    df_processed.columns = [
        "iso_alpha_3",
        "year",
        "working_age_pop",
        "country_code",
        "country_name",
    ]

    # Convert year to int
    df_processed["year"] = pd.to_numeric(df_processed["year"])
    df_processed = df_processed.dropna(subset=["working_age_pop"])

    # Remove Channel Islands entry with invalid JG code
    channel_islands_mask = df_processed["country_code"] == "JG"
    if channel_islands_mask.any():
        print(f"Removing Channel Islands entry with invalid code 'JG'")
        df_processed = df_processed[~channel_islands_mask].copy()

    # Exclude countries where service is not available
    initial_count = len(df_processed)
    df_processed = df_processed[~df_processed["country_code"].isin(EXCLUDED_COUNTRIES)]
    excluded_count = initial_count - len(df_processed)

    if excluded_count > 0:
        print(f"Excluded {excluded_count} countries where service is not available")

    return df_processed


def add_taiwan_population(df_country):
    """
    Add Taiwan population data from National Development Council.

    The World Bank API excludes Taiwan, so we use data directly from Taiwan's NDC.
    Source: https://pop-proj.ndc.gov.tw/main_en/Custom_Detail_Statistics_Search.aspx

    Args:
        df_country: Country population dataframe

    Returns:
        pd.DataFrame: Country data with Taiwan added
    """
    taiwan_file = DATA_INPUT_DIR / "Population by single age _20250903072924.csv"

    if not taiwan_file.exists():
        error_msg = f"""
Taiwan population data not found at: {taiwan_file}

To obtain this data:
1. Go to: https://pop-proj.ndc.gov.tw/main_en/Custom_Detail_Statistics_Search.aspx?n=175&_Query=258170a1-1394-49fe-8d21-dc80562b72fb&amp;page=1&amp;PageSize=10&amp;ToggleType=
2. The following options should have been selected:
   - Estimate type: Medium variant
   - Gender: Total
   - Year: {YEAR}
   - Age: Single age (ages 15-64)
   - Data attribute: data value
3. Download the CSV file
4. Save it as: "Population by single age _20250903072924.csv"
5. Place it in your data input directory

Note: Taiwan data is not available from World Bank API and must be obtained separately.
"""
        raise FileNotFoundError(error_msg)

    print("Adding Taiwan population data from NDC...")

    # Load the NDC data (skip metadata rows)
    df_taiwan = pd.read_csv(taiwan_file, skiprows=10)

    # Clean the age column and sum population
    df_taiwan["Age"] = df_taiwan["Age"].str.replace("'", "")
    df_taiwan["Age"] = pd.to_numeric(df_taiwan["Age"])

    # The data is pre-filtered to ages 15-64, so sum all values
    taiwan_working_age_pop = df_taiwan["Data value (persons)"].sum()

    # Create Taiwan row
    taiwan_row = pd.DataFrame(
        {
            "iso_alpha_3": ["TWN"],
            "year": [YEAR],
            "working_age_pop": [taiwan_working_age_pop],
            "country_code": ["TW"],
            "country_name": ["Taiwan"],
        }
    )

    # Add Taiwan to the country data
    df_with_taiwan = pd.concat([df_country, taiwan_row], ignore_index=True)
    print(f"Added Taiwan: {taiwan_working_age_pop:,.0f} working age population")

    return df_with_taiwan


def load_us_state_population_data():
    """
    Load US state population data from cache or Census Bureau.

    Returns:
        pd.DataFrame: Raw US state population data
    """
    # Check if raw data already exists
    raw_state_pop_path = DATA_INPUT_DIR / f"sc-est{YEAR}-agesex-civ.csv"
    if raw_state_pop_path.exists():
        print("Loading cached state population data...")
        return pd.read_csv(raw_state_pop_path)

    # Download if not cached
    url = f"https://www2.census.gov/programs-surveys/popest/datasets/2020-{YEAR}/state/asrh/sc-est{YEAR}-agesex-civ.csv"

    print("Downloading US state population data from Census Bureau...")
    response = httpx.get(url)
    response.raise_for_status()

    df_raw = pd.read_csv(io.StringIO(response.text))
    return df_raw


def process_state_population_data(df_raw):
    """
    Process US state population data to get working age population.

    Args:
        df_raw: Raw Census Bureau data

    Returns:
        pd.DataFrame: Processed state population data with state codes
    """
    # Filter for working age (15-64) and sum by state
    # SEX=0 means "Both sexes" to avoid double counting
    df_working_age = df_raw[
        (df_raw["AGE"] >= 15) & (df_raw["AGE"] <= 64) & (df_raw["SEX"] == 0)
    ]

    # Sum by state
    working_age_by_state = (
        df_working_age.groupby("NAME")[f"POPEST{YEAR}_CIV"].sum().reset_index()
    )
    working_age_by_state.columns = ["state", "working_age_pop"]

    # Get state codes
    state_code_dict = get_state_codes()

    # Filter out "United States" row (national total, not a state)
    working_age_by_state = working_age_by_state[
        working_age_by_state["state"] != "United States"
    ]

    # Map state names to abbreviations
    working_age_by_state["state_code"] = working_age_by_state["state"].map(
        state_code_dict
    )

    # Check for missing state codes (should be none after filtering United States)
    missing_codes = working_age_by_state[working_age_by_state["state_code"].isna()]
    if not missing_codes.empty:
        warnings.warn(
            f"Could not find state codes for: {missing_codes['state'].tolist()}",
            UserWarning,
            stacklevel=2,
        )

    return working_age_by_state


def get_state_codes():
    """
    Get US state codes from Census Bureau.

    Returns:
        dict: Mapping of state names to abbreviations
    """
    state_codes_path = DATA_INPUT_DIR / "census_state_codes.txt"

    if state_codes_path.exists():
        print("Loading cached state codes...")
        df_state_codes = pd.read_csv(state_codes_path, sep="|")
    else:
        print("Downloading state codes from Census Bureau...")
        response = httpx.get("https://www2.census.gov/geo/docs/reference/state.txt")
        response.raise_for_status()

        # Save for future use
        with open(state_codes_path, "w") as f:
            f.write(response.text)
        print(f"Cached state codes to {state_codes_path}")

        df_state_codes = pd.read_csv(io.StringIO(response.text), sep="|")

    # Create mapping dictionary
    state_code_dict = dict(
        zip(df_state_codes["STATE_NAME"], df_state_codes["STUSAB"], strict=True)
    )

    return state_code_dict


def save_data(df_country, df_state, df_world_bank_raw, df_state_raw):
    """
    Save raw and processed population data.

    Args:
        df_country: Processed country population data
        df_state: Processed state population data
        df_world_bank_raw: Raw World Bank data
        df_state_raw: Raw Census Bureau data
    """
    # Save raw data (only if doesn't exist)
    raw_country_pop_path = DATA_INPUT_DIR / f"working_age_pop_{YEAR}_country_raw.csv"
    if not raw_country_pop_path.exists():
        df_world_bank_raw.to_csv(raw_country_pop_path, index=False)
        print(f"Saved raw country data to {raw_country_pop_path}")

    raw_state_pop_path = DATA_INPUT_DIR / f"sc-est{YEAR}-agesex-civ.csv"
    if not raw_state_pop_path.exists():
        df_state_raw.to_csv(raw_state_pop_path, index=False)
        print(f"Saved raw state data to {raw_state_pop_path}")

    # Save processed data
    country_output_path = DATA_INTERMEDIATE_DIR / f"working_age_pop_{YEAR}_country.csv"
    df_country.to_csv(country_output_path, index=False)
    print(f"Saved processed country population data to {country_output_path}")

    state_output_path = DATA_INTERMEDIATE_DIR / f"working_age_pop_{YEAR}_us_state.csv"
    df_state.to_csv(state_output_path, index=False)
    print(f"Saved processed US state population data to {state_output_path}")


def main():
    """Main function to run population preprocessing."""
    # Check if files already exist
    if check_existing_files():
        return

    # Process country-level data
    print("\n=== Processing Country-Level Population Data ===")
    df_world_bank_raw = load_world_bank_population_data()
    df_country = process_country_population_data(df_world_bank_raw)
    df_country = add_taiwan_population(df_country)

    # Process US state-level data
    print("\n=== Processing US State-Level Population Data ===")
    df_state_raw = load_us_state_population_data()
    df_state = process_state_population_data(df_state_raw)

    # Save all data (raw and processed)
    print("\n=== Saving Data ===")
    save_data(df_country, df_state, df_world_bank_raw, df_state_raw)

    print("\n✅ Population data preprocessing complete!")

    # Print summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Countries processed: {len(df_country)}")
    print(f"Countries excluded (service not available): {len(EXCLUDED_COUNTRIES)}")
    print(
        f"Total global working age population: {df_country['working_age_pop'].sum():,.0f}"
    )
    print(f"US states processed: {len(df_state)}")
    print(f"Total US working age population: {df_state['working_age_pop'].sum():,.0f}")


if __name__ == "__main__":
    main()
