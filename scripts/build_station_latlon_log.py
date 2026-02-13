#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import difflib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RAW_RESERVASJONER = ROOT / "data" / "Reservasjoner - Ark 1.csv"
RAW_KAPASITETSKO = ROOT / "data" / "Reservasjoner - Kapasitetskø.csv"
CACHE_PATH = ROOT / "geocode_cache.json"
KARTGRUNNLAG_PATH = ROOT / "kartgrunnlag.geojson"
OUT_CSV = ROOT / "data" / "stasjoner_latlon_log.csv"


def load_cache() -> dict[str, dict[str, Any] | None]:
    if not CACHE_PATH.exists():
        return {}
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))


def load_kartgrunnlag() -> list[dict[str, Any]]:
    if not KARTGRUNNLAG_PATH.exists():
        return []
    data = json.loads(KARTGRUNNLAG_PATH.read_text(encoding="utf-8"))
    return data.get("features", [])


def normalize_name(value: str) -> str:
    return (
        (value or "")
        .lower()
        .replace("æ", "ae")
        .replace("ø", "oe")
        .replace("å", "aa")
        .strip()
    )


def split_alpha_digit(value: str) -> str:
    if not value:
        return value
    out = [value[0]]
    for prev, curr in zip(value, value[1:]):
        if (prev.isalpha() and curr.isdigit()) or (prev.isdigit() and curr.isalpha()):
            out.append(" ")
        out.append(curr)
    return "".join(out)


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
    normalized = normalize_name(value)
    normalized = split_alpha_digit(normalized)
    return clean_tokens(normalized)


def variant_keys(value: str) -> list[str]:
    base = normalize_station(value)
    variants = {base}
    if not base:
        return []

    for token in [
        "transformatorstasjon",
        "transformator",
        "transformator stasjon",
        "trst",
        "trst.",
        "trsf",
        "trsf.",
        "tra",
        "ge",
    ]:
        variants.add(base.replace(token, "").strip())

    variants = {v for v in variants if v}
    return sorted(variants, key=len, reverse=True)


def build_kartgrunnlag_index(
    features: list[dict[str, Any]],
) -> tuple[dict[str, list[tuple[str, list[float]]]], list[tuple[str, str, list[float]]]]:
    index: dict[str, list[tuple[str, list[float]]]] = {}
    normalized_entries: list[tuple[str, str, list[float]]] = []
    for feature in features:
        props = feature.get("properties") or {}
        name = props.get("navn") or ""
        coords = (feature.get("geometry") or {}).get("coordinates")
        if not name or not coords:
            continue
        for key in variant_keys(str(name)):
            index.setdefault(key, []).append((str(name), coords))
        normalized_entries.append((normalize_station(str(name)), str(name), coords))
    return index, normalized_entries


def read_stasjoner(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        stasjoner = []
        for row in reader:
            stasjon = (row.get("Stasjon for tilknytning i transmisjonsnettet") or "").strip()
            if stasjon:
                stasjoner.append(stasjon)
        return stasjoner


def main() -> None:
    cache = load_cache()
    features = load_kartgrunnlag()
    kart_index, kart_entries = build_kartgrunnlag_index(features)
    stasjoner = set()
    stasjoner.update(read_stasjoner(RAW_RESERVASJONER))
    stasjoner.update(read_stasjoner(RAW_KAPASITETSKO))

    rows = []
    for stasjon in sorted(stasjoner, key=lambda s: s.lower()):
        in_cache = "ja" if stasjon in cache else "nei"
        source = "mangler"
        lat = ""
        lon = ""

        result = cache.get(stasjon)
        if result is None:
            source = "null" if in_cache == "ja" else "ikke_i_cache"
        else:
            lat = str(result.get("lat", ""))
            lon = str(result.get("lon", ""))
            if result.get("comment") == "Fra kartgrunnlag.geojson":
                source = "kartgrunnlag_cache"
            else:
                source = "manual" if result.get("manual") else "cache"

        if not lat or not lon:
            for key in variant_keys(stasjon):
                matches = kart_index.get(key) or []
                if not matches:
                    continue
                name, coords = matches[0]
                lon = str(coords[0])
                lat = str(coords[1])
                source = "kartgrunnlag" if len(matches) == 1 else "kartgrunnlag_flere"
                break

        if not lat or not lon:
            target = normalize_station(stasjon)
            if target:
                candidates = {entry[0] for entry in kart_entries}
                close = difflib.get_close_matches(target, candidates, n=1, cutoff=0.92)
                if close:
                    best = close[0]
                    for normalized, name, coords in kart_entries:
                        if normalized == best:
                            lon = str(coords[0])
                            lat = str(coords[1])
                            source = "kartgrunnlag_fuzzy"
                            break

        rows.append(
            {
                "stasjon": stasjon,
                "lat": lat,
                "lon": lon,
                "kilde": source,
                "i_geocode_cache": in_cache,
            }
        )

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["stasjon", "lat", "lon", "kilde", "i_geocode_cache"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Skrev {OUT_CSV}")


if __name__ == "__main__":
    main()
