"""
Lightweight FAOSTAT API helper to fetch panels for selected items/elements.
"""

import logging
from typing import Any, Dict, List

import pandas as pd
import requests

logger = logging.getLogger(__name__)

FAOSTAT_BASE_URL = "https://fenixservices.fao.org/faostat/api/v1/en"


def fetch_faostat_indicator_panel(
    domain: str,
    item_codes: List[str],
    element_code: str,
    iso3_list: List[str],
    years: List[int],
) -> pd.DataFrame:
    """
    Fetch FAOSTAT data for a domain, multiple items, and a single element.

    Returns a tidy DataFrame with columns: iso3, year, item_code, value
    filtered to the requested iso3_list and years.
    """
    url = f"{FAOSTAT_BASE_URL}/{domain}"
    params = {
        "item_code": ",".join(item_codes),
        "element_code": element_code,
        "year": ",".join(str(y) for y in years),
        "format": "json",
    }
    logger.info("GET %s params=%s", url, params)
    try:
        resp = requests.get(url, params=params, timeout=60)
    except requests.RequestException as exc:
        raise RuntimeError(f"FAOSTAT request failed for {domain}/{item_codes}: {exc}") from exc

    if resp.status_code != 200:
        raise RuntimeError(
            f"FAOSTAT request failed with status {resp.status_code}: {resp.text}"
        )

    try:
        payload = resp.json()
    except ValueError as exc:
        raise RuntimeError(f"Invalid JSON from FAOSTAT: {exc}") from exc

    data = payload.get("data") or payload.get("Data")
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected FAOSTAT response structure: {payload}")

    target_iso3 = set(iso3_list)
    target_years = set(years)
    rows: List[Dict[str, Any]] = []
    for row in data:
        iso3 = (
            row.get("area_code_iso3")
            or row.get("area_code_3")
            or row.get("area_iso3")
            or row.get("iso3")
        )
        year = row.get("year")
        item_code = row.get("item_code") or row.get("item")
        value = row.get("value")

        try:
            year_int = int(year)
        except (TypeError, ValueError):
            continue

        if iso3 not in target_iso3 or year_int not in target_years or value is None:
            continue

        rows.append(
            {
                "iso3": iso3,
                "year": year_int,
                "item_code": str(item_code) if item_code is not None else None,
                "value": float(value),
            }
        )

    df = pd.DataFrame(rows)
    return df


def read_faostat_zip_to_df(zip_path: str, csv_name: str) -> pd.DataFrame:
    """
    Read a FAOSTAT normalized CSV from a local zip file.
    """
    import zipfile
    import io

    with zipfile.ZipFile(zip_path, "r") as zf:
        with zf.open(csv_name) as f:
            return pd.read_csv(io.TextIOWrapper(f, encoding="utf-8"), low_memory=False)
