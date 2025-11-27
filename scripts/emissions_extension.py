"""
Extend the panel with emissions indicators (methane, LULUCF).
"""

from pathlib import Path
from typing import List, Optional

import pandas as pd

from cepalstat_client import SOUTH_AMERICA_ISO3, logger
from worldbank_client import fetch_indicator_panel
from faostat_client import fetch_faostat_indicator_panel, read_faostat_zip_to_df

ANALYSIS_YEARS: List[int] = [2000, 2010, 2020]

BASE_PANEL_CSV = Path("data_cepal/forest_co2_socio_panel.csv")
OUTPUT_PANEL_CSV = Path("data_cepal/forest_co2_emissions_panel.csv")

WB_METHANE = "EN.ATM.METH.KT.CE"

# FAOSTAT bulk files
DATA_DIR = Path("data_cepal")
FILE_EMISSIONS_FOREST = DATA_DIR / "Emissions_Land_Use_Forests_E_All_Data_(Normalized).zip"
FILE_EMISSIONS_TOTAL = DATA_DIR / "Emissions_Totals_E_All_Data_(Normalized).zip"

# FAOSTAT codes
FAO_GHG_DOMAIN = "GHG"
FAO_LULUCF_ELEMENT_CO2EQ = "723113"  # Emissions (CO2eq) from AR5 (kt)
FAO_ITEM_FOREST_LAND = 6751  # Forestland
FAO_ITEM_LULUCF_TOTAL = 1707  # LULUCF total (Totals file)

AREA_NAME_TO_ISO = {
    "Argentina": "ARG",
    "Bolivia (Plurinational State of)": "BOL",
    "Brazil": "BRA",
    "Chile": "CHL",
    "Colombia": "COL",
    "Ecuador": "ECU",
    "Guyana": "GUY",
    "Paraguay": "PRY",
    "Peru": "PER",
    "Suriname": "SUR",
    "Uruguay": "URY",
    "Venezuela (Bolivarian Republic of)": "VEN",
}


def load_methane_emissions() -> pd.DataFrame:
    try:
        df = fetch_indicator_panel(SOUTH_AMERICA_ISO3, WB_METHANE, ANALYSIS_YEARS)
    except RuntimeError as exc:
        logger.warning("Methane indicator %s not available: %s", WB_METHANE, exc)
        return pd.DataFrame(columns=["iso3", "year", "methane_emissions_kt_co2eq"])
    if df.empty:
        return pd.DataFrame(columns=["iso3", "year", "methane_emissions_kt_co2eq"])
    df = df.rename(columns={"value": "methane_emissions_kt_co2eq"})
    return df[["iso3", "year", "methane_emissions_kt_co2eq"]]


def _read_emissions_zip(zip_path: Path, csv_name: str, item_code: int) -> Optional[pd.DataFrame]:
    if not zip_path.exists():
        return None
    df = read_faostat_zip_to_df(str(zip_path), csv_name)
    df = df[
        (df["Element Code"].astype(str) == FAO_LULUCF_ELEMENT_CO2EQ)
        & (df["Item Code"].astype(int) == item_code)
        & (df["Year"].isin(ANALYSIS_YEARS))
    ].copy()
    df["iso3"] = df["Area"].map(AREA_NAME_TO_ISO)
    df = df[df["iso3"].isin(SOUTH_AMERICA_ISO3)]
    if df.empty:
        return None
    df = df.rename(columns={"Year": "year", "Value": "value"})[["iso3", "year", "value"]]
    df = df.groupby(["iso3", "year"], as_index=False)["value"].sum()
    return df


def load_lulucf_forest() -> pd.DataFrame:
    df = _read_emissions_zip(
        FILE_EMISSIONS_FOREST,
        "Emissions_Land_Use_Forests_E_All_Data_(Normalized).csv",
        FAO_ITEM_FOREST_LAND,
    )
    if df is None:
        return pd.DataFrame(columns=["iso3", "year", "lulucf_forest_kt_co2eq"])
    return df.rename(columns={"value": "lulucf_forest_kt_co2eq"})


def load_lulucf_total() -> pd.DataFrame:
    df = _read_emissions_zip(
        FILE_EMISSIONS_TOTAL,
        "Emissions_Totals_E_All_Data_(Normalized).csv",
        FAO_ITEM_LULUCF_TOTAL,
    )
    if df is None:
        return pd.DataFrame(columns=["iso3", "year", "lulucf_total_kt_co2eq"])
    return df.rename(columns={"value": "lulucf_total_kt_co2eq"})


def build_emissions_panel() -> pd.DataFrame:
    logger.info("Loading base panel %s", BASE_PANEL_CSV)
    df = pd.read_csv(BASE_PANEL_CSV)

    meth = load_methane_emissions()
    lulucf_forest = load_lulucf_forest()
    lulucf_total = load_lulucf_total()

    df = df.merge(meth, on=["iso3", "year"], how="left")
    df = df.merge(lulucf_forest, on=["iso3", "year"], how="left")
    df = df.merge(lulucf_total, on=["iso3", "year"], how="left")

    OUTPUT_PANEL_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PANEL_CSV, index=False)

    logger.info("Emissions panel saved to %s", OUTPUT_PANEL_CSV)
    return df


if __name__ == "__main__":
    logger.info("Building emissions extension panel...")
    build_emissions_panel()
    logger.info("Done.")
