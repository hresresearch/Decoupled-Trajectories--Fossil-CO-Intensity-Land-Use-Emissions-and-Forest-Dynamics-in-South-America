# Tables

## Table 1. Overview of variables, data sources and units

| Variable                                      | Description                                                                                           | Source                                                                                          | Unit                                   |
|-----------------------------------------------|-------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|----------------------------------------|
| iso3                                          | Country ISO3 code                                                                                     | Multiple (CEPALSTAT, FAOSTAT, World Bank)                                                      | –                                      |
| year                                          | Calendar year                                                                                         | Multiple                                                                                       | year                                   |
| forest_area_kha                               | Forest area                                                                                           | CEPALSTAT indicator 2036                                                                       | thousand hectares                      |
| co2_per_gdp_kg_per_usd                        | CO₂ emissions per unit of GDP PPP (constant 2017 USD)                                                | CEPALSTAT indicator 3914                                                                       | kg CO₂ per USD                         |
| agriculture_value_added_share_gdp_pct         | Agriculture value added as share of GDP                                                              | CEPALSTAT indicator 3745                                                                       | percent                                |
| gdp_per_capita_ppp_const2017                  | GDP per capita, PPP (constant 2017 international dollars)                                            | World Bank NY.GDP.PCAP.PP.KD                                                                   | 2017 international USD per capita      |
| hydro_electricity_share_pct                   | Electricity production from hydropower, share of total                                               | World Bank EG.ELC.HYRO.ZS                                                                      | percent                                |
| electricity_share_coal_pct                    | Electricity production from coal, share of total                                                     | World Bank EG.ELC.COAL.ZS                                                                      | percent                                |
| electricity_share_gas_pct                     | Electricity production from natural gas, share of total                                              | World Bank EG.ELC.NGAS.ZS                                                                      | percent                                |
| electricity_share_renewables_excl_hydro_pct   | Electricity production from renewables excluding hydropower, share of total                          | World Bank EG.ELC.RNWX.ZS                                                                      | percent                                |
| electrification_rate_pct                      | Access to electricity, total                                                                         | World Bank EG.ELC.ACCS.ZS                                                                      | percent of population                  |
| soy_area_kha                                  | Soy harvested area                                                                                   | FAOSTAT Production Crops & Livestock (Item 236, Element 5312)                                  | thousand hectares                      |
| sugarcane_area_kha                            | Sugarcane harvested area                                                                             | FAOSTAT Production Crops & Livestock (Item 156, Element 5312)                                  | thousand hectares                      |
| pasture_area_kha                              | Permanent meadows and pastures area                                                                  | FAOSTAT Inputs LandUse (Item 6655, Element 5110)                                               | thousand hectares                      |
| fertilizer_use_kg_per_ha                      | Nitrogen fertiliser application rate                                                                 | FAOSTAT Inputs Fertilisers by Nutrient (Item 3102, Element 5157)                               | kg nutrient per hectare                |
| lulucf_total_kt_co2eq                         | Total LULUCF net GHG emissions                                                                       | FAOSTAT Emissions Totals (Item 1707, Element 723113)                                           | kilotonnes CO₂‑equivalent              |
| population_total                              | Total population                                                                                     | World Bank SP.POP.TOTL                                                                         | persons                                |
| population_density                            | Population density                                                                                   | World Bank EN.POP.DNST                                                                         | people per sq. km of land area         |
| delta_forest_pct                              | Decadal percentage change in forest area                                                             | Computed from forest_area_kha                                                                  | percent                                |
| delta_co2_intensity_abs                       | Decadal absolute change in CO₂ intensity per unit of GDP                                             | Computed from co2_per_gdp_kg_per_usd                                                           | kg CO₂ per USD                         |
| delta_lulucf_per_capita_t_co2eq               | Decadal change in LULUCF emissions per capita                                                        | Computed from lulucf_total_kt_co2eq and population_total                                       | tonnes CO₂‑equivalent per capita       |
| delta_hydro_share_pct                         | Decadal change in hydropower electricity share                                                       | Computed from hydro_electricity_share_pct                                                      | percentage points                      |
| delta_gdp_per_capita                          | Decadal change in GDP per capita PPP                                                                 | Computed from gdp_per_capita_ppp_const2017                                                     | 2017 international USD per capita      |
| delta_agri_share_pct                          | Decadal change in agriculture value added share of GDP                                               | Computed from agriculture_value_added_share_gdp_pct                                            | percentage points                      |

## Table 2. Summary statistics for key variables by year (12 South American countries)

Summary statistics (mean, standard deviation, minimum and maximum) are computed across the twelve countries for each benchmark year.

| Variable                                 | Year | Mean        | Std. dev.   | Min         | Max          |
|------------------------------------------|------|------------:|------------:|------------:|-------------:|
| Forest area (thousand hectares)          | 2000 | 140 795.62  | 181 380.83  | 1 369.00    | 551 088.60   |
|                                          | 2010 | 133 186.01  | 167 836.30  | 1 731.30    | 511 580.70   |
|                                          | 2020 | 128 586.92  | 160 199.83  | 2 031.00    | 496 619.60   |
| Fossil CO₂ intensity of GDP (kg CO₂/USD) | 2000 | 0.165       | 0.066       | 0.064       | 0.284        |
|                                          | 2010 | 0.156       | 0.061       | 0.066       | 0.266        |
|                                          | 2020 | 0.149       | 0.068       | 0.065       | 0.300        |
| LULUCF emissions (kt CO₂‑equivalent)     | 2000 | 338 292.16  | 767 662.03  | −91 141.77  | 2 643 654.00 |
|                                          | 2010 | 265 990.75  | 418 450.78  | −97 622.30  | 1 276 785.00 |
|                                          | 2020 | 132 701.52  | 207 501.80  | 832.71      | 687 373.00   |
| GDP per capita (PPP, 2017 USD)           | 2000 | 11 258.10   | 4 666.53    | 6 146.03    | 22 281.38    |
|                                          | 2010 | 13 962.17   | 5 159.45    | 7 571.68    | 28 056.26    |
|                                          | 2020 | 14 745.79   | 5 425.81    | 9 000.98    | 27 788.19    |
| Agriculture share of GDP (%)             | 2000 | –           | –           | –           | –            |
|                                          | 2010 | 9.40        | 7.53        | 3.62        | 28.53        |
|                                          | 2020 | 7.64        | 4.01        | 4.04        | 16.85        |
| Hydropower share of electricity (%)      | 2000 | 68.75       | 29.05       | 0.31        | 100.00       |
|                                          | 2010 | 60.66       | 28.91       | 0.00        | 100.00       |
|                                          | 2020 | 54.54       | 34.39       | 0.00        | 100.00       |

Note: The agriculture share of GDP is not available for all countries in 2000 in the analysis panel.

## Table 3. Decadal changes in fossil CO₂ intensity of GDP, hydropower share and GDP per capita by country and period

| Country | Period end year | Δ CO₂ intensity (kg CO₂/USD) | Δ hydropower share (percentage points) | Δ GDP per capita PPP (2017 USD) |
|---------|-----------------|-----------------------------:|---------------------------------------:|---------------------------------:|
| ARG     | 2010            | −0.014                       | −6.88                                  | 5 774.88                         |
| ARG     | 2020            | −0.004                       | −12.54                                 | −4 179.16                        |
| BOL     | 2010            | 0.045                        | −17.42                                 | 1 425.65                         |
| BOL     | 2020            | −0.016                       | −3.23                                  | 1 429.30                         |
| BRA     | 2010            | −0.014                       | −9.04                                  | 4 056.81                         |
| BRA     | 2020            | 0.000                        | −15.16                                 | −734.64                          |
| CHL     | 2010            | −0.014                       | −10.26                                 | 6 591.50                         |
| CHL     | 2020            | 0.000                        | −9.89                                  | 2 131.79                         |
| COL     | 2010            | −0.037                       | −7.73                                  | 3 223.57                         |
| COL     | 2020            | −0.003                       | −3.81                                  | 1 824.44                         |
| ECU     | 2010            | 0.028                        | −27.46                                 | 2 482.65                         |
| ECU     | 2020            | −0.041                       | 33.61                                  | 774.63                           |
| GUY     | 2010            | −0.046                       | −0.31                                  | 2 349.10                         |
| GUY     | 2020            | −0.062                       | 0.00                                   | 8 859.74                         |
| PER     | 2010            | −0.011                       | −25.35                                 | 4 389.92                         |
| PER     | 2020            | −0.024                       | 1.94                                   | 1 550.58                         |
| PRY     | 2010            | 0.002                        | 0.00                                   | 2 739.98                         |
| PRY     | 2020            | 0.007                        | 0.00                                   | 2 253.08                         |
| SUR     | 2010            | −0.051                       | −18.21                                 | 6 552.30                         |
| SUR     | 2020            | 0.083                        | −22.21                                 | −3 681.11                        |
| URY     | 2010            | −0.012                       | −14.64                                 | 6 127.78                         |
| URY     | 2020            | −0.007                       | −48.17                                 | 2 908.35                         |
| VEN     | 2010            | −0.016                       | −6.26                                  | –                                |
| VEN     | 2020            | 0.034                        | 10.10                                  | –                                |

Note: GDP per capita data for Venezuela at the required level of detail are not available in the analysis panel for both endpoints of each decade.

## Table 4. Decadal changes in per‑capita LULUCF emissions, forest area and agriculture share of GDP (countries with complete data)

| Country | Period end year | Δ LULUCF per capita (t CO₂‑eq) | Δ forest area (%) | Δ agriculture share of GDP (percentage points) |
|---------|-----------------|-------------------------------:|------------------:|-----------------------------------------------:|
| ARG     | 2020            | −4.02                          | −5.43             | −0.77                                          |
| BOL     | 2020            | −0.71                          | −4.24             | 3.61                                           |
| BRA     | 2020            | −3.30                          | −2.92             | 1.59                                           |
| CHL     | 2020            | 5.95                           | 8.88              | 0.42                                           |
| COL     | 2020            | 0.33                           | −2.74             | 1.15                                           |
| ECU     | 2020            | −1.84                          | −4.07             | 0.11                                           |
| GUY     | 2020            | 5.37                           | −0.56             | −11.68                                         |
| PER     | 2020            | −3.47                          | −2.32             | 0.87                                           |
| PRY     | 2020            | −3.58                          | −17.72            | −2.28                                          |
| SUR     | 2020            | 10.61                          | −0.68             | −1.98                                          |
| URY     | 2020            | 4.68                           | 17.31             | −0.63                                          |

## Table 5. Electricity mix shares by country in 2000 and 2020

| Country | Year | Hydropower share (%) | Coal share (%) | Gas share (%) | Renewables excl. hydropower share (%) |
|---------|------|---------------------:|---------------:|--------------:|--------------------------------------:|
| ARG     | 2000 | 42.76                | 15.82          | 50.51         | −7.48                                 |
| ARG     | 2020 | 35.88                | 2.90           | 50.66         | 6.17                                  |
| BOL     | 2000 | 54.00                | 0.00           | 46.00         | −0.36                                 |
| BOL     | 2020 | 50.77                | 0.00           | 48.80         | 6.42                                  |
| BRA     | 2000 | 87.24                | 3.43           | 7.31          | 2.25                                  |
| BRA     | 2020 | 63.04                | 2.83           | 14.03         | 20.13                                 |
| CHL     | 2000 | 46.20                | 33.88          | 16.33         | 3.25                                  |
| CHL     | 2020 | 26.04                | 20.87          | 30.34         | 22.74                                 |
| COL     | 2000 | 69.37                | 0.35           | 30.55         | −0.23                                 |
| COL     | 2020 | 66.84                | 1.06           | 29.66         | 2.45                                  |
| ECU     | 2000 | 60.31                | 10.07          | 29.57         | 0.00                                  |
| ECU     | 2020 | 64.40                | 0.00           | 33.75         | 1.85                                  |
| GUY     | 2000 | 88.20                | 11.80          | 0.00          | 4.14                                  |
| GUY     | 2020 | 82.38                | 17.62          | 0.00          | 7.23                                  |
| PER     | 2000 | 74.28                | 2.22           | 23.30         | 0.70                                  |
| PER     | 2020 | 76.22                | 0.32           | 17.26         | 6.19                                  |
| PRY     | 2000 | 100.00               | 0.00           | 0.00          | −0.02                                 |
| PRY     | 2020 | 100.00               | 0.00           | 0.00          | 0.55                                  |
| SUR     | 2000 | 72.14                | 27.86          | 0.00          | 16.23                                 |
| SUR     | 2020 | 49.94                | 50.06          | 0.00          | −13.87                                |
| URY     | 2000 | 92.92                | 5.23           | 1.50          | 0.36                                  |
| URY     | 2020 | 30.12                | 29.15          | 6.66          | 63.63                                 |
| VEN     | 2000 | 73.75                | 0.97           | 25.28         | 0.00                                  |
| VEN     | 2020 | 77.59                | 8.48           | 13.80         | 0.13                                  |

Note: Negative values for the share of renewables excluding hydropower in some base years reflect inconsistencies or rounding issues in the underlying source data and are carried through from the analysis panel without adjustment.

## Table 6. Regression results for decadal changes in fossil CO₂ intensity of GDP and per‑capita LULUCF emissions

Ordinary least squares regressions on the decadal‑change panel. Standard errors are heteroskedasticity‑consistent (HC1). P‑values from cluster‑robust standard errors by country are given in notes where they differ materially.

**Model A: Δ fossil CO₂ intensity of GDP (kg CO₂ per USD)**

Dependent variable: decadal absolute change in fossil CO₂ intensity of GDP (`delta_co2_intensity_abs`), N = 22 country–decade observations.

| Regressor                        | Coefficient | Std. error | p‑value |
|----------------------------------|-----------:|-----------:|--------:|
| Constant                         | −0.0042    | 0.0091     | 0.644   |
| Δ forest area (%)                | −0.0005    | 0.0006     | 0.383   |
| Δ hydropower share (p.p.)        | −0.0010    | 0.0003     | 0.001   |
| Δ GDP per capita (2017 USD)      | −5.6×10⁻⁶  | 2.3×10⁻⁶   | 0.017   |

Model statistics: R² = 0.52. With cluster‑robust standard errors by country, p‑values remain below 0.01 for Δ hydropower share and just above 0.05 for Δ GDP per capita.

**Model B: Δ per‑capita LULUCF emissions (t CO₂‑equivalent per capita)**

Dependent variable: decadal change in per‑capita LULUCF emissions (`delta_lulucf_per_capita_t_co2eq`), N = 11 country–decade observations with complete data.

| Regressor                        | Coefficient | Std. error | p‑value |
|----------------------------------|-----------:|-----------:|--------:|
| Constant                         | 0.9194     | 1.1992     | 0.443   |
| Δ forest area (%)                | 0.3330     | 0.0807     | <0.001  |
| Δ agriculture share of GDP (p.p.)| −0.4948    | 0.1472     | 0.001   |

Model statistics: R² = 0.49. Cluster‑robust standard errors by country yield very similar p‑values (both regressors remain significant at the 1% level).

