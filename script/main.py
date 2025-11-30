"""main.py

Command-line entrypoint to orchestrate the full ETL and plotting pipeline.

Usage examples::

    .\venv\Scripts\python.exe .\script\main.py
    .\venv\Scripts\python.exe .\script\main.py --skip-download

The script will download missing inputs, run cleaning/integration and then
produce the plot. Flags allow skipping or forcing individual steps.
"""

from pathlib import Path
import subprocess
import sys
import argparse


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
DATA_IN = ROOT / "data" / "input"
IN_FILES = [
    "buses_trains_passenger_transport.csv",
    "greenhouse_gas_emissions.csv",
    "road_transport_air_emissions.csv",
]
INTEGRATED = ROOT / "data" / "output" / "integrated_eurostat_transport_climate.csv"


def run_script(script: str, extra_args=None):
    cmd = [sys.executable, str(SCRIPT_DIR / script)]
    if extra_args:
        cmd += extra_args
    print("\n==> Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Run full ETL + plot pipeline")
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-clean", action="store_true")
    parser.add_argument("--skip-plot", action="store_true")
    parser.add_argument("--force-download", action="store_true")
    parser.add_argument("--force-clean", action="store_true")
    parser.add_argument("--force-plot", action="store_true")
    args = parser.parse_args()

    try:
        # Download if files are missing (or forced)
        missing = [f for f in IN_FILES if not (DATA_IN / f).exists()]
        if args.force_download or (missing and not args.skip_download):
            print("Missing input files:", missing) if missing else print("Forcing download of datasets")
            run_script("download_data.py")
        else:
            print("Input datasets present — skipping download.")

        # Run cleaning/integration if forced, missing integrated file, or not skipped
        if args.force_clean or (not INTEGRATED.exists() and not args.skip_clean):
            run_script("clean_data.py")
        else:
            print("Integrated CSV present — skipping clean/integrate.")

        # Plot
        if not args.skip_plot or args.force_plot:
            run_script("plot_scatter.py")
        else:
            print("Skipping plot step as requested.")

    except subprocess.CalledProcessError as e:
        print(f"ERROR: step failed with return code {e.returncode}")
        sys.exit(e.returncode)

    print("\nAll steps completed successfully.")


if __name__ == "__main__":
    main()
