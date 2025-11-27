"""
Extend the panel with trade and energy-related indicators (terms of trade, renewables, oil rents, GDP).
"""

from pathlib import Path
from typing import List

import pandas as pd

from cepalstat_client import SOUTH_AMERICA_ISO3, get_indicator_all_records, logger
from worldbank_client import fetch_indicator_panel

ANALYSIS_YEARS: List[int] = [2000, 2010, 2020]

BASE_PANEL_CSV = Path("data_cepal/forest_co2_emissions_panel.csv")
OUTPUT_PANEL_CSV = Path("data_cepal/forest_co2_trade_energy_panel.csv")

TERMS_OF_TRADE_INDICATOR_ID = "883"


def map_cepal_dimensions_to_iso3_year(data: pd.DataFrame, dimensions: List[dict]) -> pd.DataFrame:
    df = data.copy()
    year_dim_id = None
    for dim in dimensions:
        name = str(dim.get("name") or dim.get("label") or "").lower()
        if "year" in name:
            year_dim_id = dim.get("id")
            break
    if year_dim_id is None:
        raise RuntimeError("Year dimension not found.")
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
        raise RuntimeError(f"Year column {year_col} missing.")
    df["year"] = df[year_col].map(year_map)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df


def load_terms_of_trade() -> pd.DataFrame:
    body = get_indicator_all_records(TERMS_OF_TRADE_INDICATOR_ID)
    data = pd.DataFrame(body.get("data", []))
    dims = body.get("dimensions", [])
    if data.empty:
        logger.warning("Terms of Trade empty.")
        return pd.DataFrame(columns=["iso3", "year", "terms_of_trade_index"])
    df = map_cepal_dimensions_to_iso3_year(data, dims)
    df = df[df["iso3"].isin(SOUTH_AMERICA_ISO3)]
    df = df[df["year"].isin(ANALYSIS_YEARS)]
    df = df.rename(columns={"value": "terms_of_trade_index"})
    df["terms_of_trade_index"] = pd.to_numeric(df["terms_of_trade_index"], errors="coerce")
    return df[["iso3", "year", "terms_of_trade_index"]]


def load_renewables_share() -> pd.DataFrame:
    df = fetch_indicator_panel(SOUTH_AMERICA_ISO3, "EG.ELC.RNEW.ZS", ANALYSIS_YEARS)
    df = df.rename(columns={"value": "renewable_electricity_share_pct"})
    return df[["iso3", "year", "renewable_electricity_share_pct"]]


def load_oil_rents() -> pd.DataFrame:
    df = fetch_indicator_panel(SOUTH_AMERICA_ISO3, "NY.GDP.PETR.RT.ZS", ANALYSIS_YEARS)
    df = df.rename(columns={"value": "oil_rents_share_gdp_pct"})
    return df[["iso3", "year", "oil_rents_share_gdp_pct"]]


def load_gdp_constant() -> pd.DataFrame:
    df = fetch_indicator_panel(SOUTH_AMERICA_ISO3, "NY.GDP.MKTP.KD", ANALYSIS_YEARS)
    df = df.rename(columns={"value": "gdp_constant_2015_usd"})
    return df[["iso3", "year", "gdp_constant_2015_usd"]]


def build_trade_energy_panel() -> pd.DataFrame:
    df = pd.read_csv(BASE_PANEL_CSV)

    tot = load_terms_of_trade()
    ren = load_renewables_share()
    oil = load_oil_rents()
    gdp = load_gdp_constant()

    df = df.merge(tot, on=["iso3", "year"], how="left")
    df = df.merge(ren, on=["iso3", "year"], how="left")
    df = df.merge(oil, on=["iso3", "year"], how="left")
    df = df.merge(gdp, on=["iso3", "year"], how="left")

    df["non_oil_gdp_constant_2015_usd"] = (
        df["gdp_constant_2015_usd"] * (1.0 - df["oil_rents_share_gdp_pct"].fillna(0) / 100.0)
    )

    OUTPUT_PANEL_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PANEL_CSV, index=False)

    logger.info("Trade-energy panel saved: %s", OUTPUT_PANEL_CSV)
    return df


if __name__ == "__main__":
    logger.info("Building trade & energy extension panel...")
    build_trade_energy_panel()
    logger.info("Done.")
