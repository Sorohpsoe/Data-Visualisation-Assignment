# Data Visualisation — Transport & Climate (Eurostat)

This repository contains a compact ETL and visualisation pipeline used for
an academic assignment analysing relationships between public-transport
usage and transport-related greenhouse-gas emissions in Europe.

The project downloads Eurostat extracts, cleans and integrates three
indicators, and produces an interactive scatter plot summarising country-
level averages.

The key idea is to compare the share of passengers carried by buses and
trains (proxy for public transport usage) with road CO₂ emissions per
capita, while encoding total GHG emissions per capita as colour.

Sources: Eurostat SDG and environmental APIs (see in-script references
and `script/download_data.py`).

Citation: Eurostat (SDG_09_50, SDG_13_10, ENV_AC_AIBRID_RD)

Status: code and sample outputs are included. Input CSVs are not
committed (see `.gitignore`); the downloader can fetch them when needed.

--

**Repository structure**

- `data/input/` — raw CSVs (downloaded or provided)
- `data/output/` — generated outputs (integrated CSV, HTML/SVG/PNG plots)
- `script/download_data.py` — downloader for Eurostat SDMX-CSV endpoints
- `script/clean_data.py` — dataset-specific cleaning + integration (saves `data/output/integrated_eurostat_transport_climate.csv`)
- `script/plot_scatter.py` — builds the interactive scatter and static images
- `script/main.py` — single entrypoint that orchestrates download → clean → plot

--

**Prerequisites**

- Python 3.10+ (virtual environment recommended)
- The project `requirements.txt` pins the libraries used (pandas, numpy,
	plotly, pycountry, kaleido, requests, ...).

Install dependencies in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If you only need the interactive plot and not static image export, `kaleido`
is optional; static PNG/SVG rendering requires it.

--

**Quick usage**

1) Download inputs (only if missing):

```powershell
python .\script\download_data.py
```

2) Run cleaning & integration (produces `data/output/integrated_eurostat_transport_climate.csv`):

```powershell
python .\script\clean_data.py
```

3) Generate the interactive scatter (HTML) and static images (PNG, SVG):

```powershell
python .\script\plot_scatter.py
```

Or use the orchestrator to run the full pipeline with optional flags:

```powershell
python .\script\main.py            # run download, clean, plot
python .\script\main.py --skip-download --skip-clean  # only run plot
```

--

**Outputs produced**

- `data/output/integrated_eurostat_transport_climate.csv` — merged indicators
- `data/output/transport_climate_scatter.html` — interactive Plotly output
- `data/output/transport_climate_scatter.png|.svg` — static renders (if
	`kaleido` available)

**Notes & reproducibility**

- Input CSVs are provided by Eurostat SDMX-CSV endpoints; small differences
	in scraped data or Eurostat API parameters may change the integrated
	results over time.
- The cleaning functions in `script/clean_data.py` document the filters
	applied to keep the main series (e.g. units and series codes).
- If `pycountry` is missing, the plotting script falls back to country
	codes for labels.

--

If you want, I can also:

- add a short `requirements-dev.txt` for testing tools,
- add a small `Makefile` / PowerShell script to make running steps easier,
- or expand the README with figures and interpretation for academic
	submission.

Author: project codebase (student assignment)
