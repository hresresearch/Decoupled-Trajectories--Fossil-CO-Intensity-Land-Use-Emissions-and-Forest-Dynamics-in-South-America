"""
Generate article-ready figures for the South America forest–energy–emissions study.

Figures are saved under article/figures/ with:
- US English titles and labels,
- Times New Roman (if available) and a simple, scientific color palette.
"""

from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cepalstat_client import logger

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data_article"
FIG_DIR = BASE_DIR / "article" / "figures"

MASTER_CSV = DATA_DIR / "master_forest_energy_analysis_panel.csv"
DELTA_CSV = DATA_DIR / "south_america_delta_panel_analysis.csv"


def configure_matplotlib() -> None:
    """
    Configure matplotlib for article-style figures (Times New Roman, etc.).
    """
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 9,
            "figure.dpi": 150,
        }
    )


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load analysis-ready master and delta panels.
    """
    if not MASTER_CSV.exists():
        raise RuntimeError(f"Master analysis CSV not found: {MASTER_CSV}")
    if not DELTA_CSV.exists():
        raise RuntimeError(f"Delta analysis CSV not found: {DELTA_CSV}")
    master = pd.read_csv(MASTER_CSV)
    delta = pd.read_csv(DELTA_CSV)
    return master, delta


def fig1_trends_context(master: pd.DataFrame) -> None:
    """
    Figure 1: Regional mean trends of forest area, CO2 intensity and LULUCF emissions.
    """
    years = sorted(master["year"].unique())
    # Compute regional means
    grouped = master.groupby("year")
    forest_mean = grouped["forest_area_kha"].mean()
    co2_intensity_mean = grouped["co2_per_gdp_kg_per_usd"].mean()
    lulucf_mean = grouped["lulucf_total_kt_co2eq"].mean()

    fig, axes = plt.subplots(1, 3, figsize=(9, 3.2), sharex=True)

    axes[0].plot(years, forest_mean.loc[years] / 1000.0, marker="o", color="tab:green")
    axes[0].set_title("Forest area")
    axes[0].set_ylabel("Mean forest area (million ha)")

    axes[1].plot(years, co2_intensity_mean.loc[years], marker="o", color="tab:red")
    axes[1].set_title("CO₂ intensity of GDP")
    axes[1].set_ylabel("Mean CO₂ intensity (kg CO₂ per USD)")

    axes[2].plot(years, lulucf_mean.loc[years] / 1000.0, marker="o", color="tab:blue")
    axes[2].set_title("LULUCF emissions")
    axes[2].set_ylabel("Mean LULUCF (million t CO₂eq)")

    for ax in axes:
        ax.set_xlabel("Year")
        ax.grid(alpha=0.3)

    fig.suptitle("Regional mean trends in forest, CO₂ intensity and LULUCF (South America)")
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / "fig1_trends_forest_co2_lulucf.png"
    fig.savefig(out)
    plt.close(fig)
    logger.info("Saved %s", out)


def assign_clusters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign clusters A/B/C to countries for plotting.
    """
    cluster_map: Dict[str, str] = {}
    cluster_a = {"ARG", "BRA", "PRY", "URY"}
    cluster_b = {"BOL", "COL", "ECU", "PER", "VEN"}
    for iso in df["iso3"].unique():
        if iso in cluster_a:
            cluster_map[iso] = "A_Agro"
        elif iso in cluster_b:
            cluster_map[iso] = "B_Andean"
        else:
            cluster_map[iso] = "C_Other"
    df = df.copy()
    df["cluster"] = df["iso3"].map(cluster_map)
    return df


def fig2_delta_forest_vs_co2(delta: pd.DataFrame) -> None:
    """
    Figure 2: Scatterplot of decadal change in forest area vs. change in CO2 intensity.
    """
    df = delta.dropna(subset=["delta_forest_pct", "delta_co2_intensity_abs"]).copy()
    if df.empty:
        logger.warning("No data for ΔForest vs ΔCO₂ intensity figure.")
        return
    df = assign_clusters(df)

    colors = {"A_Agro": "tab:red", "B_Andean": "tab:blue", "C_Other": "tab:green"}

    fig, ax = plt.subplots(figsize=(6, 4))
    for cluster, group in df.groupby("cluster"):
        ax.scatter(
            group["delta_forest_pct"],
            group["delta_co2_intensity_abs"],
            label=cluster.replace("_", " "),
            color=colors.get(cluster, "gray"),
            alpha=0.8,
        )
        for _, row in group.iterrows():
            ax.text(
                row["delta_forest_pct"],
                row["delta_co2_intensity_abs"],
                f"{row['iso3']}-{int(row['year'])}",
                fontsize=8,
                ha="left",
                va="bottom",
            )

    # Regression line
    x = df["delta_forest_pct"].to_numpy(dtype=float)
    y = df["delta_co2_intensity_abs"].to_numpy(dtype=float)
    if len(x) >= 2:
        A = np.column_stack([np.ones(len(x)), x])
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = beta[0] + beta[1] * x_line
        ax.plot(x_line, y_line, color="black", linestyle="--", label="OLS fit")

    ax.set_xlabel("Decadal change in forest area (%)")
    ax.set_ylabel("Decadal change in CO₂ intensity (kg CO₂ per USD)")
    ax.set_title("Decadal changes in forest area vs. CO₂ intensity")
    ax.grid(alpha=0.3)
    ax.legend()

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / "fig2_delta_forest_vs_co2_intensity.png"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    logger.info("Saved %s", out)


def fig3_delta_forest_vs_lulucf(delta: pd.DataFrame) -> None:
    """
    Figure 3: Scatterplot of decadal change in forest area vs. change in LULUCF per capita.
    """
    df = delta.dropna(subset=["delta_forest_pct", "delta_lulucf_per_capita_t_co2eq"]).copy()
    if df.empty:
        logger.warning("No data for ΔForest vs ΔLULUCF figure.")
        return
    df = assign_clusters(df)

    colors = {"A_Agro": "tab:red", "B_Andean": "tab:blue", "C_Other": "tab:green"}

    fig, ax = plt.subplots(figsize=(6, 4))
    for cluster, group in df.groupby("cluster"):
        ax.scatter(
            group["delta_forest_pct"],
            group["delta_lulucf_per_capita_t_co2eq"],
            label=cluster.replace("_", " "),
            color=colors.get(cluster, "gray"),
            alpha=0.8,
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

    x = df["delta_forest_pct"].to_numpy(dtype=float)
    y = df["delta_lulucf_per_capita_t_co2eq"].to_numpy(dtype=float)
    if len(x) >= 2:
        A = np.column_stack([np.ones(len(x)), x])
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = beta[0] + beta[1] * x_line
        ax.plot(x_line, y_line, color="black", linestyle="--", label="OLS fit")

    ax.set_xlabel("Decadal change in forest area (%)")
    ax.set_ylabel("Decadal change in LULUCF per capita (t CO₂eq)")
    ax.set_title("Decadal changes in forest area vs. LULUCF emissions per capita")
    ax.grid(alpha=0.3)
    ax.legend()

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / "fig3_delta_forest_vs_lulucf_per_capita.png"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    logger.info("Saved %s", out)


def fig4_energy_mix_changes(master: pd.DataFrame) -> None:
    """
    Figure 4: Changes in electricity mix (hydro, coal, gas, renewables excl. hydro) by country.
    """
    # Pivot to wide format per country-year
    cols = [
        "hydro_electricity_share_pct",
        "electricity_share_coal_pct",
        "electricity_share_gas_pct",
        "electricity_share_renewables_excl_hydro_pct",
    ]
    df = master[["iso3", "year"] + cols].copy()
    # Compute change 2000->2020 for each country
    df_2000 = df[df["year"] == 2000].set_index("iso3")
    df_2020 = df[df["year"] == 2020].set_index("iso3")
    aligned = df_2020[cols].subtract(df_2000[cols], fill_value=np.nan)
    aligned = aligned.dropna(how="all")  # nur Länder mit Daten

    if aligned.empty:
        logger.warning("No data for energy mix changes figure.")
        return

    iso3_list = sorted(aligned.index)
    x = np.arange(len(iso3_list))
    width = 0.2

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.bar(x - 1.5 * width, aligned["hydro_electricity_share_pct"], width, label="Hydro", color="tab:blue")
    ax.bar(x - 0.5 * width, aligned["electricity_share_coal_pct"], width, label="Coal", color="tab:gray")
    ax.bar(x + 0.5 * width, aligned["electricity_share_gas_pct"], width, label="Gas", color="tab:orange")
    ax.bar(
        x + 1.5 * width,
        aligned["electricity_share_renewables_excl_hydro_pct"],
        width,
        label="Renewables (excl. hydro)",
        color="tab:green",
    )

    ax.set_xticks(x)
    ax.set_xticklabels(iso3_list)
    ax.set_ylabel("Change in electricity share (percentage points, 2000–2020)")
    ax.set_title("Decadal changes in electricity mix by country (2000–2020)")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / "fig4_energy_mix_changes_2000_2020.png"
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)
    logger.info("Saved %s", out)


def main() -> None:
    configure_matplotlib()
    master, delta = load_data()
    fig1_trends_context(master)
    fig2_delta_forest_vs_co2(delta)
    fig3_delta_forest_vs_lulucf(delta)
    fig4_energy_mix_changes(master)


if __name__ == "__main__":
    logger.info("Building article figures...")
    main()
    logger.info("Article figures generation completed.")
