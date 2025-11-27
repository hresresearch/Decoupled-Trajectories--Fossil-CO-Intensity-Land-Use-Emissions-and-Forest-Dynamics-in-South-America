"""
Delta-basierte Analyse für das Südamerika-Panel.

Schritte:
- lädt das Master-Panel (mit Controls, falls vorhanden),
- berechnet Dekaden-Änderungen (2000→2010, 2010→2020) für zentrale Variablen,
- erstellt Delta-Features (u.a. delta_forest_pct, delta_co2_intensity_abs),
- berechnet Korrelationen und eine OLS-Regression auf den Deltas,
- erzeugt einen Scatterplot mit Regressionslinie,
- exportiert das Delta-Panel nach data_cepal/south_america_delta_panel_processed.csv
  inklusive Platzhalter-Spalte für methane_total_kt_co2eq.
"""

from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cepalstat_client import logger

PANEL_WITH_CONTROLS = Path("data_cepal/master_forest_energy_controls_panel.csv")
PANEL_BASE = Path("data_cepal/master_forest_energy_panel.csv")
DELTA_CSV = Path("data_cepal/south_america_delta_panel_processed.csv")
DELTA_PLOT = Path("data_cepal/delta_forest_vs_co2_intensity.png")

ANALYSIS_YEARS: List[int] = [2000, 2010, 2020]


def load_panel() -> pd.DataFrame:
    """
    Lade das Master-Panel, bevorzugt die Variante mit Controls.
    """
    if PANEL_WITH_CONTROLS.exists():
        path = PANEL_WITH_CONTROLS
    elif PANEL_BASE.exists():
        path = PANEL_BASE
    else:
        raise RuntimeError("Kein Master-Panel gefunden.")
    logger.info("Lade Panel aus %s", path)
    df = pd.read_csv(path)
    # Sortierung und Basis-Bereinigung
    df = df.sort_values(["iso3", "year"]).reset_index(drop=True)
    return df


def ensure_numeric(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Erzwinge numerische Typen für die angegebenen Spalten.
    """
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def add_deltas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Berechne Dekaden-Änderungen je Land für die Kernvariablen.
    """
    vars_to_delta = [
        "forest_area_kha",
        "co2_per_gdp_kg_per_usd",
        "hydro_electricity_share_pct",
        "gdp_per_capita_ppp_const2017",
        "agriculture_value_added_share_gdp_pct",
        "lulucf_total_kt_co2eq",
        "population_total",
    ]
    df = ensure_numeric(df, vars_to_delta)

    # Gruppiert nach Land, sortiert nach Jahr und dann Differenzen berechnen
    df = df.sort_values(["iso3", "year"]).copy()
    grouped = df.groupby("iso3", group_keys=False)

    df["delta_forest_kha"] = grouped["forest_area_kha"].diff()
    df["delta_co2_intensity_abs"] = grouped["co2_per_gdp_kg_per_usd"].diff()
    df["delta_hydro_share_pct"] = grouped["hydro_electricity_share_pct"].diff()
    df["delta_gdp_per_capita"] = grouped["gdp_per_capita_ppp_const2017"].diff()
    df["delta_agri_share_pct"] = grouped["agriculture_value_added_share_gdp_pct"].diff()

    # Prozentuale Waldänderung
    prev_forest = grouped["forest_area_kha"].shift(1)
    df["delta_forest_pct"] = (df["delta_forest_kha"] / prev_forest) * 100.0

    # LULUCF pro Kopf und dessen Delta
    df["lulucf_per_capita_t_co2eq"] = (df["lulucf_total_kt_co2eq"] * 1000.0) / df["population_total"]
    df["delta_lulucf_per_capita_t_co2eq"] = grouped["lulucf_per_capita_t_co2eq"].diff()

    # Platzhalter für Methan
    df["methane_total_kt_co2eq"] = np.nan

    return df


def build_delta_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtere auf Jahre mit definierten Deltas (2010 und 2020) und exportiere.
    """
    df_delta = df[df["year"].isin(ANALYSIS_YEARS[1:])].copy()
    # explizite Periodenkennzeichnung
    df_delta["period_start"] = df_delta["year"] - 10
    df_delta["period_end"] = df_delta["year"]
    df_delta.to_csv(DELTA_CSV, index=False)
    logger.info("Delta-Panel gespeichert nach %s mit %d Zeilen.", DELTA_CSV, len(df_delta))
    return df_delta


def correlation_on_deltas(df_delta: pd.DataFrame) -> None:
    """
    Korrelationsmatrix (Pearson) nur für Delta-Variablen (CO2-Intensität).
    """
    cols = [
        "delta_forest_pct",
        "delta_co2_intensity_abs",
        "delta_hydro_share_pct",
        "delta_gdp_per_capita",
        "delta_agri_share_pct",
    ]
    sub = df_delta[cols].dropna()
    corr = sub.corr()
    print("\n=== Korrelationsmatrix (Deltas, alle Zeiträume zusammen) ===")
    print(corr)


def correlation_lulucf_on_deltas(df_delta: pd.DataFrame) -> None:
    """
    Korrelationsmatrix für Delta LULUCF pro Kopf vs. Wald- und Agrar-Änderungen.
    """
    cols = [
        "delta_lulucf_per_capita_t_co2eq",
        "delta_forest_pct",
        "delta_agri_share_pct",
    ]
    sub = df_delta[cols].dropna()
    if sub.empty:
        logger.warning("Keine Daten für LULUCF-Korrelationsanalyse.")
        return
    corr = sub.corr()
    print("\n=== Korrelationsmatrix (Deltas LULUCF pro Kopf) ===")
    print(corr)


def run_delta_ols(df_delta: pd.DataFrame) -> None:
    """
    OLS: Delta_CO2_Intensity ~ Delta_Forest_PCT + Delta_Hydro_Share + Delta_GDP_Per_Capita
    """
    cols = [
        "delta_forest_pct",
        "delta_hydro_share_pct",
        "delta_gdp_per_capita",
    ]
    sub = df_delta.dropna(subset=["delta_co2_intensity_abs"] + cols).copy()
    if sub.empty:
        logger.warning("Keine Daten für Delta-OLS.")
        return

    y = sub["delta_co2_intensity_abs"].to_numpy(dtype=float)
    X = sub[cols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])

    beta, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
    y_hat = X @ beta
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan

    print("\n=== OLS auf Deltas: delta_co2_intensity_abs ~ delta_forest_pct + delta_hydro_share_pct + delta_gdp_per_capita ===")
    print("Anzahl Beobachtungen:", len(sub))
    print("R^2:", r2)
    print("Intercept:", beta[0])
    for name, coef in zip(cols, beta[1:]):
        print(f"{name}: {coef}")


def run_lulucf_delta_ols(df_delta: pd.DataFrame) -> None:
    """
    OLS: Delta LULUCF per Capita ~ Delta Forest (%) + Delta Agri Share (%).
    """
    y_col = "delta_lulucf_per_capita_t_co2eq"
    x_cols = ["delta_forest_pct", "delta_agri_share_pct"]
    sub = df_delta.dropna(subset=[y_col] + x_cols).copy()
    if sub.empty:
        logger.warning("Keine Daten für LULUCF-Delta-OLS.")
        return
    y = sub[y_col].to_numpy(dtype=float)
    X = sub[x_cols].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])
    beta, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)
    y_hat = X @ beta
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan

    print("\n=== OLS auf Deltas: delta_lulucf_per_capita_t_co2eq ~ delta_forest_pct + delta_agri_share_pct ===")
    print("Anzahl Beobachtungen:", len(sub))
    print("R^2:", r2)
    print("Intercept:", beta[0])
    for name, coef in zip(x_cols, beta[1:]):
        print(f"{name}: {coef}")


def scatter_with_regression(df_delta: pd.DataFrame) -> None:
    """
    Scatterplot Delta Forest (%) vs. Delta CO2-Intensität mit Regressionslinie und Clustern.
    """
    sub = df_delta.dropna(subset=["delta_forest_pct", "delta_co2_intensity_abs"]).copy()
    if sub.empty:
        logger.warning("Keine Daten für Scatterplot der Deltas.")
        return

    # Cluster-Zuordnung
    cluster_map: Dict[str, str] = {}
    cluster_a = {"ARG", "BRA", "PRY", "URY"}
    cluster_b = {"BOL", "COL", "ECU", "PER", "VEN"}
    # Rest = Cluster C
    for iso in sub["iso3"].unique():
        if iso in cluster_a:
            cluster_map[iso] = "A_Agro"
        elif iso in cluster_b:
            cluster_map[iso] = "B_Andean"
        else:
            cluster_map[iso] = "C_Other"
    sub["cluster"] = sub["iso3"].map(cluster_map)

    colors = {"A_Agro": "tab:red", "B_Andean": "tab:blue", "C_Other": "tab:green"}

    fig, ax = plt.subplots(figsize=(7, 5))
    for cluster, group in sub.groupby("cluster"):
        ax.scatter(
            group["delta_forest_pct"],
            group["delta_co2_intensity_abs"],
            label=cluster,
            color=colors.get(cluster, "gray"),
        )
        # Punkte beschriften (Ländercodes + Jahr)
        for _, row in group.iterrows():
            ax.text(
                row["delta_forest_pct"],
                row["delta_co2_intensity_abs"],
                f"{row['iso3']}-{int(row['year'])}",
                fontsize=8,
                ha="left",
                va="bottom",
            )

    # Regressionslinie über alle Punkte
    x = sub["delta_forest_pct"].to_numpy(dtype=float)
    y = sub["delta_co2_intensity_abs"].to_numpy(dtype=float)
    if len(x) >= 2:
        A = np.column_stack([np.ones(len(x)), x])
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = beta[0] + beta[1] * x_line
        ax.plot(x_line, y_line, color="black", linestyle="--", label="OLS-Fit")

    ax.set_xlabel("Δ Waldfläche (%)")
    ax.set_ylabel("Δ CO₂-Intensität (kg CO₂ pro USD)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    DELTA_PLOT.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(DELTA_PLOT, dpi=150)
    plt.close(fig)
    logger.info("Scatterplot gespeichert unter %s", DELTA_PLOT)


def scatter_lulucf_vs_forest(df_delta: pd.DataFrame) -> None:
    """
    Scatterplot Delta Forest (%) vs. Delta LULUCF per Capita mit Regressionslinie und Clustern.
    """
    sub = df_delta.dropna(subset=["delta_forest_pct", "delta_lulucf_per_capita_t_co2eq"]).copy()
    if sub.empty:
        logger.warning("Keine Daten für Scatterplot LULUCF vs. Wald.")
        return

    # Cluster wie zuvor
    cluster_map: Dict[str, str] = {}
    cluster_a = {"ARG", "BRA", "PRY", "URY"}
    cluster_b = {"BOL", "COL", "ECU", "PER", "VEN"}
    for iso in sub["iso3"].unique():
        if iso in cluster_a:
            cluster_map[iso] = "A_Agro"
        elif iso in cluster_b:
            cluster_map[iso] = "B_Andean"
        else:
            cluster_map[iso] = "C_Other"
    sub["cluster"] = sub["iso3"].map(cluster_map)

    colors = {"A_Agro": "tab:red", "B_Andean": "tab:blue", "C_Other": "tab:green"}

    fig, ax = plt.subplots(figsize=(7, 5))
    for cluster, group in sub.groupby("cluster"):
        ax.scatter(
            group["delta_forest_pct"],
            group["delta_lulucf_per_capita_t_co2eq"],
            label=cluster,
            color=colors.get(cluster, "gray"),
        )
        for _, row in group.iterrows():
            ax.text(
                row["delta_forest_pct"],
                row["delta_lulucf_per_capita_t_co2eq"],
                f"{row['iso3']}-{int(row['year'])}",
                fontsize=8,
                ha="left",
                va="bottom",
            )

    x = sub["delta_forest_pct"].to_numpy(dtype=float)
    y = sub["delta_lulucf_per_capita_t_co2eq"].to_numpy(dtype=float)
    if len(x) >= 2:
        A = np.column_stack([np.ones(len(x)), x])
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = beta[0] + beta[1] * x_line
        ax.plot(x_line, y_line, color="black", linestyle="--", label="OLS-Fit")

    ax.set_xlabel("Δ Waldfläche (%)")
    ax.set_ylabel("Δ LULUCF pro Kopf (t CO₂eq)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    out_path = DELTA_PLOT.parent / "delta_forest_vs_lulucf_per_capita.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    logger.info("Scatterplot LULUCF gespeichert unter %s", out_path)


def main() -> None:
    df = load_panel()
    df = add_deltas(df)
    df_delta = build_delta_dataset(df)
    correlation_on_deltas(df_delta)
    run_delta_ols(df_delta)
    scatter_with_regression(df_delta)
    correlation_lulucf_on_deltas(df_delta)
    run_lulucf_delta_ols(df_delta)
    scatter_lulucf_vs_forest(df_delta)


if __name__ == "__main__":
    logger.info("Starte Delta-Analyse...")
    main()
    logger.info("Delta-Analyse abgeschlossen.")
