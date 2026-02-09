#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

DATASETS = [
    ROOT / "datasett_clean.json",
    ROOT / "kapasitetsko_clean.json",
]

OUT_GEOJSON = ROOT / "kartgrunnlag.geojson"
CACHE_PATH = ROOT / "geocode_cache.json"
MISSING_PATH = ROOT / "missing_stasjoner.txt"
FACTCHECK_OVERVIEW = ROOT / "data" / "stasjoner_faktasjekk_oversikt.csv"

USER_AGENT = "sa-datasenter-reservasjoner/1.0 (kontakt: redaksjon@aftenbladet.no)"
BASE_URL = "https://nominatim.openstreetmap.org/search"


def load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_cache() -> dict[str, dict[str, Any] | None]:
    if not CACHE_PATH.exists():
        return {}
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))


def save_cache(cache: dict[str, dict[str, Any] | None]) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_factcheck_overview(stasjoner: list[str], cache: dict[str, dict[str, Any] | None]) -> None:
    fieldnames = ["stasjon", "i_geocode_cache", "har_koordinat", "har_null"]
    with FACTCHECK_OVERVIEW.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for stasjon in stasjoner:
            if stasjon in cache:
                result = cache[stasjon]
                i_cache = "ja"
            else:
                result = None
                i_cache = "nei"

            har_null = "nei"
            har_koordinat = "nei"
            if result is None:
                har_null = "ja"
            else:
                try:
                    float(result["lat"])
                    float(result["lon"])
                    har_koordinat = "ja"
                except Exception:
                    har_koordinat = "nei"

            writer.writerow(
                {
                    "stasjon": stasjon,
                    "i_geocode_cache": i_cache,
                    "har_koordinat": har_koordinat,
                    "har_null": har_null,
                }
            )


def nominatim_search(query: str) -> dict[str, Any] | None:
    params = {
        "format": "json",
        "q": query,
        "countrycodes": "no",
        "limit": 1,
        "addressdetails": 0,
    }
    url = f"{BASE_URL}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as resp:  # nosec - controlled URL
        data = json.loads(resp.read().decode("utf-8"))
    if not data:
        return None
    return data[0]


def guess_query(stasjon: str) -> str:
    s = stasjon.strip()
    if not s:
        return s
    if "stasjon" in s.lower():
        return f"{s}, Norge"
    return f"{s} stasjon, Norge"


def main() -> None:
    rows = []
    for path in DATASETS:
        rows.extend(load_rows(path))

    stasjoner = sorted({(r.get("stasjon") or "").strip() for r in rows if (r.get("stasjon") or "").strip()})

    cache = load_cache()
    missing: list[str] = []
    features = []

    for idx, stasjon in enumerate(stasjoner, start=1):
        if stasjon in cache:
            result = cache[stasjon]
        else:
            query = guess_query(stasjon)
            try:
                result = nominatim_search(query)
            except Exception:
                result = None
            cache[stasjon] = result
            save_cache(cache)
            time.sleep(1.1)

        if not result:
            missing.append(stasjon)
            continue

        try:
            lat = float(result["lat"])
            lon = float(result["lon"])
        except Exception:
            missing.append(stasjon)
            continue

        features.append(
            {
                "type": "Feature",
                "properties": {
                    "stasjon": stasjon,
                    "display_name": result.get("display_name"),
                },
                "geometry": {"type": "Point", "coordinates": [lon, lat]},
            }
        )

        if idx % 10 == 0:
            print(f"Geokodet {idx}/{len(stasjoner)}")

    geojson = {"type": "FeatureCollection", "features": features}
    OUT_GEOJSON.write_text(json.dumps(geojson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MISSING_PATH.write_text("\n".join(missing) + "\n", encoding="utf-8")
    write_factcheck_overview(stasjoner, cache)

    print(f"Totalt stasjoner: {len(stasjoner)}")
    print(f"Funnet: {len(features)}")
    print(f"Mangler: {len(missing)}")
    print(f"Skrev {OUT_GEOJSON}")
    print(f"Skrev {MISSING_PATH}")
    print(f"Skrev {FACTCHECK_OVERVIEW}")


if __name__ == "__main__":
    main()
