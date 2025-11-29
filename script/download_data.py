"""
Script to download Eurostat datasets for the Data Visualisation Assignment.
Downloads datasets only if they don't already exist in data/input/ folder.
"""

import os
import requests
import gzip
import shutil
from pathlib import Path

# Define the datasets with their URLs and output filenames
DATASETS = [
    {
        "name": "Share of buses and trains in inland passenger transport",
        "url": "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/sdg_09_50?format=SDMX-CSV&compressed=true",
        "filename": "buses_trains_passenger_transport.csv"
    },
    {
        "name": "Domestic net greenhouse gas emissions",
        "url": "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/sdg_13_10?format=SDMX-CSV&compressed=true",
        "filename": "greenhouse_gas_emissions.csv"
    },
    {
        "name": "Air emissions accounts related to road transport",
        "url": "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/env_ac_aibrid_rd?format=SDMX-CSV&compressed=true",
        "filename": "road_transport_air_emissions.csv"
    }
]

def download_dataset(url, output_path):
    """
    Download a compressed dataset from Eurostat and save it as CSV.
    
    Args:
        url: URL of the compressed dataset
        output_path: Path where to save the uncompressed CSV file
    """
    # Download the compressed file
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    # Save the compressed content temporarily
    temp_gz = output_path.with_suffix('.csv.gz')
    with open(temp_gz, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    # Decompress the file
    with gzip.open(temp_gz, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    # Remove the temporary compressed file
    temp_gz.unlink()

def main():
    """Main function to download all datasets."""
    # Create the data/input directory if it doesn't exist
    data_dir = Path("data/input")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("Downloading Eurostat datasets...")
    
    # Download each dataset
    for dataset in DATASETS:
        output_path = data_dir / dataset["filename"]
        
        if output_path.exists():
            print(f"  ⊗ {dataset['filename']} - already exists")
        else:
            try:
                download_dataset(dataset["url"], output_path)
                print(f"  ✓ {dataset['filename']} - downloaded")
            except Exception as e:
                print(f"  ✗ {dataset['filename']} - error: {e}")
    
    print("Download process completed!")
    print("=" * 70)

if __name__ == "__main__":
    main()
