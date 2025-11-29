"""
Script to clean and process Eurostat datasets for the Data Visualisation Assignment.
"""

import pandas as pd
from pathlib import Path
from typing import Dict

# Define the dataset files
DATA_DIR = Path("data/input")
DATASETS = {
    "buses_trains": "buses_trains_passenger_transport.csv",
    "greenhouse_gas": "greenhouse_gas_emissions.csv",
    "road_emissions": "road_transport_air_emissions.csv"
}

def load_datasets():
    """Load all datasets into pandas DataFrames."""
    dataframes = {}
    
    for key, filename in DATASETS.items():
        filepath = DATA_DIR / filename
        print(f"Loading {filename}...")
        df = pd.read_csv(filepath)
        dataframes[key] = df
        print(f"  Shape: {df.shape}")
        print()
    
    return dataframes


def clean_buses_trains(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the buses & trains dataset.

    Keeps relevant columns, renames them and converts types.
    Keeps `OBS_FLAG` untouched.
    """
    # Keep only rows for buses total and expected columns
    if "vehicle" in df.columns:
        df = df[df["vehicle"] == "TRN_BUS_TOT_AVD"].copy()
    desired = ["geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "vehicle"]
    present = [c for c in desired if c in df.columns]
    df = df[present].copy()

    # Rename columns
    rename_map = {
        "geo": "country",
        "TIME_PERIOD": "year",
        "OBS_VALUE": "share_buses_trains",
    }
    df = df.rename(columns=rename_map)

    # Convert year to int (drop rows with invalid years)
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = df.dropna(subset=["year"]).copy()
        df["year"] = df["year"].astype(int)

    # Convert share to float
    if "share_buses_trains" in df.columns:
        df["share_buses_trains"] = pd.to_numeric(df["share_buses_trains"], errors="coerce")

    return df


def clean_greenhouse_gas(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the greenhouse gas dataset.

    Keeps and renames columns; converts `ghg_per_capita` to float.
    Assumes values are tonnes per capita.
    """
    # Keep only rows with unit == 'T_HAB' (tonnes per habitant)
    if "unit" in df.columns:
        df = df[df["unit"] == "T_HAB"].copy()

    # Keep only rows where src_crf indicates the main series (exactly TOTXMEMO)
    if "src_crf" in df.columns:
        df = df[df["src_crf"] == "TOTXMEMO"].copy()
    desired = ["geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "unit"]
    present = [c for c in desired if c in df.columns]
    df = df[present].copy()

    rename_map = {
        "geo": "country",
        "TIME_PERIOD": "year",
        "OBS_VALUE": "ghg_per_capita",
    }
    df = df.rename(columns=rename_map)

    # Convert year
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = df.dropna(subset=["year"]).copy()
        df["year"] = df["year"].astype(int)

    # Convert GHG per capita to float (tonnes per capita)
    if "ghg_per_capita" in df.columns:
        df["ghg_per_capita"] = pd.to_numeric(df["ghg_per_capita"], errors="coerce")

    return df


def clean_road_emissions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the road transport air emissions dataset.

    Filters for road CO2 per resident units (AEMIS_RES + CO2),
    keeps columns and renames `OBS_VALUE` to `road_co2_per_capita_g`.
    """
    # Ensure filter columns exist
    if "indic_env" not in df.columns or "airpol" not in df.columns:
        # Return empty dataframe with expected columns if missing
        return pd.DataFrame(columns=["country", "year", "road_co2_per_capita_g", "OBS_FLAG", "unit", "indic_env", "airpol"]) 

    # Filter rows: resident units, CO2 and keep only KG_HAB unit
    df_filtered = df[(df["indic_env"] == "AEMIS_RES") & (df["airpol"] == "CO2")].copy()
    if "unit" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["unit"] == "KG_HAB"].copy()

    # Keep relevant columns if present
    desired = ["geo", "TIME_PERIOD", "OBS_VALUE", "OBS_FLAG", "unit", "indic_env", "airpol"]
    present = [c for c in desired if c in df_filtered.columns]
    df_filtered = df_filtered[present].copy()

    # Rename
    rename_map = {
        "geo": "country",
        "TIME_PERIOD": "year",
        "OBS_VALUE": "road_co2_per_capita_g",
    }
    df_filtered = df_filtered.rename(columns=rename_map)

    # Convert types
    if "year" in df_filtered.columns:
        df_filtered["year"] = pd.to_numeric(df_filtered["year"], errors="coerce")
        df_filtered = df_filtered.dropna(subset=["year"]).copy()
        df_filtered["year"] = df_filtered["year"].astype(int)

    if "road_co2_per_capita_g" in df_filtered.columns:
        df_filtered["road_co2_per_capita_g"] = pd.to_numeric(df_filtered["road_co2_per_capita_g"], errors="coerce")

    return df_filtered


def integrate_datasets(cleaned: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Integrate the three cleaned datasets by inner join on ['country','year'].

    Removes rows with missing indicator values.
    """
    # Expecting keys: 'buses_trains', 'greenhouse_gas', 'road_emissions'
    bt = cleaned.get("buses_trains", pd.DataFrame())
    ghg = cleaned.get("greenhouse_gas", pd.DataFrame())
    road = cleaned.get("road_emissions", pd.DataFrame())

    # Merge buses_trains and greenhouse_gas
    merged = bt.merge(ghg, on=["country", "year"], how="inner", suffixes=("_bt", "_ghg"))

    # Merge with road emissions
    merged = merged.merge(road, on=["country", "year"], how="inner")

    # Keep only rows where all three indicators are present
    required = ["share_buses_trains", "ghg_per_capita", "road_co2_per_capita_g"]
    present_required = [col for col in required if col in merged.columns]
    if present_required:
        merged = merged.dropna(subset=present_required).copy()

    return merged

def display_dataset_info(dataframes):
    """Display information about each dataset."""
    for name, df in dataframes.items():
        print("=" * 70)
        print(f"Dataset: {name}")
        print("=" * 70)
        print(f"\nDataFrame Info:")
        print(df.info())
        print(f"\nFirst 5 rows:")
        print(df.head())
        print("\n")

def main():
    """Main function to load and display datasets."""
    print("=" * 70)
    print("Eurostat Dataset Cleaning Script")
    print("=" * 70)
    print()
    # Load datasets
    dataframes = load_datasets()

    # Display basic info for each raw dataset
    display_dataset_info(dataframes)

    # Apply cleaning functions to each dataset
    print("Applying cleaning functions...")
    cleaned = {}
    cleaned["buses_trains"] = clean_buses_trains(dataframes.get("buses_trains", pd.DataFrame()))
    cleaned["greenhouse_gas"] = clean_greenhouse_gas(dataframes.get("greenhouse_gas", pd.DataFrame()))
    cleaned["road_emissions"] = clean_road_emissions(dataframes.get("road_emissions", pd.DataFrame()))

    # Integrate datasets
    print("Integrating datasets (inner join on country, year)...")
    integrated = integrate_datasets(cleaned)

    # Report and save
    print("\nFinal integrated DataFrame shape:", integrated.shape)
    print("\nFirst 5 rows:")
    print(integrated.head())

    # Ensure output directory exists and save CSV
    out_dir = Path("data/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / "integrated_eurostat_transport_climate.csv"
    integrated.to_csv(output_path, index=False)

    print(f"\nSaved integrated dataset to: {output_path}")
    print("=" * 70)
    print("Data cleaning and integration completed!")
    print("=" * 70)

if __name__ == "__main__":
    main()
