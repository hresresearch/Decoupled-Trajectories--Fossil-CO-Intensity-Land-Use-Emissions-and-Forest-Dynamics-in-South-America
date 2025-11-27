# Methods – Full Technical Draft

_This document is a comprehensive, technical description of the data and methods used in the South America forest–energy–emissions analysis. It is intentionally more detailed than a typical journal “Methods” section and serves as a reference for later IMRaD-style writing._

## 1. Study design and scope

We construct a country–year panel for South America and analyse the co-evolution of:
- forest area and land-use change,
- fossil CO₂ emissions per unit of GDP (CO₂ intensity),
- land-use, land-use change and forestry (LULUCF) emissions,
- energy mix,
- agricultural structure,
- governance and social indicators.

**Spatial scope:** 12 South American countries, identified by ISO3 codes:
- Argentina (ARG), Bolivia (BOL), Brazil (BRA), Chile (CHL), Colombia (COL),
  Ecuador (ECU), Guyana (GUY), Paraguay (PRY), Peru (PER), Suriname (SUR),
  Uruguay (URY), Venezuela (VEN).

**Temporal scope:** three time points: 2000, 2010, 2020.  
Decadal changes are defined over two intervals: 2000→2010 and 2010→2020.

All code and data transformations are implemented in plain Python scripts (no notebooks). The core analysis panels are saved as:
- `article/data/master_forest_energy_analysis_panel.csv`
- `article/data/south_america_delta_panel_analysis.csv`
- with `article/data/variables_codebook.csv` documenting variables, sources and units.

## 2. Data sources and indicators

### 2.1 CEPALSTAT (CEPAL)

Data are obtained via the CEPALSTAT Open Data API using `cepalstat_client.py`.
We rely on the following indicators (indicator_id in parentheses):

- **Forest area (thousands of hectares)** – ID `2036`
  - Dimensions: Country, Years, Type of forest.
  - We use aggregate “Total forest” area per country–year.

- **CO₂ emissions per unit of GDP PPP (kg CO₂ per constant 2017 USD)** – ID `3914`
  - Country- and year-specific measure of fossil CO₂ intensity of GDP.

- **Agriculture value added share of GDP (%)** – ID `3745`
  - Dimensions: Country, Years, Reporting Type.
  - We filter to Reporting Type = “Global”.

- **Terrestrial and marine protected areas (% of land)** – ID `2260`
  - Used where available (mostly 2000). Coverage is incomplete; we treat it as an auxiliary variable, not a core regressor.

- **Gini index** – ID `3289`
- **Rural extreme poverty (%)** – ID `3328`

All CEPALSTAT calls use:
- base URL `https://api-cepalstat.cepal.org/cepalstat/api/v1`,
- parameters `lang=en`, `format=json`, `in=1`, `path=0` for cube endpoints,
- JSON parsing via the `_get` helper in `cepalstat_client.py`.

### 2.2 World Bank (WDI)

Data are retrieved from the WDI API using `worldbank_client.py` with base URL:
`https://api.worldbank.org/v2/country/{iso3}/indicator/{indicator_code}?format=json&per_page=2000`.
We use:

- **Hydropower share of electricity (% of total)** – `EG.ELC.HYRO.ZS`
- **Electricity from coal (% of total)** – `EG.ELC.COAL.ZS`
- **Electricity from natural gas (% of total)** – `EG.ELC.NGAS.ZS`
- **Electricity from renewables excl. hydro (% of total)** – `EG.ELC.RNWX.ZS`
- **Access to electricity (% of population)** – `EG.ELC.ACCS.ZS`

- **GDP per capita, PPP (constant 2017 international $)** – `NY.GDP.PCAP.PP.KD`
- **GDP (constant 2015 US$)** – `NY.GDP.MKTP.KD`
- **Oil rents (% of GDP)** – `NY.GDP.PETR.RT.ZS`

- **Total population** – `SP.POP.TOTL`
- **Population density (people per sq. km of land area)** – `EN.POP.DNST`

- **Worldwide Governance Indicators (WGI)**:
  - Control of Corruption – `CC.EST`
  - Rule of Law – `RL.EST`

For many historical WDI codes, coverage is stable. Some legacy indicators (e.g. EN.ATM.METH.KT.CE for methane, EN.ATM.CO2E.KT / EN.ATM.CO2E.PC for CO₂ totals) are no longer available via the API; we do not use them in the analysis.

The client handles:
- request retries with a configurable timeout,
- response structure checking (metadata + data list),
- raising `RuntimeError` on malformed responses or unknown indicators.

### 2.3 FAOSTAT

Wir verwenden FAOSTAT sowohl über die API als auch über die Bulk-Downloads.  
Für die kritischen Landnutzungs- und Emissionsvariablen stützen wir uns auf **Bulk-Normalized** Datensätze, die wir lokal in `data_cepal/` halten:

- `Production_Crops_Livestock_E_All_Data_(Normalized).zip`
- `Inputs_LandUse_E_All_Data_(Normalized).zip`
- `Inputs_FertilizersNutrient_E_All_Data_(Normalized).zip`
- `Inputs_FertilizersArchive_E_All_Data_(Normalized).zip`
- `Emissions_Land_Use_Forests_E_All_Data_(Normalized).zip`
- `Emissions_Totals_E_All_Data_(Normalized).zip`

Die Zip-Dateien enthalten je eine Normalized-CSV (`*_E_All_Data_(Normalized).csv`) plus Metadaten (AreaCodes, Elements).

**Landnutzungsindikatoren (Crops & LandUse)** – aus `Production_Crops_Livestock` und `Inputs_LandUse`:

- Soja:
  - Item Code `236` = “Soya beans”
  - Element Code `5312` = “Area harvested (ha)”
  → Aggregation zu `soy_area_kha` (ha → 1000 ha).

- Zuckerrohr:
  - Item Code `156` = “Sugar cane”
  - Element Code `5312` = “Area harvested (ha)”
  → Aggregation zu `sugarcane_area_kha`.

- Dauerweiden/Weideland:
  - Domain: Inputs LandUse.
  - Item Code `6655` = “Permanent meadows and pastures”
  - Element Code `5110` = “Area (ha)”
  → Aggregation zu `pasture_area_kha`.

**Dünger** – aus `Inputs_FertilizersNutrient`:
- Item Code `3102` = “Nitrogen fertilizers, total”
- Element Code `5157` = “Nutrient application rate (kg/ha)”
→ Aggregation zu `fertilizer_use_kg_per_ha`.

**LULUCF-Emissionen** – aus Emissions-Bulkfiles:

- Forestland (for information, not in final models):
  - `Emissions_Land_Use_Forests` (Forests domain),
  - Item Code `6751` = “Forestland”,
  - Element Code `723113` = “Emissions (CO2eq) from AR5 (kt)”.

- Total LULUCF:
  - `Emissions_Totals` (Totals domain),
  - Item Code `1707` = “LULUCF”,
  - Element Code `723113` = “Emissions (CO2eq) from AR5 (kt)”.
  → Wir verwenden **diese** Größe (`lulucf_total_kt_co2eq`) als zentrale LULUCF-Variable.

Da `fenixservices.fao.org` zeitweise 521-Fehler liefert, ist der Bulk-Weg die robuste Basis. Die API-Helfer sind als Fallback implementiert, werden aber für die zentralen Variablen nicht benötigt.

## 3. ETL-Pipeline und Panel-Konstruktion

Die ETL-Pipeline ist modular aufgebaut, jedes Skript erzeugt eine neue CSV auf Basis des vorherigen Standes. Dies sichert Reproduzierbarkeit und klare Abhängigkeiten.

### 3.1 Forest–CO₂-Basispanel

Skript: `extract_forest_co2_decadal_panel.py`

Schritte:
1. CEPALSTAT:
   - `get_indicator_all_records("2036")`: Waldfläche.
   - `get_indicator_all_records("3914")`: CO₂/BIP-Intensität.
2. Dimensionen aus den API-Cubes:
   - Year-Dimension via Name-Suche („Years__ESTANDAR“),
   - Country-Dimension via Code „Country__ESTANDAR“,
   - Typ-of-forest-Dimension, Filter auf “Total forest”.
3. Aggregation:
   - Waldfläche `forest_area_kha` (Value-Spalte in Tausend Hektar).
   - CO₂/BIP-Intensität `co2_per_gdp_kg_per_usd`.
4. Dekaden-Change für Wald/CO₂:
   - pro ISO3 sortiert nach Jahr,
   - `forest_area_kha_decadal_change_pct` via `pct_change`,
   - `co2_per_gdp_kg_per_usd_decadal_change_pct` analog.

Output: `forest_co2_decadal_panel.csv`.

### 3.2 Extended Panel: Ökonomie, Energie, Landnutzung, Governance, Sozio

Weitere Skripte bauen sequenziell darauf auf:

- `build_extended_forest_energy_panel.py`:
  - lädt Basispanel,
  - fügt Agrar-BIP-Anteil (`3745`), Landnutzungs-Metadaten und erste World-Bank-Indikatoren hinzu,
  - speichert `forest_co2_extended_panel.csv`.

- `energy_mix_extension.py`:
  - fügt Anteile von Strom aus Hydro, Kohle, Gas, Renewables excl. Hydro und Elektrifizierung (`EG.ELC.*`) hinzu,
  - ersetzt ggf. vorhandene Hydro-Spalte (um `_x`/`_y` zu vermeiden),
  - Output: `forest_co2_energy_mix_panel.csv`.

- `landuse_biodiversity_extension.py`:
  - liest FAOSTAT-Bulk-Zips für Soja, Zuckerrohr, Weide, Dünger (siehe Codes oben),
  - mappt Länder via Flächennamen → ISO3 (AREA_NAME_TO_ISO),
  - summiert Flächen/Anwendungsrate pro ISO3–Jahr,
  - fügt optional Schutzgebietsanteile (CEPAL 2260) hinzu,
  - Output: `forest_co2_landuse_panel.csv`.

- `governance_extension.py`:
  - lädt WGI-Indikatoren `CC.EST` (Korruption) und `RL.EST` (Rechtsstaatlichkeit),
  - Output: `forest_co2_governance_panel.csv`.

- `socio_inequality_extension.py`:
  - lädt Gini (3289) und ländliche extreme Armut (3328),
  - mappt Dimensions-IDs auf Jahr/ISO3,
  - Output: `forest_co2_socio_panel.csv`.

- `emissions_extension.py`:
  - fügt LULUCF total (`1707`, `723113`) und optional Forestland (`6751`) hinzu,
  - Methan-Indikator des WDI wird abgefangen und bleibt leer (nahezu komplett fehlend),
  - Output: `forest_co2_emissions_panel.csv`.

- `trade_energy_extension.py`:
  - Terms of Trade (CEPAL ID 883),
  - Öl-Rents, Strom-Share Renewables total, BIP (WDI),
  - berechnet `non_oil_gdp_constant_2015_usd = gdp * (1 - oil_rents_share/100)`,
  - Output: `forest_co2_trade_energy_panel.csv`.

- `build_master_panel.py`:
  - dedupliziert alle ISO3–Jahr-Kombinationen,
  - Output: `master_forest_energy_panel.csv`.

- `wb_basic_controls_extension.py`:
  - fügt `population_total` (SP.POP.TOTL) und `population_density` (EN.POP.DNST) hinzu,
  - versucht CO₂-Gesamtindikatoren, fängt aber die (fehlende) Verfügbarkeit sauber ab,
  - Output: `master_forest_energy_controls_panel.csv` (36 Länder–Jahr-Beobachtungen).

### 3.3 Analyse-Panels ohne leere Spalten

Skript: `build_analysis_panels.py`

Ziel: Panels für statistische Analysen und Regressionsmodelle bereinigen, indem Spalten, die ausschließlich NaN enthalten, entfernt werden.

- Aus `master_forest_energy_controls_panel.csv` wird:
  - `master_forest_energy_analysis_panel.csv`
  - entfernte Spalten (NA-only):
    - `methane_emissions_kt_co2eq`
    - `lulucf_forest_kt_co2eq`
    - `co2_total_kt`
    - `co2_per_capita_tons`

- Aus `south_america_delta_panel_processed.csv` wird:
  - `south_america_delta_panel_analysis.csv`
  - entfernte Spalten (NA-only):
    - `protected_areas_share_pct`
    - `methane_emissions_kt_co2eq`
    - `lulucf_forest_kt_co2eq`
    - `co2_total_kt`
    - `co2_per_capita_tons`
    - `methane_total_kt_co2eq`

Diese Analysepanels liegen im Artikel-Ordner in `article/data/`.

## 4. Konstruktion der Delta-Variablen

Die Dekaden-Deltas werden in `delta_analysis_panel.py` definiert, basierend auf `master_forest_energy_controls_panel.csv` (bzw. dem Analysependant).

### 4.1 Definition der Deltas

Für jede Variable \( X \) und jedes Land \( i \) werden Deltas über Dekaden definiert als:

\[
\Delta X_{i,t} = X_{i,t} - X_{i,t-10}
\]

mit \( t \in \{2010, 2020\} \).  
Die Daten sind pro Land nach Jahr sortiert; Deltas werden über `groupby("iso3").diff()` berechnet.

Konkrete Variablen:

- `delta_forest_kha` – absolute Änderung der Waldfläche (kha).
- `delta_forest_pct` – prozentuale Änderung der Waldfläche:

\[
\Delta \% \text{Forest}_{i,t} = 100 \cdot \frac{ \text{Forest}_{i,t} - \text{Forest}_{i,t-10} }{ \text{Forest}_{i,t-10} }.
\]

- `delta_co2_intensity_abs` – absolute Änderung der CO₂-Intensität (kg CO₂ / USD).
- `delta_hydro_share_pct` – Änderung des Wasserkraft-Anteils (Prozentpunkte).
- `delta_gdp_per_capita` – Änderung des GDP p.c. (PPP, konstante 2017-US$).
- `delta_agri_share_pct` – Änderung des Agrar-BIP-Anteils (Prozentpunkte).

### 4.2 LULUCF pro Kopf und dessen Delta

Aus `lulucf_total_kt_co2eq` und `population_total` wird zunächst eine Pro-Kopf-Größe berechnet:

\[
\text{LULUCFpc}_{i,t} = \frac{\text{LULUCFtotal}_{i,t} \cdot 1000}{\text{Population}_{i,t}} \quad \text{(t CO₂eq pro Kopf)}.
\]

Dann:

\[
\Delta \text{LULUCFpc}_{i,t} = \text{LULUCFpc}_{i,t} - \text{LULUCFpc}_{i,t-10}.
\]

Die Variablen `lulucf_per_capita_t_co2eq` und `delta_lulucf_per_capita_t_co2eq` werden im Delta-Panel gespeichert.

### 4.3 Delta-Panel

Das Delta-Panel `south_america_delta_panel_analysis.csv` enthält:
- ISO3, Jahr (2010, 2020),
- Levelwerte der Ausgangsvariablen aus dem Masterpanel,
- alle oben beschriebenen Delta-Variablen,
- period_start = Jahr-10, period_end = Jahr.

Dieses Panel umfasst 24 Beobachtungen (12 Länder × 2 Dekaden) und ist die Basis aller Delta-Regressionen.

## 5. Statistische Analyse

Wir unterscheiden zwischen:
- deskriptiven Auswertungen des Level-Panels (N=36),
- Delta-basierten Regressionsmodellen (N=22 bzw. 11, abhängig von Datenverfügbarkeit).

### 5.1 Deskriptive Statistik und Korrelationen

Skript: `analysis_master_panel.py`

Schritte:
- Für jedes Jahr (2000, 2010, 2020) werden Standarddeskriptiva (Mittelwert, Std, Min, Max) für zentrale Variablen berechnet:
  - `forest_area_kha`, `co2_per_gdp_kg_per_usd`,
  - `soy_area_kha`, `sugarcane_area_kha`, `pasture_area_kha`,
  - `fertilizer_use_kg_per_ha`,
  - `gdp_per_capita_ppp_const2017`, `population_total`, `population_density`.
- Korrelationsmatrizen (Pearson) für ausgewählte Variablen:
  - u.a. Waldfläche, CO₂-Intensität, LULUCF total, Soja/Weide/Dünger, Hydro-Anteil, GDP p.c., Dichte.

Diese Auswertungen dienen vor allem dem „Kontext“, nicht der Kausalidentifikation.

### 5.2 Delta-Modelle: CO₂-Intensität

Skripte: `delta_analysis_panel.py`, `regression_models.py`

Modell A (gesamtes Delta-Panel, N=22):

\[
\Delta \text{CO2Intensity}_{i} =
 \beta_0 + \beta_1 \Delta \text{Forest\%}_i + \beta_2 \Delta \text{HydroShare\%}_i +
 \beta_3 \Delta \text{GDPpc}_i + \varepsilon_i.
\]

Implementierung:
- `regression_models.py`, Funktion `run_delta_co2_model`.
- OLS mit `statsmodels.OLS`:
  - klassische SE und robuste HC1-SE.
- Variablen:
  - y = `delta_co2_intensity_abs`,
  - X = `delta_forest_pct`, `delta_hydro_share_pct`, `delta_gdp_per_capita`.

Erweiterung:
- `run_delta_co2_model_by_period` schätzt dasselbe Modell getrennt für 2000→2010 und 2010→2020 (N=11 pro Dekade; aufgrund kleiner Stichprobe primär qualitativ zu interpretieren).

### 5.3 Delta-Modelle: LULUCF pro Kopf

Modell B (fit auf N=11, Länder mit vollständigen LULUCF- und Populationsdaten):

\[
\Delta \text{LULUCFpc}_{i} =
 \gamma_0 + \gamma_1 \Delta \text{Forest\%}_i + \gamma_2 \Delta \text{AgriShare\%}_i + \varepsilon_i.
\]

Implementierung:
- `regression_models.py`, Funktion `run_delta_lulucf_model`.
- OLS (statsmodels) mit:
  - klassische SE,
  - robuste HC1-SE,
  - zusätzlich cluster-robuste SE (Cluster = `iso3`) via `cov_type="cluster"`.

Erweiterungen/Robustness:
- `run_delta_lulucf_model_by_period`:
  - schätzt Modell B getrennt nach Dekaden (für 2000→2010 zu wenige Beobachtungen, dies wird geloggt).
- `run_delta_lulucf_leave_one_out`:
  - führt Leave-one-country-out-Analysen durch:
    - für jedes Land wird das Modell ohne dieses Land geschätzt,
    - es werden Koeffizient und p-Wert von `delta_forest_pct` protokolliert.
  - Ziel: prüfen, ob der Wald-Effekt robust gegenüber einzelnen Ländern ist.
- `run_delta_lulucf_clustered`:
  - OLS mit cluster-robusten Standardfehlern nach Land (ISO3),
  - testet Robustheit der Signifikanz gegen gruppierte Fehlerstrukturen.

### 5.4 Visualisierung

Skript: `delta_analysis_panel.py`

Erzeugte Plots:
- `delta_forest_vs_co2_intensity.png`:
  - X: `delta_forest_pct`,
  - Y: `delta_co2_intensity_abs`,
  - Farbe: Cluster (A_Agro: ARG, BRA, PRY, URY; B_Andean: BOL, COL, ECU, PER, VEN; C_Other: GUY, SUR, CHL),
  - Beschriftung: ISO3–Jahr,
  - OLS-Regressionslinie.

- `delta_forest_vs_lulucf_per_capita.png`:
  - X: `delta_forest_pct`,
  - Y: `delta_lulucf_per_capita_t_co2eq`,
  - gleiche Cluster- und Label-Logik,
  - OLS-Regressionslinie.

Die Plots dienen der visuellen Unterstützung der Regressionsergebnisse.

## 6. Umgang mit fehlenden Daten und leeren Variablen

- Einige externe Indikatoren (z. B. WDI Methan, WDI CO₂ total) sind über die aktuelle API nicht mehr verfügbar; entsprechende Spalten (`methane_emissions_kt_co2eq`, `co2_total_kt` etc.) verbleiben im Rohpanel, sind aber vollständig NaN.
- Die Funktion `build_analysis_panels.py` entfernt aus den Analysepanels alle Spalten, deren Nicht-NaN-Anzahl 0 ist (also _wirklich_ nie beobachtet).
- Das bedeutet:
  - **In den finalen Analysepanels werden ausschließlich Variablen verwendet, die mindestens einen beobachteten Wert tragen.**
  - Leere Methan/LULUCF-Forest/CO₂-total-Spalten fließen **nicht** in Modelle ein.

Für Full-Reproducibility sind die ursprünglichen Panels und Bulk-Dateien im Projekt weiterhin vorhanden; die Analysepanels sind lediglich eine bereinigte Sicht darauf.

---

_Dieser Methodenentwurf ist bewusst ausführlich. In einem späteren Artikel werden wir daraus die strukturierte „Methods“-Sektion extrahieren, ggf. mit gekürzten technischen Details und Verweisen auf ein Online-Repository (z. B. GitHub) für den vollständigen Code und die Daten._ 

