"""
Regressionsskript mit statsmodels für das Masterpanel.

Ziele:
- OLS auf Deltas der CO2-Intensität:
  delta_co2_intensity_abs ~ delta_forest_pct + delta_hydro_share_pct + delta_gdp_per_capita
- OLS auf Deltas der LULUCF-Emissionen pro Kopf:
  delta_lulucf_per_capita_t_co2eq ~ delta_forest_pct + delta_agri_share_pct

Es werden klassische und robuste (HC1) Standardfehler ausgegeben.
"""

from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import statsmodels.api as sm

from cepalstat_client import logger

PANEL_WITH_CONTROLS = Path("data_cepal/master_forest_energy_controls_panel.csv")
DELTA_CSV = Path("data_cepal/south_america_delta_panel_processed.csv")

ANALYSIS_YEARS: List[int] = [2000, 2010, 2020]


def load_delta_panel() -> pd.DataFrame:
    """
    Lade das Delta-Panel, falls bereits vorhanden, ansonsten berechne es neu.
    """
    if DELTA_CSV.exists():
        logger.info("Lade Delta-Panel aus %s", DELTA_CSV)
        return pd.read_csv(DELTA_CSV)

    if not PANEL_WITH_CONTROLS.exists():
        raise RuntimeError("Weder Delta-Panel noch Masterpanel mit Controls gefunden.")

    from delta_analysis_panel import load_panel, add_deltas, build_delta_dataset

    logger.info("Erzeuge Delta-Panel neu aus Masterpanel.")
    df = load_panel()
    df = add_deltas(df)
    return build_delta_dataset(df)


def ols_with_robust(y: pd.Series, X: pd.DataFrame, add_const: bool = True) -> None:
    """
    Führe OLS mit klassischen und robusten (HC1) SEs aus und drucke kompakte Ergebnisse.
    """
    if add_const:
        X = sm.add_constant(X)
    model = sm.OLS(y, X, missing="drop")
    results = model.fit()
    robust = results.get_robustcov_results(cov_type="HC1")

    print("\nKlassische OLS-Schätzung:")
    print(results.summary())

    print("\nRobuste (HC1) Standardfehler:")
    out = pd.DataFrame(
        {
            "coef": robust.params,
            "std_err": robust.bse,
            "t": robust.tvalues,
            "P>|t|": robust.pvalues,
        }
    )
    print(out)
    print("R^2:", results.rsquared)


def ols_with_cluster(y: pd.Series, X: pd.DataFrame, groups: pd.Series, add_const: bool = True) -> None:
    """
    OLS mit cluster-robusten Standardfehlern (Cluster = Länder).
    """
    if add_const:
        X = sm.add_constant(X)
    model = sm.OLS(y, X, missing="drop")
    results = model.fit(cov_type="cluster", cov_kwds={"groups": groups})

    print("\nOLS mit Cluster-robusten SE (Cluster = iso3):")
    print(results.summary())


def run_delta_co2_model(df_delta: pd.DataFrame) -> None:
    """
    OLS für Delta CO2-Intensität.
    """
    cols = ["delta_forest_pct", "delta_hydro_share_pct", "delta_gdp_per_capita"]
    sub = df_delta.dropna(subset=["delta_co2_intensity_abs"] + cols).copy()
    if sub.empty:
        logger.warning("Keine Daten für Delta-CO2-Modell.")
        return
    print("\n=== OLS-Modell: ΔCO2-Intensität ===")
    print("Beobachtungen:", len(sub))
    y = sub["delta_co2_intensity_abs"]
    X = sub[cols]
    ols_with_robust(y, X)


def run_delta_co2_model_by_period(df_delta: pd.DataFrame) -> None:
    """
    OLS für Delta CO2-Intensität getrennt nach Dekaden (2000->2010, 2010->2020).
    """
    cols = ["delta_forest_pct", "delta_hydro_share_pct", "delta_gdp_per_capita"]
    for year in [2010, 2020]:
        sub = df_delta[df_delta["year"] == year].dropna(subset=["delta_co2_intensity_abs"] + cols).copy()
        period = f"{year-10}-{year}"
        if len(sub) < len(cols) + 1:
            logger.warning("Zu wenige Beobachtungen für Delta-CO2-Modell in Periode %s.", period)
            continue
        print(f"\n=== OLS ΔCO2-Intensität für Periode {period} ===")
        print("Beobachtungen:", len(sub))
        y = sub["delta_co2_intensity_abs"]
        X = sub[cols]
        ols_with_robust(y, X)


def run_delta_lulucf_model(df_delta: pd.DataFrame) -> None:
    """
    OLS für Delta LULUCF pro Kopf.
    """
    cols = ["delta_forest_pct", "delta_agri_share_pct"]
    sub = df_delta.dropna(subset=["delta_lulucf_per_capita_t_co2eq"] + cols).copy()
    if sub.empty:
        logger.warning("Keine Daten für Delta-LULUCF-Modell.")
        return
    print("\n=== OLS-Modell: ΔLULUCF pro Kopf ===")
    print("Beobachtungen:", len(sub))
    y = sub["delta_lulucf_per_capita_t_co2eq"]
    X = sub[cols]
    ols_with_robust(y, X)


def run_delta_lulucf_model_by_period(df_delta: pd.DataFrame) -> None:
    """
    OLS für Delta LULUCF pro Kopf getrennt nach Dekaden.
    """
    cols = ["delta_forest_pct", "delta_agri_share_pct"]
    for year in [2010, 2020]:
        sub = df_delta[df_delta["year"] == year].dropna(subset=["delta_lulucf_per_capita_t_co2eq"] + cols).copy()
        period = f"{year-10}-{year}"
        if len(sub) < len(cols) + 1:
            logger.warning("Zu wenige Beobachtungen für Delta-LULUCF-Modell in Periode %s.", period)
            continue
        print(f"\n=== OLS ΔLULUCF pro Kopf für Periode {period} ===")
        print("Beobachtungen:", len(sub))
        y = sub["delta_lulucf_per_capita_t_co2eq"]
        X = sub[cols]
        ols_with_robust(y, X)


def run_delta_lulucf_leave_one_out(df_delta: pd.DataFrame) -> None:
    """
    Leave-one-out Robustness für das LULUCF-Delta-Modell.
    """
    cols = ["delta_forest_pct", "delta_agri_share_pct"]
    rows = []
    for iso in sorted(df_delta["iso3"].unique()):
        sub = df_delta[df_delta["iso3"] != iso].dropna(subset=["delta_lulucf_per_capita_t_co2eq"] + cols).copy()
        if len(sub) < len(cols) + 1:
            continue
        y = sub["delta_lulucf_per_capita_t_co2eq"]
        X = sm.add_constant(sub[cols])
        model = sm.OLS(y, X, missing="drop")
        res = model.fit(cov_type="HC1")
        coef = res.params.get("delta_forest_pct", np.nan)
        pval = res.pvalues.get("delta_forest_pct", np.nan)
        rows.append({"omitted_iso3": iso, "coef_delta_forest_pct": coef, "p_value": pval, "n_obs": len(sub)})
    if not rows:
        logger.warning("Keine Daten für Leave-one-out-Analyse.")
        return
    df_res = pd.DataFrame(rows)
    print("\n=== Leave-one-out ΔLULUCF pro Kopf: Effekt von ΔForest% ===")
    print(df_res)


def run_delta_lulucf_clustered(df_delta: pd.DataFrame) -> None:
    """
    OLS für Delta LULUCF pro Kopf mit cluster-robusten SE (Cluster = iso3).
    """
    cols = ["delta_forest_pct", "delta_agri_share_pct"]
    sub = df_delta.dropna(subset=["delta_lulucf_per_capita_t_co2eq"] + cols).copy()
    if sub.empty:
        logger.warning("Keine Daten für LULUCF-Cluster-Modell.")
        return
    print("\n=== OLS ΔLULUCF pro Kopf mit cluster-robusten SE (Cluster=iso3) ===")
    print("Beobachtungen:", len(sub))
    y = sub["delta_lulucf_per_capita_t_co2eq"]
    X = sub[cols]
    ols_with_cluster(y, X, groups=sub["iso3"])


def main() -> None:
    df_delta = load_delta_panel()
    run_delta_co2_model(df_delta)
    run_delta_co2_model_by_period(df_delta)
    run_delta_lulucf_model(df_delta)
    run_delta_lulucf_model_by_period(df_delta)
    run_delta_lulucf_leave_one_out(df_delta)
    run_delta_lulucf_clustered(df_delta)


if __name__ == "__main__":
    logger.info("Starte Regressionsanalyse (statsmodels) auf Delta-Panel...")
    main()
    logger.info("Regressionsanalyse abgeschlossen.")
