#!/usr/bin/env python3
import requests

BASE = "https://nve.geodataonline.no/arcgis/rest/services/Nettanlegg4/MapServer/5/query"

NAMES = [
    "alta tra",
    "arendal industrinett",
    "aurland2",
    "bardufoss transformatorstasjon",
    "fana transformatorstasjon",
    "humleberget",
    "hyggevatn",
    "nes ge",
    "novle",
    "salten transformatorstasjon",
    "t35",
]


def query_name(name: str) -> dict:
    where = f"navn LIKE '%{name.replace("'", "''")}%'"
    params = {
        "where": where,
        "outFields": "navn,eier,spenning_kV,nveNetbasID",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }
    response = requests.get(BASE, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def pick_best(features: list[dict], name: str) -> dict | None:
    if not features:
        return None
    name_l = name.lower()

    def score(feature: dict):
        nm = (feature.get("properties", {}).get("navn") or "").lower()
        return (abs(len(nm) - len(name_l)), 0 if name_l in nm else 1, nm)

    return sorted(features, key=score)[0]


def main() -> int:
    results = []
    for name in NAMES:
        data = query_name(name)
        feats = data.get("features", [])
        best = pick_best(feats, name)
        if not best:
            results.append((name, None, None, 0, None))
            continue
        lon, lat = best["geometry"]["coordinates"]
        results.append((name, lat, lon, len(feats), best.get("properties", {}).get("navn")))

    for input_name, lat, lon, hits, matched_name in results:
        if lat is None:
            print(f"{input_name:28}  ->  INGEN TREFF")
        else:
            print(
                f"{input_name:28}  ->  {lat:.6f}, {lon:.6f}   (treff={hits}, match='{matched_name}')"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
