"""
Build an extended panel combining forest/CO2 data with agriculture value added and
World Bank indicators for South America (2000, 2010, 2020).
"""

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from cepalstat_client import (
    SOUTH_AMERICA_ISO3,
    get_indicator_all_records,
    logger,
)
from worldbank_client import fetch_indicator_panel

ANALYSIS_YEARS: List[int] = [2000, 2010, 2020]

FOREST_CO2_PANEL_CSV = Path("data_cepal/forest_co2_decadal_panel.csv")
EXTENDED_PANEL_CSV = Path("data_cepal/forest_co2_extended_panel.csv")

AGR_VALUE_ADDED_INDICATOR_ID = "3745"  # AG_PRD_AGVAS: Agriculture value added share of GDP (%)

WB_HYDRO_SHARE_CODE = "EG.ELC.HYRO.ZS"
WB_GDP_PCAP_PPP_CODE = "NY.GDP.PCAP.PP.KD"
WB_AG_LAND_SHARE_CODE = "AG.LND.AGRI.ZS"
WB_URBAN_POP_SHARE_CODE = "SP.URB.TOTL.IN.ZS"


def _find_dimension_id(dimensions: List[Dict[str, Any]], keyword: str) -> int:
    """Find dimension id whose name contains keyword."""
    for dim in dimensions:
        name = str(dim.get("name") or dim.get("label") or "").lower()
        if keyword.lower() in name:
            dim_id = dim.get("id")
            if dim_id is not None:
                return int(dim_id)
    raise RuntimeError(f"Dimension containing '{keyword}' not found.")


def _build_member_map(dim: Dict[str, Any]) -> Dict[Any, str]:
    """Map member id to name for a dimension."""
    mapping: Dict[Any, str] = {}
    for member in dim.get("members", []) or []:
        mid = member.get("id")
        name = member.get("name") or member.get("label")
        if mid is not None and name is not None:
            mapping[mid] = str(name)
    return mapping


def load_base_forest_co2_panel() -> pd.DataFrame:
    """
    Load existing forest/CO2 panel CSV.
    """
    if not FOREST_CO2_PANEL_CSV.exists():
        raise RuntimeError(f"Base panel not found at {FOREST_CO2_PANEL_CSV}")
    df = pd.read_csv(FOREST_CO2_PANEL_CSV)
    required_cols = {
        "iso3",
        "year",
        "forest_area_kha",
        "forest_area_kha_decadal_change_pct",
        "co2_per_gdp_kg_per_usd",
        "co2_per_gdp_kg_per_usd_decadal_change_pct",
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise RuntimeError(f"Base panel missing required columns: {missing}")
    return df


def load_agriculture_value_added_cepal() -> pd.DataFrame:
    """
    Fetch agriculture value added share of GDP (%) from CEPAL (indicator 3745).
    Filters to South America, analysis years, and reporting type Global.

    Returns columns: iso3, year, agriculture_value_added_share_gdp_pct.
    """
    body = get_indicator_all_records(AGR_VALUE_ADDED_INDICATOR_ID)
    data = body.get("data", [])
    dimensions = body.get("dimensions", [])
    df = pd.DataFrame(data)
    if df.empty:
        raise RuntimeError("No data returned for agriculture value added indicator.")

    year_dim_id = _find_dimension_id(dimensions, "year")
    reporting_dim_id = _find_dimension_id(dimensions, "reporting")

    year_map: Dict[Any, str] = {}
    reporting_map: Dict[Any, str] = {}
    for dim in dimensions:
        if dim.get("id") == year_dim_id:
            year_map = _build_member_map(dim)
        elif dim.get("id") == reporting_dim_id:
            reporting_map = _build_member_map(dim)
    if not year_map:
        raise RuntimeError("Year member map empty for agriculture value added indicator.")
    if not reporting_map:
        raise RuntimeError("Reporting member map empty for agriculture value added indicator.")

    year_col = f"dim_{year_dim_id}"
    reporting_col = f"dim_{reporting_dim_id}"
    if year_col not in df.columns:
        raise RuntimeError(f"Year column {year_col} missing in agriculture value added data.")
    if reporting_col not in df.columns:
        raise RuntimeError(f"Reporting column {reporting_col} missing in agriculture value added data.")

    df["year"] = df[year_col].map(year_map)
    df["reporting_type"] = df[reporting_col].map(reporting_map)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["agriculture_value_added_share_gdp_pct"] = pd.to_numeric(df["value"], errors="coerce")

    df = df[df["iso3"].isin(SOUTH_AMERICA_ISO3)]
    df = df[df["year"].isin(ANALYSIS_YEARS)]
    df = df[df["reporting_type"].str.lower() == "global"]

    df = df[["iso3", "year", "agriculture_value_added_share_gdp_pct"]].dropna()
    df["year"] = df["year"].astype(int)
    return df.reset_index(drop=True)


def load_worldbank_indicator(indicator_code: str, value_column_name: str) -> pd.DataFrame:
    """
    Wrapper to fetch a World Bank indicator and return tidy df with renamed value column.
    """
    df = fetch_indicator_panel(SOUTH_AMERICA_ISO3, indicator_code, ANALYSIS_YEARS)
    if df.empty:
        raise RuntimeError(f"No data returned for World Bank indicator {indicator_code}.")
    df = df.rename(columns={"value": value_column_name})
    return df


def load_hydro_share() -> pd.DataFrame:
    return load_worldbank_indicator(WB_HYDRO_SHARE_CODE, "hydro_electricity_share_pct")


def load_gdp_per_capita_ppp() -> pd.DataFrame:
    return load_worldbank_indicator(WB_GDP_PCAP_PPP_CODE, "gdp_per_capita_ppp_const2017")


def load_agricultural_land_share() -> pd.DataFrame:
    return load_worldbank_indicator(WB_AG_LAND_SHARE_CODE, "agricultural_land_share_pct")


def load_urban_population_share() -> pd.DataFrame:
    return load_worldbank_indicator(WB_URBAN_POP_SHARE_CODE, "urban_population_share_pct")


def build_extended_panel() -> pd.DataFrame:
    """
    Build extended panel by merging base forest/CO2 data with CEPAL agriculture value added
    and World Bank indicators.
    """
    df = load_base_forest_co2_panel()
    df = df.merge(load_agriculture_value_added_cepal(), on=["iso3", "year"], how="left")
    df = df.merge(load_hydro_share(), on=["iso3", "year"], how="left")
    df = df.merge(load_gdp_per_capita_ppp(), on=["iso3", "year"], how="left")
    df = df.merge(load_agricultural_land_share(), on=["iso3", "year"], how="left")
    df = df.merge(load_urban_population_share(), on=["iso3", "year"], how="left")

    logger.info("Extended panel rows: %d", len(df))
    missing_counts = df.isna().sum()
    logger.info("Missing values per column:\n%s", missing_counts)

    EXTENDED_PANEL_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(EXTENDED_PANEL_CSV, index=False)
    return df


if __name__ == "__main__":
    logger.info("Building extended forest/energy panel for South America...")
    panel_df = build_extended_panel()
    logger.info("Done. Saved %d rows to %s", len(panel_df), EXTENDED_PANEL_CSV)
