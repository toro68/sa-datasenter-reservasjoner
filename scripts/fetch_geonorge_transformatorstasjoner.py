#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_LAYER = "https://nve.geodataonline.no/arcgis/rest/services/Nettanlegg4/MapServer/5"
QUERY_URL = f"{BASE_LAYER}/query"
USER_AGENT = "sa-datasenter-reservasjoner/1.0 (kontakt: redaksjon@aftenbladet.no)"


def fetch_json(url: str) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as resp:  # nosec - controlled URL
        return json.loads(resp.read().decode("utf-8"))


def query_batch(offset: int, limit: int) -> dict[str, Any]:
    params = {
        "where": "1=1",
        "outFields": "navn,nveNetbasID,spenning_kV,driftsattaar,eier",
        "returnGeometry": "true",
        "outSR": 4326,
        "f": "geojson",
        "resultRecordCount": limit,
        "resultOffset": offset,
    }
    return fetch_json(f"{QUERY_URL}?{urlencode(params)}")


def extract_row(feature: dict[str, Any]) -> dict[str, Any]:
    props = feature.get("properties") or {}
    geom = feature.get("geometry") or {}
    coords = geom.get("coordinates") or [None, None]
    lon = coords[0] if len(coords) > 0 else None
    lat = coords[1] if len(coords) > 1 else None
    return {
        "navn": props.get("navn") or "",
        "nveNetbasID": props.get("nveNetbasID") or "",
        "spenning_kV": props.get("spenning_kV") or "",
        "driftsattaar": props.get("driftsattaar") or "",
        "eier": props.get("eier") or "",
        "lat": lat,
        "lon": lon,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "navn",
                "nveNetbasID",
                "spenning_kV",
                "driftsattaar",
                "eier",
                "lat",
                "lon",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Hent alle transformatorstasjoner fra NVE/Geonorge (Nettanlegg4)."
    )
    parser.add_argument(
        "--out",
        default="geonorge_transformatorstasjoner.csv",
        help="Hvor CSV skal lagres (default: geonorge_transformatorstasjoner.csv)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Batch-størrelse for ArcGIS API (default: 1000)",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.25,
        help="Pause mellom kall i sekunder (default: 0.25)",
    )
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    offset = 0

    while True:
        data = query_batch(offset, args.limit)
        features = data.get("features") or []
        if not features:
            break
        rows.extend(extract_row(feature) for feature in features)
        offset += len(features)
        if len(features) < args.limit:
            break
        time.sleep(args.sleep)

    out_path = Path(args.out)
    write_csv(out_path, rows)
    print(f"Skrev {out_path} ({len(rows)} rader)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
