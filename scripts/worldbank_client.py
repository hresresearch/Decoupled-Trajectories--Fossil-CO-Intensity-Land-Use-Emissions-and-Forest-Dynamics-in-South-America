"""
Lightweight World Bank API client helpers.
"""

import logging
import time
from typing import Any, Dict, List

import requests
import pandas as pd

logger = logging.getLogger(__name__)

WORLD_BANK_BASE_URL = "https://api.worldbank.org/v2"


def fetch_indicator_raw(
    iso3: str,
    indicator_code: str,
    per_page: int = 2000,
    retries: int = 3,
    timeout: int = 60,
) -> List[Dict[str, Any]]:
    """
    Fetch raw World Bank API data for a single country and indicator.

    Returns the raw data list (second element of the JSON response).
    Raises RuntimeError on HTTP or response errors.
    """
    url = f"{WORLD_BANK_BASE_URL}/country/{iso3}/indicator/{indicator_code}"
    params = {"format": "json", "per_page": per_page}
    attempt = 0
    while True:
        attempt += 1
        logger.info("GET %s params=%s (attempt %d)", url, params, attempt)
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            if resp.status_code == 200:
                break
            if attempt >= retries:
                raise RuntimeError(
                    f"World Bank API request failed for {iso3}/{indicator_code} "
                    f"with status {resp.status_code}: {resp.text}"
                )
        except requests.RequestException as exc:
            if attempt >= retries:
                raise RuntimeError(
                    f"Request to World Bank API failed for {iso3}/{indicator_code}: {exc}"
                ) from exc
        time.sleep(1)

    try:
        payload = resp.json()
    except ValueError as exc:
        raise RuntimeError(f"Invalid JSON from World Bank for {iso3}/{indicator_code}: {exc}") from exc

    if not isinstance(payload, list) or len(payload) < 2:
        raise RuntimeError(f"Unexpected World Bank response format for {iso3}/{indicator_code}: {payload}")

    data = payload[1]
    if data is None:
        return []
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected data section in World Bank response for {iso3}/{indicator_code}: {data}")
    return data


def fetch_indicator_panel(iso3_list: List[str], indicator_code: str, years: List[int]) -> pd.DataFrame:
    """
    Fetch a World Bank indicator for multiple countries and years and return a tidy DataFrame.

    Columns: iso3, year, value (float). Only keeps rows matching iso3_list, years, and non-null value.
    """
    records: List[Dict[str, Any]] = []
    target_years = set(years)
    target_iso3 = set(iso3_list)

    for iso3 in iso3_list:
        data = fetch_indicator_raw(iso3, indicator_code)
        for obs in data:
            iso_code = obs.get("countryiso3code")
            date_str = obs.get("date")
            value = obs.get("value")
            if iso_code not in target_iso3:
                continue
            try:
                year = int(date_str)
            except (TypeError, ValueError):
                continue
            if year not in target_years or value is None:
                continue
            records.append({"iso3": iso_code, "year": year, "value": float(value)})

    df = pd.DataFrame(records)
    return df
