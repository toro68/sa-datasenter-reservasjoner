#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT_GEOJSON = ROOT / "kartgrunnlag.geojson"

BASE_LAYER = "https://nve.geodataonline.no/arcgis/rest/services/Nettanlegg4/MapServer/5"
QUERY_URL = f"{BASE_LAYER}/query"
USER_AGENT = "sa-datasenter-reservasjoner/1.0 (kontakt: redaksjon@aftenbladet.no)"

FIELDS = [
    "navn",
    "nveNetbasID",
    "spenning_kV",
    "driftsattaar",
    "eier",
    "nveNettnivaa",
    "sosiNettnivaa",
]


def fetch_json(url: str) -> dict[str, Any]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=60) as resp:  # nosec - controlled URL
        return json.loads(resp.read().decode("utf-8"))


def get_layer_meta() -> dict[str, Any]:
    return fetch_json(f"{BASE_LAYER}?f=pjson")


def get_total_count() -> int:
    params = {
        "where": "1=1",
        "returnCountOnly": "true",
        "f": "json",
    }
    url = f"{QUERY_URL}?{urlencode(params)}"
    data = fetch_json(url)
    return int(data.get("count", 0))


def fetch_batch(offset: int, size: int) -> dict[str, Any]:
    params = {
        "where": "1=1",
        "outFields": ",".join(FIELDS),
        "f": "geojson",
        "outSR": 4326,
        "resultOffset": offset,
        "resultRecordCount": size,
    }
    url = f"{QUERY_URL}?{urlencode(params)}"
    return fetch_json(url)


def main() -> None:
    meta = get_layer_meta()
    max_count = int(meta.get("maxRecordCount", 2000))
    total = get_total_count()
    print(f"Total features: {total} (batch {max_count})")

    features: list[dict[str, Any]] = []
    offset = 0
    while offset < total:
        batch = fetch_batch(offset, max_count)
        batch_features = batch.get("features", [])
        features.extend(batch_features)
        offset += max_count
        print(f"Hentet {len(features)}/{total}")
        if not batch_features:
            break

    geojson = {"type": "FeatureCollection", "features": features}
    OUT_GEOJSON.write_text(json.dumps(geojson, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Skrev {OUT_GEOJSON}")


if __name__ == "__main__":
    main()
