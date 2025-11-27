"""
Basic exploratory analysis for the master forest/energy panel.

Computes descriptive statistics, correlations and simple cross-sectional OLS
regressions for the years 2000, 2010 and 2020.
"""

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from cepalstat_client import logger

PANEL_WITH_CONTROLS = Path("data_cepal/master_forest_energy_controls_panel.csv")
PANEL_BASE = Path("data_cepal/master_forest_energy_panel.csv")

ANALYSIS_YEARS: List[int] = [2000, 2010, 2020]


def load_panel() -> pd.DataFrame:
    """
    Load the most complete master panel (with controls if available).
    """
    if PANEL_WITH_CONTROLS.exists():
        path = PANEL_WITH_CONTROLS
    elif PANEL_BASE.exists():
        path = PANEL_BASE
    else:
        raise RuntimeError("No master panel CSV found.")
    logger.info("Loading panel from %s", path)
    df = pd.read_csv(path)
    return df


def describe_by_year(df: pd.DataFrame) -> None:
    """
    Print basic descriptive statistics per year for key variables.
    """
    vars_to_describe = [
        "forest_area_kha",
        "co2_per_gdp_kg_per_usd",
        "lulucf_forest_kt_co2eq",
        "lulucf_total_kt_co2eq",
        "soy_area_kha",
        "sugarcane_area_kha",
        "pasture_area_kha",
        "fertilizer_use_kg_per_ha",
        "gdp_per_capita_ppp_const2017",
        "population_total",
        "population_density",
    ]
    logger.info("Descriptive statistics by year:")
    for year in ANALYSIS_YEARS:
        sub = df[df["year"] == year]
        if sub.empty:
            continue
        logger.info("Year %d:", year)
        desc = sub[vars_to_describe].describe().T
        print(f"\n=== Descriptives {year} ===")
        print(desc[["mean", "std", "min", "max"]])


def correlation_by_year(df: pd.DataFrame) -> None:
    """
    Print correlation matrices for selected variables by year.
    """
    vars_for_corr = [
        "forest_area_kha",
        "co2_per_gdp_kg_per_usd",
        "lulucf_total_kt_co2eq",
        "soy_area_kha",
        "pasture_area_kha",
        "fertilizer_use_kg_per_ha",
        "hydro_electricity_share_pct",
        "gdp_per_capita_ppp_const2017",
        "population_density",
    ]
    logger.info("Correlation matrices by year:")
    for year in ANALYSIS_YEARS:
        sub = df[df["year"] == year]
        if sub.empty:
            continue
        corr = sub[vars_for_corr].corr()
        print(f"\n=== Correlations {year} ===")
        print(corr)


def run_ols(
    df: pd.DataFrame,
    year: int,
    y_col: str,
    x_cols: List[str],
) -> None:
    """
    Run simple OLS for a given year and print coefficients.
    """
    sub = df[df["year"] == year].dropna(subset=[y_col] + x_cols)
    if sub.empty:
        logger.warning("No data for OLS in year %d.", year)
        return
    y = sub[y_col].to_numpy(dtype=float)
    X = sub[x_cols].to_numpy(dtype=float)
    # Add intercept
    X = np.column_stack([np.ones(len(X)), X])
    try:
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    except np.linalg.LinAlgError as exc:
        logger.warning("OLS failed for year %d: %s", year, exc)
        return
    print(f"\n=== OLS {year}: {y_col} ~ " + " + ".join(x_cols) + " ===")
    print("Intercept:", beta[0])
    for name, coef in zip(x_cols, beta[1:]):
        print(f"{name}: {coef}")


def run_basic_ols_set(df: pd.DataFrame) -> None:
    """
    Run a small set of illustrative OLS models for each year.
    """
    y = "co2_per_gdp_kg_per_usd"
    x = [
        "forest_area_kha",
        "soy_area_kha",
        "hydro_electricity_share_pct",
        "gdp_per_capita_ppp_const2017",
        "population_density",
    ]
    for year in ANALYSIS_YEARS:
        run_ols(df, year, y_col=y, x_cols=x)


def main() -> None:
    df = load_panel()
    describe_by_year(df)
    correlation_by_year(df)
    run_basic_ols_set(df)


if __name__ == "__main__":
    logger.info("Running analysis on master forest/energy panel...")
    main()
    logger.info("Analysis complete.")

