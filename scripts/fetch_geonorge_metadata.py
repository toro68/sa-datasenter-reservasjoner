#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import urlopen, Request


URL = "https://kartkatalog.geonorge.no/api/metadata/ae55f901-480d-4fdc-8f1e-58ef3004d169"


def fetch(url: str) -> str:
    req = Request(url, headers={"User-Agent": "sa-datasenter-reservasjoner-tij"})
    with urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def main() -> int:
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/geonorge_metadata.json")
    try:
        text = fetch(URL)
    except HTTPError as exc:
        print(f"HTTP error {exc.code}: {exc.reason}", file=sys.stderr)
        return 1
    except URLError as exc:
        print(f"Network error: {exc.reason}", file=sys.stderr)
        return 1

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = text

    if isinstance(data, str):
        out_path.write_text(data, encoding="utf-8")
    else:
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
