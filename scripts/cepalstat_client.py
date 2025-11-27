"""
Simple CEPALSTAT Open Data API client.

This module provides lightweight helpers to explore the thematic tree,
inspect indicator metadata, and fetch indicator data or full data cubes.
"""

from typing import Any, Dict, Optional

import logging
import requests

BASE_URL = "https://api-cepalstat.cepal.org/cepalstat/api/v1"
DEFAULT_LANG = "en"
DEFAULT_FORMAT = "json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOUTH_AMERICA_ISO3 = [
    "ARG",
    "BOL",
    "BRA",
    "CHL",
    "COL",
    "ECU",
    "GUY",
    "PRY",
    "PER",
    "SUR",
    "URY",
    "VEN",
]


def _get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Perform a GET request against the CEPALSTAT API.

    :param path: Relative API path, e.g. "/thematic-tree".
    :param params: Optional query parameters.
    :return: Parsed JSON as dict.
    :raises RuntimeError: On HTTP errors or invalid JSON.
    """
    params = params.copy() if params else {}
    params.setdefault("lang", DEFAULT_LANG)
    params.setdefault("format", DEFAULT_FORMAT)

    url = f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    logger.info("GET %s params=%s", url, params)

    try:
        response = requests.get(url, params=params, timeout=30)
    except requests.RequestException as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"Request failed for {url} with status {response.status_code}: {response.text}"
        )

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError(f"Invalid JSON response for {url}: {exc}") from exc


def get_thematic_tree(lang: str = DEFAULT_LANG) -> Dict[str, Any]:
    """
    Fetch the full CEPALSTAT thematic tree.

    This is useful to discover available themes, subthemes and indicators.
    The response usually contains keys such as "nodes", each with potential
    "children" and "indicator_id" fields.
    """
    return _get("/thematic-tree", params={"lang": lang})


def get_indicator_dimensions(indicator_id: str, lang: str = DEFAULT_LANG) -> Dict[str, Any]:
    """
    Fetch metadata about the dimensions of a given indicator.

    This typically includes dimensions such as country, sex, time period, etc.
    The returned dict should contain the raw JSON from the API.
    """
    return _get(
        f"/indicator/{indicator_id}/dimensions",
        params={"lang": lang, "in": 1, "path": 0},
    )


def get_indicator_areas(indicator_id: str, lang: str = DEFAULT_LANG) -> Dict[str, Any]:
    """
    Fetch the areas (profiles) associated with a given indicator.

    This helps to see in which thematic "profiles" the indicator is used.
    """
    return _get(f"/indicator/{indicator_id}/areas", params={"lang": lang})


def get_indicator_records(indicator_id: str, members: str, lang: str = DEFAULT_LANG) -> Dict[str, Any]:
    """
    Fetch raw records for an indicator.

    :param indicator_id: The CEPALSTAT indicator ID (string).
    :param members: A comma-separated string with dimension member IDs.
                    This corresponds to the 'members' query parameter
                    expected by CEPALSTAT (e.g. country IDs, time IDs, etc.).
                    Build this string using the dimension metadata.
    :param lang: Language code, default 'en'.
    :return: Parsed JSON as dict. The raw data are usually under
             'indicator_records' or a similar key.
    """
    return _get(
        f"/indicator/{indicator_id}/records",
        params={"lang": lang, "members": members},
    )


def get_indicator_data_cube(indicator_id: str, members: str, lang: str = DEFAULT_LANG) -> Dict[str, Any]:
    """
    Fetch the full data cube for an indicator, including:
    - data (observations)
    - dimensions
    - metadata
    - sources
    - footnotes
    - credits

    :param indicator_id: CEPALSTAT indicator ID.
    :param members: Comma-separated members parameter (same as for records).
    :param lang: Language code, default 'en'.
    :return: Parsed JSON dict as returned by the API.
    """
    return _get(
        f"/indicator/{indicator_id}/data",
        params={"lang": lang, "members": members, "in": 1, "path": 0},
    )


def get_indicator_all_records(indicator_id: str, lang: str = DEFAULT_LANG) -> Dict[str, Any]:
    """
    Fetch all records for a given indicator without applying a 'members' filter.

    This convenience wrapper calls the /data endpoint without 'members' and
    returns the body with keys such as metadata, data, dimensions, sources,
    footnotes and credits.

    :param indicator_id: CEPALSTAT indicator ID.
    :param lang: Language code, default 'en'.
    :return: Parsed JSON body as dict.
    :raises RuntimeError: On HTTP errors or invalid responses.
    """
    payload = _get(
        f"/indicator/{indicator_id}/data",
        params={"lang": lang, "in": 1, "path": 0},
    )
    if isinstance(payload, dict) and "body" in payload:
        body = payload["body"]
        if isinstance(body, dict):
            return body
        raise RuntimeError("Unexpected body format in data cube response.")
    raise RuntimeError("Missing 'body' in data cube response.")


def filter_dimension_members_for_south_america(
    dimensions: Dict[str, Any],
    country_dim_code: str = "Country__ESTANDAR",
) -> Dict[str, str]:
    """
    Given the dimensions metadata of an indicator, extract the members
    that correspond to South American countries based on ISO3 codes.

    :param dimensions: The JSON object returned by get_indicator_dimensions().
    :param country_dim_code: The dimension code for countries (default 'Country__ESTANDAR').
    :return: A mapping {iso3_code: member_id} for South American countries.
    """
    dim_list: Any = []
    if isinstance(dimensions, list):
        dim_list = dimensions
    elif isinstance(dimensions, dict) and isinstance(dimensions.get("dimensions"), list):
        dim_list = dimensions["dimensions"]

    if not dim_list:
        logger.warning("No dimensions found in payload while looking for %s", country_dim_code)
        return {}

    country_dim: Optional[Dict[str, Any]] = None
    for dim in dim_list:
        code = (
            dim.get("code")
            or dim.get("dimension_code")
            or dim.get("dimensionCode")
            or dim.get("id")
        )
        if code == country_dim_code:
            country_dim = dim
            break

    if not country_dim:
        logger.warning("Country dimension %s not found", country_dim_code)
        return {}

    members = country_dim.get("members") or country_dim.get("Members") or []
    if not isinstance(members, list):
        logger.warning("Unexpected members format in country dimension: %s", type(members))
        return {}

    mapping: Dict[str, str] = {}
    for member in members:
        iso_candidate: Optional[str] = None
        for key in ("iso3", "iso_3", "iso", "iso_code", "iso_code3", "code3", "code"):
            value = member.get(key)
            if isinstance(value, str) and len(value.strip()) == 3:
                iso_candidate = value.strip().upper()
                break
        if not iso_candidate:
            continue

        member_id = (
            member.get("id")
            or member.get("member_id")
            or member.get("memberId")
            or member.get("value")
            or member.get("code")
        )

        if iso_candidate in SOUTH_AMERICA_ISO3 and member_id is not None:
            mapping[iso_candidate] = str(member_id)

    if not mapping:
        logger.warning("No South American members found in dimension %s", country_dim_code)
    return mapping


if __name__ == "__main__":
    from pprint import pprint

    print("Fetching thematic tree...")
    thematic_tree = get_thematic_tree()

    top_level_nodes = []
    if isinstance(thematic_tree, dict):
        if isinstance(thematic_tree.get("nodes"), list):
            top_level_nodes = thematic_tree["nodes"]
        elif isinstance(thematic_tree.get("data"), list):
            top_level_nodes = thematic_tree["data"]
        elif isinstance(thematic_tree.get("data"), dict) and isinstance(
            thematic_tree["data"].get("nodes"), list
        ):
            top_level_nodes = thematic_tree["data"]["nodes"]
        elif isinstance(thematic_tree.get("children"), list):
            top_level_nodes = thematic_tree["children"]

    print("Top-level themes (name / id):")
    for node in top_level_nodes[:10]:  # limit output
        name = (
            node.get("label")
            or node.get("name")
            or node.get("title")
            or node.get("node_name")
            or "Unknown"
        )
        node_id = node.get("id") or node.get("node_id") or node.get("indicator_id") or "n/a"
        print(f"- {name} ({node_id})")
    if not top_level_nodes:
        print("No themes found. Inspect thematic_tree structure to locate nodes.")

    # TODO: Replace this with a real indicator ID from the thematic tree
    example_indicator_id = "210002"
    print(f"\nFetching dimensions for indicator {example_indicator_id}...")
    dims_payload = get_indicator_dimensions(example_indicator_id)

    dims_list: Any = []
    if isinstance(dims_payload.get("dimensions"), list):  # type: ignore[union-attr]
        dims_list = dims_payload["dimensions"]  # type: ignore[index]
    elif isinstance(dims_payload, list):
        dims_list = dims_payload

    print("Available dimensions (code: name):")
    for dim in dims_list:
        code = dim.get("code") or dim.get("dimension_code") or dim.get("id")
        name = dim.get("name") or dim.get("label") or dim.get("title")
        print(f"- {code}: {name}")

    country_dim_code = "Country__ESTANDAR"
    country_members = []
    for dim in dims_list:
        code = dim.get("code") or dim.get("dimension_code") or dim.get("id")
        if code == country_dim_code:
            raw_members = dim.get("members") or []
            if isinstance(raw_members, list):
                country_members = raw_members[:5]
            break

    if country_members:
        print("\nSample country members:")
        for member in country_members:
            print(
                f"- {member.get('name') or member.get('label')} "
                f"(id={member.get('id')}, code={member.get('code')})"
            )
    elif dims_list:
        print("\nNo country members preview available; adjust country_dim_code if needed.")

    # Build a simple example members string.
    # The exact structure depends on the indicator; adjust as needed.
    example_members = ""
    if dims_list:
        south_american_members = filter_dimension_members_for_south_america(
            dims_payload, country_dim_code=country_dim_code
        )
        selected_country_ids = list(south_american_members.values())[:2]

        time_member_ids = []
        for dim in dims_list:
            code = dim.get("code") or dim.get("dimension_code") or dim.get("id")
            name = dim.get("name") or dim.get("label")
            looks_like_time = False
            if code and "TIME" in str(code).upper():
                looks_like_time = True
            elif name and "time" in str(name).lower():
                looks_like_time = True
            if looks_like_time:
                raw_members = dim.get("members") or []
                if isinstance(raw_members, list):
                    time_member_ids = [
                        str(m.get("id")) for m in raw_members[:5] if m.get("id") is not None
                    ]
                break

        example_members = ",".join(selected_country_ids + time_member_ids[:3])

    if example_members:
        print(f"\nExample members string (adjust for your indicator): {example_members}")
    else:
        print(
            "\nExample members string not built (missing dimensions or country/time members). "
            "Inspect dimensions and build members manually."
        )

    if example_members:
        print("\nFetching indicator records (first 3 shown)...")
        try:
            records_payload = get_indicator_records(example_indicator_id, members=example_members)
            indicator_records = records_payload.get("indicator_records") or records_payload.get("data") or []
            print(f"Records returned: {len(indicator_records)}")
            pprint(indicator_records[:3])
        except RuntimeError as exc:
            print(f"Could not fetch records: {exc}")

        print("\nFetching indicator data cube...")
        try:
            cube_payload = get_indicator_data_cube(example_indicator_id, members=example_members)
            indicator_cube = cube_payload.get("indicator_cube") or cube_payload
            data_points = indicator_cube.get("data") or indicator_cube.get("records") or []
            metadata = indicator_cube.get("metadata") or {}
            title = metadata.get("title") or metadata.get("name") or metadata.get("indicator_title")
            last_update = metadata.get("last_update") or metadata.get("lastUpdate") or metadata.get("updated")
            print(f"Data points: {len(data_points)}")
            print(f"Indicator title: {title}")
            print(f"Last update: {last_update}")
        except RuntimeError as exc:
            print(f"Could not fetch data cube: {exc}")
    else:
        print("Skipping record and cube fetch because members string is empty.")
