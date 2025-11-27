"""
Extend the master panel with basic World Bank controls (population, density, CO2 totals).
"""

from pathlib import Path
from typing import List

import pandas as pd

from cepalstat_client import SOUTH_AMERICA_ISO3, logger
from worldbank_client import fetch_indicator_panel

ANALYSIS_YEARS: List[int] = [2000, 2010, 2020]

BASE_PANEL_CSV = Path("data_cepal/master_forest_energy_panel.csv")
OUTPUT_PANEL_CSV = Path("data_cepal/master_forest_energy_controls_panel.csv")

WB_POP_TOTAL = "SP.POP.TOTL"
WB_POP_DENSITY = "EN.POP.DNST"
WB_CO2_TOTAL = "EN.ATM.CO2E.KT"
WB_CO2_PER_CAP = "EN.ATM.CO2E.PC"


def load_wb_indicator(indicator_code: str, value_column: str) -> pd.DataFrame:
    """
    Fetch a World Bank indicator for South America and analysis years and rename value column.
    """
    try:
        df = fetch_indicator_panel(SOUTH_AMERICA_ISO3, indicator_code, ANALYSIS_YEARS)
    except RuntimeError as exc:
        logger.warning("WB indicator %s not available: %s", indicator_code, exc)
        return pd.DataFrame(columns=["iso3", "year", value_column])
    if df.empty:
        logger.warning("No data returned for WB indicator %s", indicator_code)
        return pd.DataFrame(columns=["iso3", "year", value_column])
    df = df.rename(columns={"value": value_column})
    return df[["iso3", "year", value_column]]


def build_controls_panel() -> pd.DataFrame:
    """
    Merge World Bank controls into the master panel and save to CSV.
    """
    if not BASE_PANEL_CSV.exists():
        raise RuntimeError(f"Base master panel not found at {BASE_PANEL_CSV}")

    logger.info("Loading master panel from %s", BASE_PANEL_CSV)
    df = pd.read_csv(BASE_PANEL_CSV)

    pop = load_wb_indicator(WB_POP_TOTAL, "population_total")
    density = load_wb_indicator(WB_POP_DENSITY, "population_density")
    co2_total = load_wb_indicator(WB_CO2_TOTAL, "co2_total_kt")
    co2_pc = load_wb_indicator(WB_CO2_PER_CAP, "co2_per_capita_tons")

    df = df.merge(pop, on=["iso3", "year"], how="left")
    df = df.merge(density, on=["iso3", "year"], how="left")
    df = df.merge(co2_total, on=["iso3", "year"], how="left")
    df = df.merge(co2_pc, on=["iso3", "year"], how="left")

    logger.info("Controls panel rows: %d", len(df))
    logger.info("Missing values per column:\n%s", df.isna().sum())

    OUTPUT_PANEL_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PANEL_CSV, index=False)
    logger.info("Controls-extended master panel saved to %s", OUTPUT_PANEL_CSV)
    return df


if __name__ == "__main__":
    logger.info("Building World Bank controls extension for master panel...")
    build_controls_panel()
    logger.info("Done.")
