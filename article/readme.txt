Project context and objective
-----------------------------

This folder contains data, scripts and draft text for a scientific article on
the relationship between deforestation, land-use emissions (LULUCF), and fossil
CO2 intensity of GDP in South America.

Target:
- Peer-reviewed scientific article in US English.
- Formal, precise language; no casual or colloquial wording.
- Avoid vague adjectives such as "robust", "huge", "strong" unless they are
  clearly defined (e.g., statistically significant at a given level).

Scope of the study
------------------

Spatial scope:
- 12 South American countries (ISO3): ARG, BOL, BRA, CHL, COL, ECU, GUY,
  PRY, PER, SUR, URY, VEN.

Temporal scope:
- Three time points: 2000, 2010, 2020.
- Decadal changes defined over 2000→2010 and 2010→2020.

Main research questions:
1. How has fossil CO2 intensity of GDP evolved in South America, and how is it
   related to changes in the electricity mix (hydropower vs. fossil fuels and
   other renewables)?
2. How are land-use, land-use change and forestry (LULUCF) emissions related to
   changes in forest area and agricultural structure?
3. How do these patterns connect to the Sustainable Development Goals (SDGs),
   in particular SDG 7 (energy), SDG 13 (climate), SDG 15 (forests), SDG 2
   (food) and SDG 16 (governance)?

Data and ETL summary
--------------------

Main data sources:
- CEPALSTAT Open Data API (cepalstat_client.py):
  * Forest area (indicator 2036).
  * CO2 emissions per unit of GDP PPP (indicator 3914).
  * Agriculture value added share of GDP (indicator 3745).
  * Protected areas share (indicator 2260, limited coverage).
  * Gini index (indicator 3289) and rural extreme poverty (indicator 3328).

- World Bank (worldbank_client.py):
  * Electricity mix: hydropower, coal, gas, renewables excl. hydro, access
    to electricity.
  * GDP per capita PPP (constant 2017 international dollar), GDP (constant
    2015 USD), oil rents.
  * Governance indicators: Control of Corruption (CC.EST), Rule of Law (RL.EST).
  * Population and population density.

- FAOSTAT (faostat_client.py, using bulk downloads):
  * Production_Crops_Livestock_E_All_Data_(Normalized).zip:
    - Soybeans (Item Code 236, Element 5312: area harvested).
    - Sugar cane (Item Code 156, Element 5312: area harvested).
  * Inputs_LandUse_E_All_Data_(Normalized).zip:
    - Permanent meadows and pastures (Item Code 6655, Element 5110: area).
  * Inputs_FertilizersNutrient_E_All_Data_(Normalized).zip:
    - Nitrogen fertilizers total (Item Code 3102, Element 5157: application
      rate in kg/ha).
  * Emissions_Totals_E_All_Data_(Normalized).zip:
    - LULUCF total (Item Code 1707, Element 723113: CO2eq AR5, kt).

Pipeline structure (high level):
- Extract forest and CO2 intensity panel.
- Extend with economic, energy, land-use, governance and socio indicators
  via modular scripts:
  * build_extended_forest_energy_panel.py
  * energy_mix_extension.py
  * landuse_biodiversity_extension.py
  * governance_extension.py
  * socio_inequality_extension.py
  * emissions_extension.py
  * trade_energy_extension.py
  * build_master_panel.py
  * wb_basic_controls_extension.py
- Final master panel:
  * data_cepal/master_forest_energy_controls_panel.csv
  * analysis version without all-NA columns:
    data_cepal/master_forest_energy_analysis_panel.csv

Decadal changes and analysis panels
-----------------------------------

- Delta construction (delta_analysis_panel.py):
  * For each country, compute differences between 2010 and 2000, and between
    2020 and 2010.
  * Key delta variables:
    - delta_forest_pct (percentage change in forest area).
    - delta_co2_intensity_abs (absolute change in CO2 intensity).
    - delta_hydro_share_pct, delta_gdp_per_capita, delta_agri_share_pct.
    - lulucf_per_capita_t_co2eq and delta_lulucf_per_capita_t_co2eq.
  * Output:
    - data_cepal/south_america_delta_panel_processed.csv
    - analysis version (no all-NA columns):
      data_cepal/south_america_delta_panel_analysis.csv.

Core empirical results (summary)
--------------------------------

Fossil CO2 intensity:
- Fossil CO2 emissions per unit of GDP PPP (kg CO2 per 2017 USD) declined
  between 2000 and 2020 in most South American countries.
- Decadal regression models show:
  * Changes in hydropower share and GDP per capita are significantly
    associated with declining CO2 intensity.
  * Changes in forest area (delta_forest_pct) do not show a statistically
    relevant effect on delta_co2_intensity_abs in our models.
- Interpretation: decarbonisation of the energy system (especially via
  hydropower and structural change) is the main driver of observed CO2
  intensity improvements, not forest change.

LULUCF emissions:
- LULUCF total emissions (lulucf_total_kt_co2eq) are fully populated for all
  countries and years.
- When expressed per capita and examined in decadal changes:
  * delta_lulucf_per_capita_t_co2eq is positively associated with
    delta_forest_pct:
    - more forest loss (negative delta_forest_pct) corresponds to higher
      increases in LULUCF emissions per capita.
  * delta_lulucf_per_capita_t_co2eq is negatively associated with
    delta_agri_share_pct:
    - decreasing agricultural share in GDP is linked with more favourable
      LULUCF trends.
- These associations are stable across ordinary least squares, robust
  (HC1) and cluster-robust standard errors and leave-one-country-out tests.

Overall message:
- Energy-sector decarbonisation and land-use emissions follow different
  trajectories in South America:
  * It is possible to reduce fossil CO2 intensity of GDP through changes in
    the energy mix and structural economic change.
  * At the same time, forest loss remains tightly linked to LULUCF
    emissions per capita.
- Evaluating climate performance solely through CO2 intensity can therefore
  be misleading; land-use emissions must be explicitly considered.

Figures and article-style plots
-------------------------------

Script:
- article/scripts/build_article_figures.py

Figures (article/figures/):
- fig1_trends_forest_co2_lulucf.png:
  * Regional mean trends in forest area, CO2 intensity of GDP, and LULUCF
    emissions (2000, 2010, 2020).
- fig2_delta_forest_vs_co2_intensity.png:
  * Scatterplot of decadal change in forest area (%) vs. change in CO2
    intensity (kg CO2 per USD), with country clusters and OLS fit.
- fig3_delta_forest_vs_lulucf_per_capita.png:
  * Scatterplot of decadal change in forest area (%) vs. change in LULUCF
    emissions per capita (t CO2eq), with country clusters and OLS fit.
- fig4_energy_mix_changes_2000_2020.png:
  * Changes in electricity mix shares (hydro, coal, gas, renewables excl.
    hydro) between 2000 and 2020 by country.

Draft text
----------

- Methods draft:
  * article/methods_full_draft.md
  * Detailed description of data sources, ETL pipeline, delta construction
    and regression models.
- Discussion and conclusions exist in the conversation history and can be
  reconstructed or summarised as needed.

Language and style constraints for the article
----------------------------------------------

Target language:
- US English.

Style:
- Formal, scientific writing; no colloquial expressions.
- Avoid vague or subjective terms such as "robust", "huge", "strong" unless
  precisely defined (for example, with reference to statistical significance
  or effect size).
- When describing results, prefer specific statements:
  * "the coefficient is positive and statistically significant at the 5% level"
    instead of "the effect is strong and robust".
  * "the model explains approximately half of the variance" instead of "the
    model fits very well".

Expectations for future sessions
--------------------------------

- The goal for future work is to:
  1. Transform the existing methods draft and empirical results into a
     full scientific article (IMRaD structure or journal-specific structure)
     in US English.
  2. Use the existing data and scripts as fixed analytical backbone; no
     substantial new data collection is planned at this stage.
  3. Focus on:
     - clear presentation of methods and data,
     - transparent description of regression models and findings,
     - careful interpretation in the context of SDGs and existing literature.

- A future assistant should:
  * Rely on the artefacts in the "article" and "data_cepal" folders,
    especially:
    - article/data/master_forest_energy_analysis_panel.csv
    - article/data/south_america_delta_panel_analysis.csv
    - article/data/variables_codebook.csv
    - article/methods_full_draft.md
  * Avoid introducing informal language and speculative claims.
  * Use the SciSpace-based master reference list
    (article/references_master_list.txt) and the underlying Excel files in
    article/SciSpace as the primary literature pool.

Additional note for future language models
------------------------------------------

- The target output is a scientific article in US English.
- Avoid non-technical adjectives such as "robust", "huge", "strong",
  "powerful" or similar unless they are explicitly tied to quantitative
  evidence (for example: "statistically significant at the 5% level" or
  "coefficient magnitude above X").
- Do not re-derive the data pipeline; treat the CSV files in article/data/
  and data_cepal/ and the scripts in the repository as given and already
  validated.
- You may assume that compute and context are available to focus directly on
  drafting introduction, methods, results, discussion and conclusion text,
  using the information summarised in this readme and in
  article/methods_full_draft.md.

Recommendation for a public GitHub repository
---------------------------------------------

For reproducibility, a public GitHub repository accompanying the article
should at minimum contain:

- Environment / setup:
  * requirements.txt (Python dependencies).

- API client modules:
  * cepalstat_client.py
  * worldbank_client.py
  * faostat_client.py

- ETL / panel construction scripts:
  * extract_forest_co2_decadal_panel.py
  * build_extended_forest_energy_panel.py
  * energy_mix_extension.py
  * landuse_biodiversity_extension.py
  * governance_extension.py
  * socio_inequality_extension.py
  * emissions_extension.py
  * trade_energy_extension.py
  * wb_basic_controls_extension.py
  * build_master_panel.py
  * build_analysis_panels.py
  * build_variables_codebook.py

- Analysis scripts:
  * delta_analysis_panel.py
  * regression_models.py
  * article/scripts/build_article_figures.py

- Data files (CSV) required to reproduce the main tables/figures:
  * article/data/master_forest_energy_analysis_panel.csv
  * article/data/south_america_delta_panel_analysis.csv
  * article/data/variables_codebook.csv

- Documentation:
  * article/readme.txt (this file)
  * article/methods_full_draft.md
  * article/references_master_list.txt

Large raw FAOSTAT bulk files (ZIP) need not be hosted in the repository;
instead, refer to the official FAOSTAT bulk download URLs and document
the exact dataset names and codes, as already done in this readme and in
the methods draft. If file size permits, a derived, country-year subset
of FAOSTAT data used in the analysis may be included as an additional CSV.

With this context, a new chat with fresh compute can proceed directly to
article drafting (introduction, condensed methods, results, discussion,
conclusion) without re-deriving the data pipeline.
