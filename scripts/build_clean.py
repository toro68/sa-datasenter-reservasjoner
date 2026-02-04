#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SRC_CSV = ROOT / "Reservasjoner - Ark 1.csv"
OUT_CLEAN_CSV = ROOT / "datasett_clean.csv"
OUT_CLEAN_JSON = ROOT / "datasett_clean.json"
OUT_SUMMARY_JSON = ROOT / "summary.json"


def parse_date_ddmmyyyy(value: str) -> str | None:
    value = (value or "").strip()
    if not value:
        return None
    return datetime.strptime(value, "%d.%m.%Y").date().isoformat()


def parse_mw(value: str) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    value = value.replace(" ", "").replace(",", ".")
    return float(value)


def norm_key(value: str) -> str:
    return (value or "").strip()


@dataclass(frozen=True)
class CleanRow:
    saksnr: str
    stasjon: str
    omradeplan: str
    prisomrade: str | None
    statnetts_kunde: str
    sluttkunde: str
    naringstype: str
    reservert_mw: float | None
    reservert_dato: str | None
    onsket_tilknytning: str | None
    kundens_referanse: str | None
    kunde_og_tilknytningsansvarlig: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "saksnr": self.saksnr,
            "stasjon": self.stasjon,
            "omradeplan": self.omradeplan,
            "prisomrade": self.prisomrade,
            "statnetts_kunde": self.statnetts_kunde,
            "sluttkunde": self.sluttkunde,
            "naringstype": self.naringstype,
            "reservert_mw": self.reservert_mw,
            "reservert_dato": self.reservert_dato,
            "onsket_tilknytning": self.onsket_tilknytning,
            "kundens_referanse": self.kundens_referanse,
            "kunde_og_tilknytningsansvarlig": self.kunde_og_tilknytningsansvarlig,
        }


def build_clean_row(raw: dict[str, str]) -> CleanRow:
    saksnr = norm_key(raw.get("Saksnr."))
    stasjon = norm_key(raw.get("Stasjon for tilknytning i transmisjonsnettet"))
    omradeplan = norm_key(raw.get("Områdeplan"))
    prisomrade = norm_key(raw.get("Prisområde")) or None
    statnetts_kunde = norm_key(raw.get("Statnetts kunde"))
    sluttkunde = norm_key(raw.get("Sluttkunde"))
    naringstype = norm_key(raw.get("Næringstype"))
    reservert_mw = parse_mw(raw.get("Reservert kapasitet (MW)", ""))
    reservert_dato = parse_date_ddmmyyyy(raw.get("Dato for når Statnett reserverte kapasitet til kunden", ""))
    onsket_tilknytning = parse_date_ddmmyyyy(raw.get("Kundens ønskede tilknytningstidspunkt", ""))
    kundens_referanse = norm_key(raw.get("Kundens referanse")) or None
    kunde_og_tilknytningsansvarlig = norm_key(raw.get("Kunde og tilknytningsansvarlig")) or None

    return CleanRow(
        saksnr=saksnr,
        stasjon=stasjon,
        omradeplan=omradeplan,
        prisomrade=prisomrade,
        statnetts_kunde=statnetts_kunde,
        sluttkunde=sluttkunde,
        naringstype=naringstype,
        reservert_mw=reservert_mw,
        reservert_dato=reservert_dato,
        onsket_tilknytning=onsket_tilknytning,
        kundens_referanse=kundens_referanse,
        kunde_og_tilknytningsansvarlig=kunde_og_tilknytningsansvarlig,
    )


def write_clean_csv(rows: list[CleanRow]) -> None:
    fieldnames = list(rows[0].to_dict().keys()) if rows else []
    with OUT_CLEAN_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_dict())


def write_clean_json(rows: list[CleanRow]) -> None:
    OUT_CLEAN_JSON.write_text(
        json.dumps([r.to_dict() for r in rows], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_summary(rows: list[CleanRow]) -> None:
    total_mw = sum((r.reservert_mw or 0.0) for r in rows)
    by_naringstype: dict[str, float] = {}
    by_prisomrade: dict[str, float] = {}

    for r in rows:
        mw = r.reservert_mw or 0.0
        by_naringstype[r.naringstype] = by_naringstype.get(r.naringstype, 0.0) + mw
        if r.prisomrade:
            by_prisomrade[r.prisomrade] = by_prisomrade.get(r.prisomrade, 0.0) + mw

    summary = {
        "rows": len(rows),
        "total_mw": round(total_mw, 3),
        "by_naringstype_mw": dict(sorted(by_naringstype.items(), key=lambda kv: kv[1], reverse=True)),
        "by_prisomrade_mw": dict(sorted(by_prisomrade.items(), key=lambda kv: kv[1], reverse=True)),
    }

    OUT_SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if not SRC_CSV.exists():
        raise SystemExit(f"Missing source file: {SRC_CSV}")

    with SRC_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [build_clean_row(r) for r in reader]

    write_clean_csv(rows)
    write_clean_json(rows)
    write_summary(rows)

    print(f"Wrote {OUT_CLEAN_CSV.name}, {OUT_CLEAN_JSON.name}, {OUT_SUMMARY_JSON.name} ({len(rows)} rows)")


if __name__ == "__main__":
    main()

