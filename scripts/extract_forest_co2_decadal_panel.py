"""
Build a decadal panel for forest area vs CO2 per GDP in South America.

This script fetches CEPALSTAT indicators 2036 (forest area) and 3914 (CO2 per
GDP), filters to South American countries and years 2000/2010/2020, computes
decadal percentage changes, and writes a merged panel to CSV.
"""

from typing import Any, Dict, List

import os

import pandas as pd

from cepalstat_client import get_indicator_all_records, SOUTH_AMERICA_ISO3, logger

FOREST_AREA_INDICATOR_ID = "2036"
CO2_PER_GDP_INDICATOR_ID = "3914"

ANALYSIS_YEARS: List[int] = [2000, 2010, 2020]
OUTPUT_CSV = "data_cepal/forest_co2_decadal_panel.csv"


def _find_dimension_id(dimensions: List[Dict[str, Any]], keyword: str) -> int:
    """
    Find a dimension ID whose name contains the given keyword (case-insensitive).
    Raises RuntimeError if not found.
    """
    for dim in dimensions:
        name = str(dim.get("name") or dim.get("label") or "").lower()
        if keyword.lower() in name:
            dim_id = dim.get("id")
            if dim_id is not None:
                return int(dim_id)
    raise RuntimeError(f"Dimension containing '{keyword}' not found in dimensions metadata.")


def _build_member_map(dim: Dict[str, Any]) -> Dict[Any, str]:
    """Return a mapping from member ID to member name for a dimension."""
    members = dim.get("members") or []
    mapping: Dict[Any, str] = {}
    for member in members:
        member_id = member.get("id")
        name = member.get("name") or member.get("label")
        if member_id is not None and name is not None:
            mapping[member_id] = str(name)
    return mapping


def load_forest_area_data() -> pd.DataFrame:
    """
    Download forest area data (indicator 2036), filter to South America and
    ANALYSIS_YEARS, keep only Total forest.

    Returns columns: iso3, year, forest_area_kha.
    """
    body = get_indicator_all_records(FOREST_AREA_INDICATOR_ID)
    data = body.get("data", [])
    dimensions = body.get("dimensions", [])

    df = pd.DataFrame(data)
    if df.empty:
        raise RuntimeError("No data returned for forest area indicator.")

    year_dim_id = _find_dimension_id(dimensions, "year")
    forest_dim_id = _find_dimension_id(dimensions, "forest")

    year_map: Dict[Any, str] = {}
    forest_map: Dict[Any, str] = {}
    for dim in dimensions:
        if dim.get("id") == year_dim_id:
            year_map = _build_member_map(dim)
        elif dim.get("id") == forest_dim_id:
            forest_map = _build_member_map(dim)
    if not year_map:
        raise RuntimeError("Year member map is empty for forest area indicator.")
    if not forest_map:
        raise RuntimeError("Forest type member map is empty for forest area indicator.")

    year_col = f"dim_{year_dim_id}"
    forest_col = f"dim_{forest_dim_id}"
    if year_col not in df.columns:
        raise RuntimeError(f"Year dimension column {year_col} missing in data.")
    if forest_col not in df.columns:
        raise RuntimeError(f"Forest type dimension column {forest_col} missing in data.")

    df["year"] = df[year_col].map(year_map)
    df["forest_type"] = df[forest_col].map(forest_map)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["forest_area_kha"] = pd.to_numeric(df["value"], errors="coerce")

    df = df[df["iso3"].isin(SOUTH_AMERICA_ISO3)]
    df = df[df["year"].isin(ANALYSIS_YEARS)]
    df = df[df["forest_type"].str.lower() == "total forest"]

    df = df[["iso3", "year", "forest_area_kha"]].dropna()
    if df.empty:
        raise RuntimeError("No forest area records found after filtering.")
    df["year"] = df["year"].astype(int)
    return df.reset_index(drop=True)


def load_co2_per_gdp_data() -> pd.DataFrame:
    """
    Download CO2 per GDP data (indicator 3914), filter to South America and
    ANALYSIS_YEARS, keep only reporting type Global.

    Returns columns: iso3, year, co2_per_gdp_kg_per_usd.
    """
    body = get_indicator_all_records(CO2_PER_GDP_INDICATOR_ID)
    data = body.get("data", [])
    dimensions = body.get("dimensions", [])

    df = pd.DataFrame(data)
    if df.empty:
        raise RuntimeError("No data returned for CO2 per GDP indicator.")

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
        raise RuntimeError("Year member map is empty for CO2 per GDP indicator.")
    if not reporting_map:
        raise RuntimeError("Reporting type member map is empty for CO2 per GDP indicator.")

    year_col = f"dim_{year_dim_id}"
    reporting_col = f"dim_{reporting_dim_id}"
    if year_col not in df.columns:
        raise RuntimeError(f"Year dimension column {year_col} missing in data.")
    if reporting_col not in df.columns:
        raise RuntimeError(f"Reporting dimension column {reporting_col} missing in data.")

    df["year"] = df[year_col].map(year_map)
    df["reporting_type"] = df[reporting_col].map(reporting_map)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["co2_per_gdp_kg_per_usd"] = pd.to_numeric(df["value"], errors="coerce")

    df = df[df["iso3"].isin(SOUTH_AMERICA_ISO3)]
    df = df[df["year"].isin(ANALYSIS_YEARS)]
    df = df[df["reporting_type"].str.lower() == "global"]

    df = df[["iso3", "year", "co2_per_gdp_kg_per_usd"]].dropna()
    if df.empty:
        raise RuntimeError("No CO2 per GDP records found after filtering.")
    df["year"] = df["year"].astype(int)
    return df.reset_index(drop=True)


def add_decadal_change(df: pd.DataFrame, value_column: str, group_column: str = "iso3") -> pd.DataFrame:
    """
    Add a '<value_column>_decadal_change_pct' column with pct change per group.
    """
    change_col = f"{value_column}_decadal_change_pct"
    df_sorted = df.sort_values([group_column, "year"]).copy()
    df_sorted[change_col] = df_sorted.groupby(group_column)[value_column].pct_change() * 100
    return df_sorted


def build_forest_co2_decadal_panel() -> pd.DataFrame:
    """
    End-to-end pipeline to build and save the decadal panel.
    """
    logger.info("Loading forest area data (indicator %s)...", FOREST_AREA_INDICATOR_ID)
    df_forest = load_forest_area_data()
    df_forest = add_decadal_change(df_forest, "forest_area_kha")

    logger.info("Loading CO2 per GDP data (indicator %s)...", CO2_PER_GDP_INDICATOR_ID)
    df_co2 = load_co2_per_gdp_data()
    df_co2 = add_decadal_change(df_co2, "co2_per_gdp_kg_per_usd")

    logger.info("Merging datasets...")
    panel = pd.merge(df_forest, df_co2, on=["iso3", "year"], how="inner")
    panel = panel[
        [
            "iso3",
            "year",
            "forest_area_kha",
            "forest_area_kha_decadal_change_pct",
            "co2_per_gdp_kg_per_usd",
            "co2_per_gdp_kg_per_usd_decadal_change_pct",
        ]
    ]

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    panel.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    return panel


if __name__ == "__main__":
    logger.info("Building forest vs CO2 per GDP decadal panel for South America...")
    panel_df = build_forest_co2_decadal_panel()
    logger.info("Done. Saved %d rows to %s", len(panel_df), OUTPUT_CSV)
