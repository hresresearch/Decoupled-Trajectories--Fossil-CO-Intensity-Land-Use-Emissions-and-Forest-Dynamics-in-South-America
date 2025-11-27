"""
Erzeuge ein einfaches Codebook für die wichtigsten Panel-Variablen.

Schreibt data_cepal/variables_codebook.csv mit Spalten:
- variable
- description
- source
- unit
"""

from pathlib import Path

import pandas as pd

from cepalstat_client import logger

OUTPUT_CSV = Path("data_cepal/variables_codebook.csv")


def build_codebook() -> pd.DataFrame:
    entries = [
        # Level-Variablen
        {
            "variable": "iso3",
            "description": "Country ISO3 code",
            "source": "Multiple (CEPALSTAT, FAOSTAT, World Bank)",
            "unit": "-",
        },
        {
            "variable": "year",
            "description": "Calendar year",
            "source": "Multiple",
            "unit": "year",
        },
        {
            "variable": "forest_area_kha",
            "description": "Forest area",
            "source": "CEPALSTAT indicator 2036",
            "unit": "thousand hectares",
        },
        {
            "variable": "co2_per_gdp_kg_per_usd",
            "description": "CO2 emissions per unit of GDP PPP (constant 2017 USD)",
            "source": "CEPALSTAT indicator 3914",
            "unit": "kg CO2 / USD",
        },
        {
            "variable": "agriculture_value_added_share_gdp_pct",
            "description": "Agriculture value added as share of GDP",
            "source": "CEPALSTAT indicator 3745",
            "unit": "percent",
        },
        {
            "variable": "gdp_per_capita_ppp_const2017",
            "description": "GDP per capita, PPP (constant 2017 international dollars)",
            "source": "World Bank NY.GDP.PCAP.PP.KD",
            "unit": "2017 international USD per capita",
        },
        {
            "variable": "hydro_electricity_share_pct",
            "description": "Electricity production from hydroelectric sources, share of total",
            "source": "World Bank EG.ELC.HYRO.ZS",
            "unit": "percent",
        },
        {
            "variable": "electricity_share_coal_pct",
            "description": "Electricity production from coal sources, share of total",
            "source": "World Bank EG.ELC.COAL.ZS",
            "unit": "percent",
        },
        {
            "variable": "electricity_share_gas_pct",
            "description": "Electricity production from natural gas sources, share of total",
            "source": "World Bank EG.ELC.NGAS.ZS",
            "unit": "percent",
        },
        {
            "variable": "electricity_share_renewables_excl_hydro_pct",
            "description": "Electricity production from renewables excluding hydro, share of total",
            "source": "World Bank EG.ELC.RNWX.ZS",
            "unit": "percent",
        },
        {
            "variable": "electrification_rate_pct",
            "description": "Access to electricity, total",
            "source": "World Bank EG.ELC.ACCS.ZS",
            "unit": "percent of population",
        },
        {
            "variable": "soy_area_kha",
            "description": "Soy harvested area",
            "source": "FAOSTAT Production Crops & Livestock (Item Code 236, Element 5312)",
            "unit": "thousand hectares",
        },
        {
            "variable": "sugarcane_area_kha",
            "description": "Sugarcane harvested area",
            "source": "FAOSTAT Production Crops & Livestock (Item Code 156, Element 5312)",
            "unit": "thousand hectares",
        },
        {
            "variable": "pasture_area_kha",
            "description": "Permanent meadows and pastures area",
            "source": "FAOSTAT Inputs LandUse (Item Code 6655, Element 5110)",
            "unit": "thousand hectares",
        },
        {
            "variable": "fertilizer_use_kg_per_ha",
            "description": "Nitrogen fertilizer application rate",
            "source": "FAOSTAT Inputs Fertilizers by Nutrient (Item Code 3102, Element 5157)",
            "unit": "kg nutrient per hectare",
        },
        {
            "variable": "lulucf_total_kt_co2eq",
            "description": "Total LULUCF net GHG emissions",
            "source": "FAOSTAT Emissions Totals (Item Code 1707, Element 723113)",
            "unit": "kilotonnes CO2eq",
        },
        {
            "variable": "population_total",
            "description": "Total population",
            "source": "World Bank SP.POP.TOTL",
            "unit": "persons",
        },
        {
            "variable": "population_density",
            "description": "Population density",
            "source": "World Bank EN.POP.DNST",
            "unit": "people per sq. km of land area",
        },
        # Delta-Variablen
        {
            "variable": "delta_forest_pct",
            "description": "Decadal percentage change in forest area",
            "source": "Computed from forest_area_kha",
            "unit": "percent",
        },
        {
            "variable": "delta_co2_intensity_abs",
            "description": "Decadal absolute change in CO2 intensity per GDP",
            "source": "Computed from co2_per_gdp_kg_per_usd",
            "unit": "kg CO2 / USD",
        },
        {
            "variable": "delta_lulucf_per_capita_t_co2eq",
            "description": "Decadal change in LULUCF emissions per capita",
            "source": "Computed from lulucf_total_kt_co2eq and population_total",
            "unit": "tonnes CO2eq per capita",
        },
        {
            "variable": "delta_hydro_share_pct",
            "description": "Decadal change in hydro electricity share",
            "source": "Computed from hydro_electricity_share_pct",
            "unit": "percentage points",
        },
        {
            "variable": "delta_gdp_per_capita",
            "description": "Decadal change in GDP per capita PPP",
            "source": "Computed from gdp_per_capita_ppp_const2017",
            "unit": "2017 international USD per capita",
        },
        {
            "variable": "delta_agri_share_pct",
            "description": "Decadal change in agriculture value added share of GDP",
            "source": "Computed from agriculture_value_added_share_gdp_pct",
            "unit": "percentage points",
        },
    ]

    df = pd.DataFrame(entries)
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    logger.info("Variables codebook saved to %s (%d Einträge).", OUTPUT_CSV, len(df))
    return df


if __name__ == "__main__":
    build_codebook()

