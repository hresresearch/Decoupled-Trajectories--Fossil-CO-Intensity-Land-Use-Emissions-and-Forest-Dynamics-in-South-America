"""
Extend the panel with socio-economic inequality indicators (Gini, rural extreme poverty).
"""

from pathlib import Path
from typing import List

import pandas as pd

from cepalstat_client import (
    SOUTH_AMERICA_ISO3,
    get_indicator_all_records,
    logger,
)

ANALYSIS_YEARS: List[int] = [2000, 2010, 2020]

BASE_PANEL_CSV = Path("data_cepal/forest_co2_governance_panel.csv")
OUTPUT_PANEL_CSV = Path("data_cepal/forest_co2_socio_panel.csv")

GINI_INDICATOR_ID = "3289"
RURAL_POVERTY_INDICATOR_ID = "3328"


def map_cepal_dimensions_to_iso3_year(data: pd.DataFrame, dimensions: List[dict]) -> pd.DataFrame:
    """
    Map CEPAL dimension member IDs to iso3 and year columns using dimensions metadata.
    """
    df = data.copy()
    year_dim_id = None
    for dim in dimensions:
        name = str(dim.get("name") or dim.get("label") or "").lower()
        if "year" in name:
            year_dim_id = dim.get("id")
            break
    if year_dim_id is None:
        raise RuntimeError("Year dimension not found in CEPAL dimensions.")

    year_map = {}
    for dim in dimensions:
        if dim.get("id") == year_dim_id:
            for member in dim.get("members", []) or []:
                mid = member.get("id")
                label = member.get("name") or member.get("label")
                if mid is not None and label is not None:
                    year_map[mid] = label
            break

    year_col = f"dim_{year_dim_id}"
    if year_col not in df.columns:
        raise RuntimeError(f"Year column {year_col} missing in data.")

    df["year"] = df[year_col].map(year_map)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df


def load_cepal_indicator(indicator_id: str, value_column: str) -> pd.DataFrame:
    """
    Fetch a CEPALSTAT indicator and map its dimensions to iso3/year.
    """
    body = get_indicator_all_records(indicator_id)
    data = pd.DataFrame(body.get("data", []))
    dims = body.get("dimensions", [])
    if data.empty or not dims:
        logger.warning("Indicator %s has no data/dimensions", indicator_id)
        return pd.DataFrame(columns=["iso3", "year", value_column])

    df_mapped = map_cepal_dimensions_to_iso3_year(data, dims)
    if "iso3" not in df_mapped.columns:
        raise RuntimeError(f"Indicator {indicator_id} data missing iso3 column.")

    df_mapped = df_mapped[df_mapped["iso3"].isin(SOUTH_AMERICA_ISO3)]
    df_mapped = df_mapped[df_mapped["year"].isin(ANALYSIS_YEARS)]
    df_mapped = df_mapped.rename(columns={"value": value_column})
    df_mapped[value_column] = pd.to_numeric(df_mapped[value_column], errors="coerce")
    return df_mapped[["iso3", "year", value_column]]


def load_gini_index() -> pd.DataFrame:
    return load_cepal_indicator(GINI_INDICATOR_ID, "gini_index")


def load_rural_extreme_poverty() -> pd.DataFrame:
    return load_cepal_indicator(RURAL_POVERTY_INDICATOR_ID, "rural_extreme_poverty_pct")


def build_socio_panel() -> pd.DataFrame:
    logger.info("Loading base panel: %s", BASE_PANEL_CSV)
    df = pd.read_csv(BASE_PANEL_CSV)

    gini = load_gini_index()
    poverty = load_rural_extreme_poverty()

    df = df.merge(gini, on=["iso3", "year"], how="left")
    df = df.merge(poverty, on=["iso3", "year"], how="left")

    OUTPUT_PANEL_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PANEL_CSV, index=False)

    logger.info("Socio panel saved: %s", OUTPUT_PANEL_CSV)
    return df


if __name__ == "__main__":
    logger.info("Building socio inequality extension panel...")
    build_socio_panel()
    logger.info("Done.")
