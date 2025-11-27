"""
Extend the panel with governance indicators (WGI Control of Corruption, Rule of Law).
"""

from pathlib import Path
from typing import List

import pandas as pd

from cepalstat_client import SOUTH_AMERICA_ISO3, logger
from worldbank_client import fetch_indicator_panel

ANALYSIS_YEARS: List[int] = [2000, 2010, 2020]

BASE_PANEL_CSV = Path("data_cepal/forest_co2_landuse_panel.csv")
OUTPUT_PANEL_CSV = Path("data_cepal/forest_co2_governance_panel.csv")

WB_CC_CODE = "CC.EST"  # Control of Corruption
WB_RL_CODE = "RL.EST"  # Rule of Law


def load_wgi_indicator(indicator_code: str, value_column: str) -> pd.DataFrame:
    """
    Pull a Worldwide Governance Indicator for South America and analysis years.
    Returns columns: iso3, year, value_column.
    """
    df = fetch_indicator_panel(SOUTH_AMERICA_ISO3, indicator_code, ANALYSIS_YEARS)
    if df.empty:
        return pd.DataFrame(columns=["iso3", "year", value_column])
    df = df.rename(columns={"value": value_column})
    return df[["iso3", "year", value_column]]


def load_control_of_corruption() -> pd.DataFrame:
    return load_wgi_indicator(WB_CC_CODE, "control_of_corruption_est")


def load_rule_of_law() -> pd.DataFrame:
    return load_wgi_indicator(WB_RL_CODE, "rule_of_law_est")


def build_governance_panel() -> pd.DataFrame:
    logger.info("Loading base panel from %s", BASE_PANEL_CSV)
    df = pd.read_csv(BASE_PANEL_CSV)

    cc = load_control_of_corruption()
    rl = load_rule_of_law()

    df = df.merge(cc, on=["iso3", "year"], how="left")
    df = df.merge(rl, on=["iso3", "year"], how="left")

    OUTPUT_PANEL_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PANEL_CSV, index=False)

    logger.info("Governance panel saved to %s with %d rows", OUTPUT_PANEL_CSV, len(df))
    return df


if __name__ == "__main__":
    logger.info("Building governance extension panel...")
    build_governance_panel()
    logger.info("Done.")
