#!/usr/bin/env python3
import requests
from pathlib import Path

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

VARIANTS = {
    "alta tra": ["Alta", "Alta tra", "Alta TRST"],
    "arendal industrinett": ["Arendal", "Arendal industrinett"],
    "aurland2": ["Aurland 2", "Aurland2"],
    "bardufoss transformatorstasjon": ["Bardufoss", "Bardufoss transformatorstasjon"],
    "fana transformatorstasjon": ["Fana", "Fana transformatorstasjon"],
    "humleberget": ["Humleberget"],
    "hyggevatn": ["Hyggevatn"],
    "nes ge": ["Nes", "Nes GE", "Nes ge"],
    "novle": ["Novle"],
    "salten transformatorstasjon": ["Salten", "Salten transformatorstasjon"],
    "t35": ["T35", "T 35"],
}


def query_name(name: str):
    escaped = name.replace("'", "''")
    where = "UPPER(navn) LIKE '%{}%'".format(escaped.upper())
    params = {
        "where": where,
        "outFields": "navn,eier,spenning_kV,nveNetbasID",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }
    r = requests.get(BASE, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def pick_best(features, name):
    if not features:
        return None
    name_l = name.lower()
    def score(ft):
        nm = (ft["properties"].get("navn") or "").lower()
        return (abs(len(nm) - len(name_l)), 0 if name_l in nm else 1, nm)
    return sorted(features, key=score)[0]


def main() -> None:
    lines = []
    for name in NAMES:
        candidates = VARIANTS.get(name, [name])
        best = None
        used = None
        hits = 0
        for candidate in candidates:
            data = query_name(candidate)
            feats = data.get("features", [])
            if not feats:
                continue
            best = pick_best(feats, candidate)
            used = candidate
            hits = len(feats)
            if best:
                break

        if not best:
            lines.append(f"{name:28}  ->  INGEN TREFF")
            continue

        lon, lat = best["geometry"]["coordinates"]
        matched_name = best["properties"].get("navn")
        lines.append(
            f"{name:28}  ->  {lat:.6f}, {lon:.6f}   (treff={hits}, match='{matched_name}', query='{used}')"
        )

    Path("data/geonorge_results.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("WROTE data/geonorge_results.txt")


if __name__ == "__main__":
    main()
