"""
Script to clean and process Eurostat datasets for the Data Visualisation Assignment.
"""

import pandas as pd
from pathlib import Path

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
    
    # Display information
    display_dataset_info(dataframes)
    
    print("=" * 70)
    print("Data loading completed!")
    print("=" * 70)

if __name__ == "__main__":
    main()
