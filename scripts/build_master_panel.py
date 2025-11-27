"""
Build the final master panel by deduplicating the latest trade/energy panel.
"""

from pathlib import Path

import pandas as pd

from cepalstat_client import logger

INPUT_CSV = Path("data_cepal/forest_co2_trade_energy_panel.csv")
OUTPUT_CSV = Path("data_cepal/master_forest_energy_panel.csv")


def build_master_panel() -> pd.DataFrame:
    df = pd.read_csv(INPUT_CSV)
    df = df.drop_duplicates(subset=["iso3", "year"], keep="first")
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    logger.info("Master panel saved to %s with %d rows.", OUTPUT_CSV, len(df))
    return df


if __name__ == "__main__":
    logger.info("Building MASTER PANEL...")
    build_master_panel()
    logger.info("Done.")
