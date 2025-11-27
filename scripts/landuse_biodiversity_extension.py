"""
Extend the panel with land-use and biodiversity indicators from FAOSTAT and CEPAL.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from cepalstat_client import SOUTH_AMERICA_ISO3, get_indicator_all_records, logger
from faostat_client import fetch_faostat_indicator_panel, read_faostat_zip_to_df

ANALYSIS_YEARS: List[int] = [2000, 2010, 2020]

BASE_PANEL_CSV = Path("data_cepal/forest_co2_energy_mix_panel.csv")
OUTPUT_PANEL_CSV = Path("data_cepal/forest_co2_landuse_panel.csv")

# --- FAOSTAT crops / land use configuration ---
# Crops domain (QC) – harvested area
FAOSTAT_DOMAIN_CROPS = "QC"
FAOSTAT_ELEMENT_AREA_HARVESTED = "5312"  # Area harvested (ha)
FAOSTAT_ITEM_SOYBEANS = "236"  # Soybeans
FAOSTAT_ITEM_SUGARCANE = "156"  # Sugar cane

# Land use domain (RL) – land area
FAOSTAT_DOMAIN_LAND = "RL"
FAOSTAT_ELEMENT_LAND_AREA = "5110"  # Area (ha)
FAOSTAT_ITEM_PASTURES = "6655"  # Permanent meadows and pastures

# Optional: Fertilizers
FAOSTAT_DOMAIN_FERTILIZERS = "EF"
FAOSTAT_ELEMENT_N_APPL_RATE = "5157"  # Nutrient application rate (kg/ha)
FAOSTAT_ITEM_NITROGEN_TOTAL = "3102"  # Nitrogen fertilizers, total

# CEPALSTAT protected areas indicator
PROTECTED_AREAS_INDICATOR_ID: Optional[str] = "2260"
DATA_DIR = Path("data_cepal")
FILE_CROPS = DATA_DIR / "Production_Crops_Livestock_E_All_Data_(Normalized).zip"
FILE_LANDUSE = DATA_DIR / "Inputs_LandUse_E_All_Data_(Normalized).zip"
FILE_FERTILIZER = DATA_DIR / "Inputs_FertilizersNutrient_E_All_Data_(Normalized).zip"
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


def load_base_panel() -> pd.DataFrame:
    """
    Load the latest master panel as a starting point.
    """
    if not BASE_PANEL_CSV.exists():
        raise RuntimeError(f"Base panel not found at {BASE_PANEL_CSV}")
    df = pd.read_csv(BASE_PANEL_CSV)
    required_cols = {"iso3", "year"}
    missing = required_cols - set(df.columns)
    if missing:
        raise RuntimeError(f"Base panel missing required columns: {missing}")
    return df


def _find_dimension_id(dimensions: List[Dict[str, Any]], keyword: str) -> int:
    """
    Find a dimension id whose name contains the keyword (case-insensitive).
    """
    for dim in dimensions:
        name = str(dim.get("name") or dim.get("label") or "").lower()
        if keyword.lower() in name:
            dim_id = dim.get("id")
            if dim_id is not None:
                return int(dim_id)
    raise RuntimeError(f"Dimension containing '{keyword}' not found.")


def _build_member_map(dim: Dict[str, Any]) -> Dict[Any, str]:
    """Map member id to member name for a dimension."""
    mapping: Dict[Any, str] = {}
    for member in dim.get("members", []) or []:
        mid = member.get("id")
        name = member.get("name") or member.get("label")
        if mid is not None and name is not None:
            mapping[mid] = str(name)
    return mapping


def _aggregate_faostat_area(
    domain: str,
    item_codes: List[str],
    element_code: str,
    target_column: str,
    scale: float = 1.0,
) -> pd.DataFrame:
    """
    Fetch FAOSTAT data and aggregate value per iso3/year.
    """
    df_raw: pd.DataFrame
    if domain == FAOSTAT_DOMAIN_CROPS and FILE_CROPS.exists():
        df_bulk = read_faostat_zip_to_df(
            str(FILE_CROPS), "Production_Crops_Livestock_E_All_Data_(Normalized).csv"
        )
        df_bulk = df_bulk[
            (df_bulk["Item Code"].astype(str).isin(item_codes))
            & (df_bulk["Element Code"].astype(str) == element_code)
        ]
        df_bulk = df_bulk[df_bulk["Year"].isin(ANALYSIS_YEARS)]
        df_bulk["iso3"] = df_bulk["Area"].map(AREA_NAME_TO_ISO)
        df_bulk = df_bulk[df_bulk["iso3"].isin(SOUTH_AMERICA_ISO3)]
        df_raw = df_bulk.rename(columns={"Year": "year", "Value": "value", "Item Code": "item_code"})[
            ["iso3", "year", "item_code", "value"]
        ]
    elif domain == FAOSTAT_DOMAIN_LAND and FILE_LANDUSE.exists():
        df_bulk = read_faostat_zip_to_df(
            str(FILE_LANDUSE), "Inputs_LandUse_E_All_Data_(Normalized).csv"
        )
        df_bulk = df_bulk[
            (df_bulk["Item Code"].astype(str).isin(item_codes))
            & (df_bulk["Element Code"].astype(str) == element_code)
        ]
        df_bulk = df_bulk[df_bulk["Year"].isin(ANALYSIS_YEARS)]
        df_bulk["iso3"] = df_bulk["Area"].map(AREA_NAME_TO_ISO)
        df_bulk = df_bulk[df_bulk["iso3"].isin(SOUTH_AMERICA_ISO3)]
        df_raw = df_bulk.rename(columns={"Year": "year", "Value": "value", "Item Code": "item_code"})[
            ["iso3", "year", "item_code", "value"]
        ]
    elif domain == FAOSTAT_DOMAIN_FERTILIZERS and FILE_FERTILIZER.exists():
        df_bulk = read_faostat_zip_to_df(
            str(FILE_FERTILIZER), "Inputs_FertilizersNutrient_E_All_Data_(Normalized).csv"
        )
        df_bulk = df_bulk[
            (df_bulk["Item Code"].astype(str).isin(item_codes))
            & (df_bulk["Element Code"].astype(str) == element_code)
        ]
        df_bulk = df_bulk[df_bulk["Year"].isin(ANALYSIS_YEARS)]
        df_bulk["iso3"] = df_bulk["Area"].map(AREA_NAME_TO_ISO)
        df_bulk = df_bulk[df_bulk["iso3"].isin(SOUTH_AMERICA_ISO3)]
        df_raw = df_bulk.rename(columns={"Year": "year", "Value": "value", "Item Code": "item_code"})[
            ["iso3", "year", "item_code", "value"]
        ]
    else:
        df_raw = fetch_faostat_indicator_panel(domain, item_codes, element_code, SOUTH_AMERICA_ISO3, ANALYSIS_YEARS)
    if df_raw.empty:
        raise RuntimeError(f"No FAOSTAT data returned for {domain}/{item_codes}/{element_code}")
    df = df_raw.groupby(["iso3", "year"])["value"].sum().reset_index()
    df[target_column] = df["value"] * scale
    return df[["iso3", "year", target_column]]


def load_soy_and_sugarcane_area() -> pd.DataFrame:
    """
    Harvested area for soybeans and sugarcane (kha) aggregated per iso3/year.
    """
    if FILE_CROPS.exists():
        df_bulk = read_faostat_zip_to_df(
            str(FILE_CROPS), "Production_Crops_Livestock_E_All_Data_(Normalized).csv"
        )
        df_bulk = df_bulk[
            (df_bulk["Item Code"].astype(str).isin([FAOSTAT_ITEM_SOYBEANS, FAOSTAT_ITEM_SUGARCANE]))
            & (df_bulk["Element Code"].astype(str) == FAOSTAT_ELEMENT_AREA_HARVESTED)
            & (df_bulk["Year"].isin(ANALYSIS_YEARS))
        ]
        df_bulk["iso3"] = df_bulk["Area"].map(AREA_NAME_TO_ISO)
        df_bulk = df_bulk[df_bulk["iso3"].isin(SOUTH_AMERICA_ISO3)]
        df_crops = df_bulk.rename(
            columns={"Year": "year", "Value": "value", "Item Code": "item_code"}
        )[["iso3", "year", "item_code", "value"]]
    else:
        df_crops = fetch_faostat_indicator_panel(
            domain=FAOSTAT_DOMAIN_CROPS,
            item_codes=[FAOSTAT_ITEM_SOYBEANS, FAOSTAT_ITEM_SUGARCANE],
            element_code=FAOSTAT_ELEMENT_AREA_HARVESTED,
            iso3_list=SOUTH_AMERICA_ISO3,
            years=ANALYSIS_YEARS,
        )
    if df_crops.empty:
        raise RuntimeError("No FAOSTAT crop data returned for soy/sugarcane.")

    pivoted = (
        df_crops.assign(item_code=df_crops["item_code"].astype(int))
        .pivot_table(index=["iso3", "year"], columns="item_code", values="value", aggfunc="sum")
        .reset_index()
    )
    rename_map = {
        int(FAOSTAT_ITEM_SOYBEANS): "soy_area_kha",
        int(FAOSTAT_ITEM_SUGARCANE): "sugarcane_area_kha",
    }
    pivoted = pivoted.rename(columns=rename_map)
    for col in ("soy_area_kha", "sugarcane_area_kha"):
        if col in pivoted.columns:
            pivoted[col] = pd.to_numeric(pivoted[col], errors="coerce") / 1000.0
    return pivoted[["iso3", "year"] + [c for c in ("soy_area_kha", "sugarcane_area_kha") if c in pivoted.columns]]


def load_pasture_area() -> Optional[pd.DataFrame]:
    """
    Pasture/permanent meadows area (kha) from FAOSTAT land use domain.
    Returns None if constants are not configured.
    """
    if not FAOSTAT_DOMAIN_LAND or not FAOSTAT_ITEM_PASTURES or not FAOSTAT_ELEMENT_LAND_AREA:
        logger.info("Pasture constants not configured; skipping pasture_area_kha.")
        return None
    df = _aggregate_faostat_area(
        FAOSTAT_DOMAIN_LAND,
        [FAOSTAT_ITEM_PASTURES],
        FAOSTAT_ELEMENT_LAND_AREA,
        "pasture_area_kha",
        scale=0.001,
    )
    return df


def load_fertilizer_use() -> Optional[pd.DataFrame]:
    """
    Fertilizer use per hectare if FAOSTAT codes are configured.
    """
    if not FAOSTAT_DOMAIN_FERTILIZERS or not FAOSTAT_ITEM_NITROGEN_TOTAL or not FAOSTAT_ELEMENT_N_APPL_RATE:
        logger.info("Fertilizer constants not configured; skipping fertilizer_use_kg_per_ha.")
        return None
    if FILE_FERTILIZER.exists():
        df_bulk = read_faostat_zip_to_df(
            str(FILE_FERTILIZER), "Inputs_FertilizersNutrient_E_All_Data_(Normalized).csv"
        )
        df_bulk = df_bulk[
            (df_bulk["Item Code"].astype(str) == FAOSTAT_ITEM_NITROGEN_TOTAL)
            & (df_bulk["Element Code"].astype(str) == FAOSTAT_ELEMENT_N_APPL_RATE)
            & (df_bulk["Year"].isin(ANALYSIS_YEARS))
        ]
        df_bulk["iso3"] = df_bulk["Area"].map(AREA_NAME_TO_ISO)
        df_bulk = df_bulk[df_bulk["iso3"].isin(SOUTH_AMERICA_ISO3)]
        df = df_bulk.rename(columns={"Year": "year", "Value": "value"})[["iso3", "year", "value"]]
    else:
        df = fetch_faostat_indicator_panel(
            FAOSTAT_DOMAIN_FERTILIZERS,
            [FAOSTAT_ITEM_NITROGEN_TOTAL],
            FAOSTAT_ELEMENT_N_APPL_RATE,
            SOUTH_AMERICA_ISO3,
            ANALYSIS_YEARS,
        )
        if df.empty:
            logger.warning("No fertilizer data returned; skipping fertilizer_use_kg_per_ha.")
            return None
    df = (
        df.groupby(["iso3", "year"], as_index=False)["value"]
        .mean()
        .rename(columns={"value": "fertilizer_use_kg_per_ha"})
    )
    return df


def load_protected_areas_share() -> Optional[pd.DataFrame]:
    """
    Protected areas share (% of land) from CEPAL if indicator ID is configured.
    """
    if not PROTECTED_AREAS_INDICATOR_ID:
        logger.info("Protected areas indicator ID not set; skipping protected_areas_share_pct.")
        return None

    body = get_indicator_all_records(PROTECTED_AREAS_INDICATOR_ID)
    data = body.get("data", [])
    dimensions = body.get("dimensions", [])
    df = pd.DataFrame(data)
    if df.empty:
        raise RuntimeError("No data returned for protected areas indicator.")

    year_dim_id = _find_dimension_id(dimensions, "year")
    year_map: Dict[Any, str] = {}
    for dim in dimensions:
        if dim.get("id") == year_dim_id:
            year_map = _build_member_map(dim)
            break

    year_col = f"dim_{year_dim_id}"
    if year_col not in df.columns:
        raise RuntimeError(f"Year column {year_col} missing for protected areas indicator.")

    df["year"] = df[year_col].map(year_map)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["protected_areas_share_pct"] = pd.to_numeric(df["value"], errors="coerce")

    df = df[df["iso3"].isin(SOUTH_AMERICA_ISO3)]
    df = df[df["year"].isin(ANALYSIS_YEARS)]
    df = df[["iso3", "year", "protected_areas_share_pct"]].dropna()
    if df.empty:
        logger.warning("No protected areas records remain after filtering.")
        return None
    df["year"] = df["year"].astype(int)
    return df.reset_index(drop=True)


def build_landuse_panel() -> pd.DataFrame:
    """
    Build the land-use/biodiversity extension and save to CSV.
    """
    df = load_base_panel()

    try:
        soy_sugar_df = load_soy_and_sugarcane_area()
        df = df.merge(soy_sugar_df, on=["iso3", "year"], how="left")
    except RuntimeError as exc:
        logger.warning("Skipping soy/sugarcane areas due to error: %s", exc)

    try:
        pasture_df = load_pasture_area()
        if pasture_df is not None:
            df = df.merge(pasture_df, on=["iso3", "year"], how="left")
    except RuntimeError as exc:
        logger.warning("Skipping pasture area due to error: %s", exc)

    try:
        fert_df = load_fertilizer_use()
        if fert_df is not None:
            df = df.merge(fert_df, on=["iso3", "year"], how="left")
    except RuntimeError as exc:
        logger.warning("Skipping fertilizer use due to error: %s", exc)

    try:
        protected_df = load_protected_areas_share()
        if protected_df is not None:
            df = df.merge(protected_df, on=["iso3", "year"], how="left")
    except RuntimeError as exc:
        logger.warning("Skipping protected areas due to error: %s", exc)

    logger.info("Land-use panel rows: %d", len(df))
    logger.info("Missing values per column:\n%s", df.isna().sum())

    OUTPUT_PANEL_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PANEL_CSV, index=False)
    return df


if __name__ == "__main__":
    logger.info("Building land-use/biodiversity extension for South America...")
    panel_df = build_landuse_panel()
    logger.info("Done. Saved %d rows to %s", len(panel_df), OUTPUT_PANEL_CSV)
