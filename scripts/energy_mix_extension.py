"""
Extend the forest/CO2 panel with detailed energy mix indicators from the World Bank.
"""

from pathlib import Path
from typing import List

import pandas as pd

from cepalstat_client import SOUTH_AMERICA_ISO3, logger
from worldbank_client import fetch_indicator_panel

ANALYSIS_YEARS: List[int] = [2000, 2010, 2020]

BASE_PANEL_CSV = Path("data_cepal/forest_co2_extended_panel.csv")
OUTPUT_PANEL_CSV = Path("data_cepal/forest_co2_energy_mix_panel.csv")

WB_HYDRO_SHARE_CODE = "EG.ELC.HYRO.ZS"
WB_COAL_SHARE_CODE = "EG.ELC.COAL.ZS"
WB_GAS_SHARE_CODE = "EG.ELC.NGAS.ZS"
WB_RENEW_EX_HYDRO_CODE = "EG.ELC.RNWX.ZS"
WB_ELECTRIFICATION_CODE = "EG.ELC.ACCS.ZS"


def load_base_panel() -> pd.DataFrame:
    """
    Load the existing extended panel as a starting point.
    """
    if not BASE_PANEL_CSV.exists():
        raise RuntimeError(f"Base panel not found at {BASE_PANEL_CSV}")
    df = pd.read_csv(BASE_PANEL_CSV)
    required_cols = {"iso3", "year"}
    missing = required_cols - set(df.columns)
    if missing:
        raise RuntimeError(f"Base panel missing required columns: {missing}")
    return df


def load_worldbank_indicator(indicator_code: str, value_column: str) -> pd.DataFrame:
    """
    Fetch a World Bank indicator for South America and analysis years.
    """
    df = fetch_indicator_panel(SOUTH_AMERICA_ISO3, indicator_code, ANALYSIS_YEARS)
    if df.empty:
        raise RuntimeError(f"No data returned for World Bank indicator {indicator_code}")
    df = df.rename(columns={"value": value_column})
    return df


def load_hydro_share() -> pd.DataFrame:
    return load_worldbank_indicator(WB_HYDRO_SHARE_CODE, "hydro_electricity_share_pct")


def load_coal_share() -> pd.DataFrame:
    return load_worldbank_indicator(WB_COAL_SHARE_CODE, "electricity_share_coal_pct")


def load_gas_share() -> pd.DataFrame:
    return load_worldbank_indicator(WB_GAS_SHARE_CODE, "electricity_share_gas_pct")


def load_renewables_ex_hydro_share() -> pd.DataFrame:
    return load_worldbank_indicator(WB_RENEW_EX_HYDRO_CODE, "electricity_share_renewables_excl_hydro_pct")


def load_electrification_rate() -> pd.DataFrame:
    return load_worldbank_indicator(WB_ELECTRIFICATION_CODE, "electrification_rate_pct")


def build_energy_mix_panel() -> pd.DataFrame:
    """
    Merge energy mix indicators into the existing panel and save to CSV.
    """
    df = load_base_panel()

    if "hydro_electricity_share_pct" in df.columns:
        df = df.drop(columns=["hydro_electricity_share_pct"])

    df = df.merge(load_hydro_share(), on=["iso3", "year"], how="left")
    df = df.merge(load_coal_share(), on=["iso3", "year"], how="left")
    df = df.merge(load_gas_share(), on=["iso3", "year"], how="left")
    df = df.merge(load_renewables_ex_hydro_share(), on=["iso3", "year"], how="left")
    df = df.merge(load_electrification_rate(), on=["iso3", "year"], how="left")

    logger.info("Energy mix panel rows: %d", len(df))
    missing = df.isna().sum()
    logger.info("Missing values per column:\n%s", missing)

    OUTPUT_PANEL_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PANEL_CSV, index=False)
    return df


if __name__ == "__main__":
    logger.info("Building energy mix extension for South America...")
    panel_df = build_energy_mix_panel()
    logger.info("Done. Saved %d rows to %s", len(panel_df), OUTPUT_PANEL_CSV)
