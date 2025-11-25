# Decoupled Trajectories: Fossil CO₂ Intensity, Land‑Use Emissions and Forest Dynamics in South America

This repository contains data and scripts for a comparative country‑level analysis of how fossil CO₂ intensity of GDP, land‑use, land‑use change and forestry (LULUCF) emissions and forest area have evolved in twelve South American countries between 2000 and 2020.

The project combines harmonised official statistics from CEPALSTAT, the World Bank’s World Development Indicators and FAOSTAT to construct:
- an annual country–year panel for 2000, 2010 and 2020, and
- a decadal‑change panel for 2000–2010 and 2010–2020.

Using these panels, the study estimates simple linear regressions that relate:
- decadal changes in fossil CO₂ intensity of GDP to changes in forest area, the hydropower share of electricity generation and GDP per capita, and
- decadal changes in per‑capita LULUCF emissions to changes in forest area and the agriculture value added share of GDP.

The main empirical findings are:
- fossil CO₂ emissions per unit of GDP declined in most South American countries and are significantly associated with changes in the electricity mix and income growth, but not with decadal percentage changes in forest area once energy and income dynamics are controlled for;
- decadal changes in per‑capita LULUCF emissions are closely associated with forest area dynamics and with the agriculture share of GDP, with forest loss linked to larger increases in per‑capita LULUCF emissions and declining agriculture shares linked to more favourable LULUCF trajectories;
- simple regional clusters (agricultural Southern Cone, Andean and Amazon‑frontier, and other countries) illustrate that low or declining fossil CO₂ intensity of GDP can coexist with substantial forest loss or mixed forest trends.

Taken together, the results show that energy‑sector decarbonisation and land‑use emissions have followed distinct, though interconnected, trajectories in South America. Standard climate performance indicators that rely solely on fossil CO₂ intensity of GDP may overstate mitigation progress in forest‑rich economies where land‑use emissions remain substantial.

## Repository structure

- `article/data/` – analysis‑ready panels used in the paper:
  - `master_forest_energy_analysis_panel.csv` – country–year panel for 2000, 2010, 2020.
  - `south_america_delta_panel_analysis.csv` – decadal‑change panel for 2000–2010 and 2010–2020.
  - `variables_codebook.csv` – variable names, descriptions, sources and units.
- `data_cepal/` – source and intermediate data from the CEPALSTAT‑centred ETL pipeline.
- `article/scripts/` – Python scripts to build the analysis panels and article figures.

Additional documentation of the ETL steps and methods is provided in `article/methods_full_draft.md` and `article/methods.md`.

