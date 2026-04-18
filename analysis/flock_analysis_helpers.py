from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
ANALYSIS_CSV_DIR = DATA_DIR / "analysis-csv"
RAW_SCRAPE_PATH = DATA_DIR / "flock-data.csv"

NUMERIC_FIELDS = {
    "Data retention (in days)": "retention_days",
    "Number of LPR and other cameras": "camera_count",
    "Vehicles detected in the last 30 days": "vehicles_30d",
    "Unique vehicles detected in the last 30 days": "unique_vehicles_30d",
    "Hotlist hits in the last 30 days": "hotlist_hits_30d",
    "Searches in the last 30 days": "searches_30d",
}

US_STATE_ABBREVIATIONS = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
}

STATE_NAME_TO_ABBR = {
    "alabama": "AL",
    "alaska": "AK",
    "arizona": "AZ",
    "arkansas": "AR",
    "california": "CA",
    "colorado": "CO",
    "connecticut": "CT",
    "delaware": "DE",
    "florida": "FL",
    "georgia": "GA",
    "hawaii": "HI",
    "idaho": "ID",
    "illinois": "IL",
    "indiana": "IN",
    "iowa": "IA",
    "kansas": "KS",
    "kentucky": "KY",
    "louisiana": "LA",
    "maine": "ME",
    "maryland": "MD",
    "massachusetts": "MA",
    "michigan": "MI",
    "minnesota": "MN",
    "mississippi": "MS",
    "missouri": "MO",
    "montana": "MT",
    "nebraska": "NE",
    "nevada": "NV",
    "new hampshire": "NH",
    "new jersey": "NJ",
    "new mexico": "NM",
    "new york": "NY",
    "north carolina": "NC",
    "north dakota": "ND",
    "ohio": "OH",
    "oklahoma": "OK",
    "oregon": "OR",
    "pennsylvania": "PA",
    "rhode island": "RI",
    "south carolina": "SC",
    "south dakota": "SD",
    "tennessee": "TN",
    "texas": "TX",
    "utah": "UT",
    "vermont": "VT",
    "virginia": "VA",
    "washington": "WA",
    "west virginia": "WV",
    "wisconsin": "WI",
    "wyoming": "WY",
    "district of columbia": "DC",
}

NON_STATE_TOKENS = {
    "pd",
    "so",
    "sd",
    "da",
    "dps",
    "dept",
    "department",
    "office",
    "campus",
    "public",
    "safety",
    "county",
    "city",
    "town",
    "of",
    "de",
    "la",
    "st",
    "mt",
}


def _strip_frame(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=lambda value: str(value).strip())
    for column in df.select_dtypes(include="object"):
        df[column] = df[column].map(lambda value: value.strip() if isinstance(value, str) else value)
    return df


def normalize_label(label: str) -> str:
    label = str(label).strip()
    lowered = label.lower()

    if lowered.startswith("organizations granted access"):
        return "Organizations granted access"

    if lowered.startswith("organizations sharing their data"):
        return "Organizations sharing data"

    return label


def normalize_list_item(item: str) -> str:
    item = str(item).strip().strip('"').strip("'").lower()
    item = item.rstrip(".")
    item = re.sub(r"\s+", " ", item)
    item = item.replace("harrassment", "harassment")

    if item in {"license plate", "license plates", "rear license plates"}:
        return "license plates"

    if item in {"vehicle", "vehicles", "rear of vehicle", "rear of vehicles", "image of the rear of vehicles"}:
        return "vehicles"

    if item in {"facial recognition", "face recognition"}:
        return "facial recognition"

    if item in {"person", "people"}:
        return "people"

    if item in {"traffic enforcement", "routine traffic enforcement or parking monitoring"}:
        return "traffic enforcement"

    if item in {"personal use", "or personal use", "personal use by staff"}:
        return "personal use"

    if item.startswith("usage based solely on a protected class"):
        return "usage based solely on a protected class"

    if item.startswith("harassment, intimidation, or profiling based on protected traits"):
        return "usage based solely on a protected class"

    if item in {"harassment", "harassment or intimidation"}:
        return "harassment or intimidation"

    if item.startswith("immigration enforcement and civil immigration matters"):
        return "immigration enforcement"

    return item


def split_structured_items(text: str | float | None) -> list[str]:
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return []

    parts = re.split(r",\s*(?![^()]*\))", str(text).strip())
    return [normalize_list_item(part) for part in parts if part.strip()]


def split_raw_items(text: str | float | None) -> list[str]:
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return []

    parts = re.split(r",\s*(?![^()]*\))", str(text).strip())
    return [part.strip() for part in parts if part.strip()]


def parse_number(value: str | float | int | None) -> float:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan

    text = str(value).strip().lower()
    if not text or text in {"nan", "data unavailable", "none"}:
        return np.nan

    text = text.replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else np.nan


def extract_state_from_slug(slug: str) -> str | None:
    parts = [part for part in str(slug).split("-") if part]
    for part in reversed(parts):
        lowered = part.lower()
        if lowered in NON_STATE_TOKENS:
            continue
        if len(lowered) == 2 and lowered.isalpha():
            return lowered.upper()
    return None


def is_federal_org(org_name: str) -> bool:
    text = str(org_name).strip().lower()
    federal_patterns = [
        r"^\[federal\]",
        r"\bu\.?s\.?\b",
        r"\busms\b",
        r"postal inspection service",
        r"national park service",
        r"veterans affairs",
        r"air force base",
        r"border patrol",
        r"department of homeland security",
        r"\bfbi\b",
        r"\bdea\b",
        r"\batf\b",
    ]
    return any(re.search(pattern, text) for pattern in federal_patterns)


def extract_state_from_org_name(org_name: str) -> str | None:
    text = str(org_name).strip()

    if is_federal_org(text):
        return None

    uppercase_tokens = re.findall(r"\b[A-Z]{2}\b", text)
    for token in reversed(uppercase_tokens):
        if token in US_STATE_ABBREVIATIONS:
            return token

    lowered = text.lower()
    for state_name, abbreviation in STATE_NAME_TO_ABBR.items():
        if re.search(rf"\b{re.escape(state_name)}\b", lowered):
            return abbreviation

    return None


def classify_partner_jurisdiction(org_name: str, home_state: str | None) -> str:
    if is_federal_org(org_name):
        return "federal"

    partner_state = extract_state_from_org_name(org_name)
    if partner_state is None or home_state is None:
        return "unknown"

    return "in_state" if partner_state == home_state else "out_of_state"


def load_summary_tables() -> dict[str, pd.DataFrame]:
    field_counts = _strip_frame(pd.read_csv(ANALYSIS_CSV_DIR / "field-counts.csv"))
    field_counts["count"] = pd.to_numeric(field_counts["count"], errors="coerce")

    list_counts = load_list_counts()
    list_counts["topic"] = list_counts["topic"].str.lower()
    list_counts["count"] = pd.to_numeric(list_counts["count"], errors="coerce")
    list_counts["rate"] = pd.to_numeric(list_counts["rate"], errors="coerce")

    numeric = _strip_frame(pd.read_csv(ANALYSIS_CSV_DIR / "numeric.csv"))
    numeric["num"] = pd.to_numeric(numeric["num"], errors="coerce")

    orgs = load_orgs_lines()
    orgs_merged = pd.read_csv(ANALYSIS_CSV_DIR / "orgs_merged.csv", index_col=0, low_memory=False)
    orgs_merged = orgs_merged.rename_axis(index="field").rename(columns=lambda value: str(value).strip())

    return {
        "field_counts": field_counts,
        "list_counts": list_counts,
        "numeric": numeric,
        "orgs": orgs,
        "orgs_merged": orgs_merged,
    }


def load_list_counts() -> pd.DataFrame:
    rows = []
    path = ANALYSIS_CSV_DIR / "list-counts.csv"

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        if line_number == 0 or not line.strip():
            continue
        topic, remainder = line.split(",", 1)
        item, count, rate = remainder.rsplit(",", 2)
        rows.append(
            {
                "topic": topic.strip(),
                "item": item.strip(),
                "count": count.strip(),
                "rate": rate.strip(),
            }
        )

    return pd.DataFrame(rows)


def load_orgs_lines() -> pd.DataFrame:
    rows = []
    path = ANALYSIS_CSV_DIR / "orgs.csv"

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        owner, shared = (line.split(",", 1) + [""])[:2]
        rows.append(
            {
                "portal_owner": owner.strip(),
                "shared_with_raw": shared.strip().strip('"'),
            }
        )

    return pd.DataFrame(rows)


def load_raw_portal_matrix() -> pd.DataFrame:
    raw = pd.read_csv(RAW_SCRAPE_PATH, index_col=0, low_memory=False)
    raw = raw[~raw.index.isna()]
    raw.index = [normalize_label(label) for label in raw.index]
    raw = raw.drop(index=["url", "error"], errors="ignore")
    raw = raw.replace("", np.nan)
    return raw.groupby(raw.index).first()


def load_portal_table() -> pd.DataFrame:
    portals = load_raw_portal_matrix().T
    portals.index.name = "portal_slug"
    return portals


def count_structured_field(
    portals: pd.DataFrame,
    field: str,
    dedupe_within_portal: bool = False,
    raw_items: bool = False,
) -> pd.DataFrame:
    if field not in portals.columns:
        return pd.DataFrame(columns=["item", "count", "rate"])

    values = portals[field].dropna()
    counter: Counter[str] = Counter()

    for value in values:
        items = split_raw_items(value) if raw_items else split_structured_items(value)
        if dedupe_within_portal:
            items = list(dict.fromkeys(items))
        counter.update(items)

    rows = [
        {
            "item": item,
            "count": count,
            "rate": count / len(values),
        }
        for item, count in counter.most_common()
    ]
    return pd.DataFrame(rows)


def summarize_granted_access_geography(portals: pd.DataFrame | None = None) -> pd.DataFrame:
    portals = portals if portals is not None else load_portal_table()

    rows = []
    if "Organizations granted access" not in portals.columns:
        return pd.DataFrame()

    values = portals["Organizations granted access"].dropna()

    for slug, raw_value in values.items():
        home_state = extract_state_from_slug(slug)
        partners = split_raw_items(raw_value)
        jurisdiction_counts = Counter(classify_partner_jurisdiction(partner, home_state) for partner in partners)

        has_federal = jurisdiction_counts["federal"] > 0
        has_out_of_state = jurisdiction_counts["out_of_state"] > 0

        if has_federal and has_out_of_state:
            category = "Includes federal and out-of-state"
        elif has_federal:
            category = "Includes federal only"
        elif has_out_of_state:
            category = "Includes out-of-state only"
        else:
            category = "In-state only"

        rows.append(
            {
                "portal_slug": slug,
                "home_state": home_state,
                "partner_count": len(partners),
                "in_state_count": jurisdiction_counts["in_state"],
                "out_of_state_count": jurisdiction_counts["out_of_state"],
                "federal_count": jurisdiction_counts["federal"],
                "unknown_count": jurisdiction_counts["unknown"],
                "geography_category": category,
            }
        )

    return pd.DataFrame(rows)


def build_portal_metrics(portals: pd.DataFrame | None = None) -> pd.DataFrame:
    portals = portals if portals is not None else load_portal_table()

    metrics = pd.DataFrame(index=portals.index)
    metrics["state"] = metrics.index.map(extract_state_from_slug)
    metrics["filled_fields"] = portals.notna().sum(axis=1)

    for source_field, target_field in NUMERIC_FIELDS.items():
        if source_field in portals.columns:
            metrics[target_field] = portals[source_field].map(parse_number)

    if "Organizations granted access" in portals.columns:
        metrics["granted_access_partners"] = portals["Organizations granted access"].map(
            lambda value: len(split_structured_items(value)) if pd.notna(value) else np.nan
        )

    if "Organizations sharing data" in portals.columns:
        metrics["sharing_data_partners"] = portals["Organizations sharing data"].map(
            lambda value: len(split_structured_items(value)) if pd.notna(value) else np.nan
        )

    if {"vehicles_30d", "camera_count"}.issubset(metrics.columns):
        metrics["vehicles_per_camera"] = metrics["vehicles_30d"] / metrics["camera_count"]

    if {"searches_30d", "vehicles_30d"}.issubset(metrics.columns):
        metrics["searches_per_10k_vehicles"] = metrics["searches_30d"] / metrics["vehicles_30d"] * 10_000

    if {"hotlist_hits_30d", "vehicles_30d"}.issubset(metrics.columns):
        metrics["hits_per_10k_vehicles"] = metrics["hotlist_hits_30d"] / metrics["vehicles_30d"] * 10_000

    return metrics.replace([np.inf, -np.inf], np.nan)


def compute_story_metrics(portals: pd.DataFrame | None = None) -> dict[str, pd.DataFrame | pd.Series]:
    portals = portals if portals is not None else load_portal_table()
    portal_metrics = build_portal_metrics(portals)
    geography = summarize_granted_access_geography(portals)

    return {
        "field_coverage": portals.notna().sum().sort_values(ascending=False),
        "state_counts": portal_metrics["state"].value_counts(dropna=True).sort_values(ascending=False),
        "retention_counts": portal_metrics["retention_days"].dropna().value_counts().sort_values(ascending=False),
        "detected_items": count_structured_field(portals, "What's Detected"),
        "not_detected_items": count_structured_field(portals, "What's Not Detected"),
        "prohibited_items": count_structured_field(portals, "Prohibited Uses"),
        "hotlist_items": count_structured_field(portals, "Hotlists Alerted On", dedupe_within_portal=True),
        "granted_org_items": count_structured_field(
            portals,
            "Organizations granted access",
            dedupe_within_portal=True,
            raw_items=True,
        ),
        "sharing_org_items": count_structured_field(
            portals,
            "Organizations sharing data",
            dedupe_within_portal=True,
            raw_items=True,
        ),
        "granted_access_geography": geography,
        "portal_metrics": portal_metrics,
    }
