# Decoupled Trajectories: Fossil CO₂ Intensity, Land‑Use Emissions and Forest Dynamics in South America

This repository contains the reproducible data pipeline for the project “Decoupled Trajectories: Fossil CO₂ Intensity, Land‑Use Emissions and Forest Dynamics in South America (2000–2020).” It focuses on three deliverables:

1. Harmonised source data from CEPALSTAT, World Development Indicators and FAOSTAT.
2. Analysis‑ready tables that summarise country‑level dynamics in fossil CO₂ intensity, forest area and LULUCF emissions.
3. Python scripts that rebuild the panels, export public versions of the data and regenerate the article figures.

The study compares twelve South American countries at three benchmark years (2000, 2010, 2020) and across two decades of change (2000–2010, 2010–2020). With these panels we estimate linear regressions that link:
- decadal changes in fossil CO₂ intensity of GDP to forest area change, shifts in the electricity mix and income growth, and
- decadal changes in per‑capita LULUCF emissions to forest dynamics and the agriculture share of GDP.

The main takeaway is that energy decarbonisation and land‑use mitigation have advanced on different—sometimes diverging—paths. Countries may post low fossil CO₂ intensity while still experiencing forest loss and LULUCF hotspots; therefore mitigation dashboards need to track both fossil and land‑use components to capture real progress.

## Repository structure

- `data_cepal/` – raw pulls from CEPALSTAT plus intermediate joins (ZIP files) and enriched CSV panels that feed the models.
- `data_article/` – public analysis tables cited in the manuscript:
  - `master_forest_energy_analysis_panel.csv` – country–year panel (2000, 2010, 2020) with energy, land‑use and socioeconomic indicators.
  - `south_america_delta_panel_analysis.csv` – decadal‑change panel for 2000–2010 and 2010–2020.
  - `variables_codebook.csv` – plain‑language descriptions and units.
- `scripts/` – complete ETL and modelling toolchain. Highlights:
  - `build_master_panel.py`, `build_extended_forest_energy_panel.py`, `build_variables_codebook.py` – construct the main tables under `data_cepal/` and `data_article/`.
  - `*_extension.py` modules – add governance, trade, socio‑economic and energy‑mix covariates.
  - `build_article_figures.py` – reads `data_article/` and recreates the figures cited in the article, saving PNGs under `article/figures/` (the folder stays local/ignored).
  - `regression_models.py` – helper routines used to estimate the relationships discussed in the text.

## Usage

1. Create a Python environment with the dependencies you normally use for pandas/matplotlib (e.g. `python -m venv .venv && source .venv/bin/activate` followed by `pip install pandas numpy matplotlib`).
2. Run the build scripts in `scripts/` to refresh data:
   ```bash
   python scripts/build_master_panel.py
   python scripts/build_extended_forest_energy_panel.py
   python scripts/build_variables_codebook.py
   ```
   These will recreate the CSVs in `data_cepal/` and export the public subset into `data_article/`.
3. (Optional) Recreate the publication figures:
   ```bash
   python scripts/build_article_figures.py
   ```
   Outputs will land in `article/figures/` locally.

Each script logs its progress through the shared `cepalstat_client.logger`. Refer to the docstrings inside `scripts/` for argument details and processing notes.
