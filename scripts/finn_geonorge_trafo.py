#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
import time
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "data" / "stasjoner_latlon_log.csv"
OUTPUT_CSV = ROOT / "data" / "geonorge_kandidater.csv"

GEONORGE_UUID = "ae55f901-480d-4fdc-8f1e-58ef3004d169"
GEONORGE_METADATA_URL = f"https://kartkatalog.geonorge.no/api/metadata/{GEONORGE_UUID}"

BASE_LAYER = "https://nve.geodataonline.no/arcgis/rest/services/Nettanlegg4/MapServer/5"
QUERY_URL = f"{BASE_LAYER}/query"
USER_AGENT = "sa-datasenter-reservasjoner/1.0 (kontakt: redaksjon@aftenbladet.no)"

FIELDS = ["navn", "nveNetbasID", "spenning_kV", "driftsattaar", "eier"]


@dataclass
class Match:
    stasjon: str
    query: str
    query_type: str
    match_navn: str
    lat: str
    lon: str
    score: float
    nveNetbasID: str
    spenning_kV: str
    driftsattaar: str
    eier: str


def fetch_json(url: str) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as resp:  # nosec - controlled URL
        return json.loads(resp.read().decode("utf-8"))


def normalize(value: str) -> str:
    return (
        (value or "")
        .lower()
        .replace("æ", "ae")
        .replace("ø", "oe")
        .replace("å", "aa")
        .strip()
    )


def clean_tokens(value: str) -> str:
    cleaned = []
    prev_space = False
    for ch in value:
        if ch.isalnum():
            cleaned.append(ch)
            prev_space = False
        else:
            if not prev_space:
                cleaned.append(" ")
                prev_space = True
    return "".join(cleaned).strip()


def normalize_station(value: str) -> str:
    return clean_tokens(normalize(value))


def strip_suffixes(value: str) -> str:
    base = normalize_station(value)
    if not base:
        return base
    for token in [
        "transformatorstasjon",
        "transformator stasjon",
        "trst",
        "trst.",
        "trsf",
        "trsf.",
        "tra",
        "stasjon",
    ]:
        base = base.replace(token, "").strip()
    return base


def select_query_terms(stasjon: str) -> list[str]:
    base = strip_suffixes(stasjon)
    if not base:
        return []
    tokens = [t for t in base.split() if len(t) >= 3]
    candidates = []
    if base:
        candidates.append(base)
    if tokens:
        candidates.append(" ".join(tokens))
        candidates.extend(tokens)
    seen = set()
    ordered = []
    for item in candidates:
        if item in seen:
            continue
        ordered.append(item)
        seen.add(item)
    return ordered


def build_where_exact(name: str) -> str:
    safe = name.replace("'", "''")
    return f"UPPER(navn) = '{safe.upper()}'"


def build_where_like(term: str) -> str:
    safe = term.replace("'", "''")
    return f"UPPER(navn) LIKE '%{safe.upper()}%'"


def query_features(where: str, limit: int = 10) -> list[dict[str, Any]]:
    params = {
        "where": where,
        "outFields": ",".join(FIELDS),
        "f": "geojson",
        "outSR": 4326,
        "resultRecordCount": limit,
    }
    url = f"{QUERY_URL}?{urlencode(params)}"
    data = fetch_json(url)
    return data.get("features", [])


def score_match(stasjon: str, kandidat: str) -> float:
    return SequenceMatcher(None, normalize_station(stasjon), normalize_station(kandidat)).ratio()


def to_match(stasjon: str, query: str, query_type: str, feature: dict[str, Any]) -> Match:
    props = feature.get("properties") or {}
    geom = feature.get("geometry") or {}
    coords = geom.get("coordinates") or ["", ""]
    lon = str(coords[0]) if len(coords) > 0 else ""
    lat = str(coords[1]) if len(coords) > 1 else ""
    navn = str(props.get("navn") or "")
    return Match(
        stasjon=stasjon,
        query=query,
        query_type=query_type,
        match_navn=navn,
        lat=lat,
        lon=lon,
        score=score_match(stasjon, navn),
        nveNetbasID=str(props.get("nveNetbasID") or ""),
        spenning_kV=str(props.get("spenning_kV") or ""),
        driftsattaar=str(props.get("driftsattaar") or ""),
        eier=str(props.get("eier") or ""),
    )


def load_missing_stasjoner(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        missing = []
        for row in reader:
            stasjon = (row.get("stasjon") or "").strip()
            lat = (row.get("lat") or "").strip()
            lon = (row.get("lon") or "").strip()
            if stasjon and (not lat or not lon):
                missing.append(stasjon)
        return missing


def fetch_metadata() -> dict[str, Any] | None:
    try:
        return fetch_json(GEONORGE_METADATA_URL)
    except Exception:
        return None


def main() -> int:
    missing = load_missing_stasjoner(INPUT_CSV)
    if not missing:
        print("Fant ingen stasjoner uten lat/lon.")
        return 0

    metadata = fetch_metadata()
    if metadata:
        title = metadata.get("Title") or ""
        org = metadata.get("Organization") or ""
        print(f"Geonorge-datasett: {title} ({org})")

    matches: list[Match] = []
    for idx, stasjon in enumerate(missing, start=1):
        found = False

        exact_where = build_where_exact(stasjon)
        exact_features = query_features(exact_where)
        for feature in exact_features:
            matches.append(to_match(stasjon, stasjon, "exact", feature))
            found = True

        if not found:
            for term in select_query_terms(stasjon):
                like_where = build_where_like(term)
                features = query_features(like_where)
                if not features:
                    continue
                for feature in features:
                    matches.append(to_match(stasjon, term, "like", feature))
                found = True
                break

        if idx % 10 == 0:
            print(f"Sjekket {idx}/{len(missing)}")

        time.sleep(0.3)

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "stasjon",
                "query",
                "query_type",
                "match_navn",
                "lat",
                "lon",
                "score",
                "nveNetbasID",
                "spenning_kV",
                "driftsattaar",
                "eier",
            ],
        )
        writer.writeheader()
        for match in sorted(matches, key=lambda m: (m.stasjon.lower(), -m.score)):
            writer.writerow(
                {
                    "stasjon": match.stasjon,
                    "query": match.query,
                    "query_type": match.query_type,
                    "match_navn": match.match_navn,
                    "lat": match.lat,
                    "lon": match.lon,
                    "score": f"{match.score:.3f}",
                    "nveNetbasID": match.nveNetbasID,
                    "spenning_kV": match.spenning_kV,
                    "driftsattaar": match.driftsattaar,
                    "eier": match.eier,
                }
            )

    print(f"Skrev {OUTPUT_CSV} ({len(matches)} kandidater)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
