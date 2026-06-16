"""Fetch and normalize OFAC SDN CSV flat file rows.

OFAC SDN data is public and official. This module normalizes only the primary
SDN.CSV rows for teaching. Production diligence should also account for
addresses, aliases, comments, weak aliases, and official instructions.
"""

from __future__ import annotations

import argparse
import csv
import sys
import urllib.error
from pathlib import Path
from urllib.request import Request, urlopen


# Canonical OFAC publication endpoint (sanctions list service). The legacy
# treasury.gov path is retained as a fallback for environments that still
# resolve it.
OFAC_SDN_CSV_URL = "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV"
OFAC_SDN_CSV_LEGACY_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"

SDN_COLUMNS = [
    "uid",
    "name",
    "sdn_type",
    "program",
    "title",
    "call_sign",
    "vessel_type",
    "tonnage",
    "gross_registered_tonnage",
    "vessel_flag",
    "vessel_owner",
    "remarks",
]


def _fetch_one(url: str, timeout: int) -> str:
    req = Request(url, headers={"User-Agent": "ns-diligence-lab/0.1"})
    with urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8-sig", errors="replace")


def fetch_text(url: str | None = None, timeout: int = 30) -> str:
    """Fetch the OFAC SDN CSV text.

    When no explicit URL is given, try the canonical endpoint first and fall
    back to the legacy treasury.gov path on failure. Any network failure is
    surfaced as a clean OFACSourceUnreachable error instead of a raw traceback.
    """

    if url is not None:
        candidates = [url]
    else:
        candidates = [OFAC_SDN_CSV_URL, OFAC_SDN_CSV_LEGACY_URL]

    last_error: Exception | None = None
    for candidate in candidates:
        try:
            return _fetch_one(candidate, timeout)
        except (urllib.error.URLError, OSError) as exc:
            last_error = exc
            continue
    raise OFACSourceUnreachable("OFAC source unreachable; try again later") from last_error


class OFACSourceUnreachable(RuntimeError):
    """Raised when no OFAC SDN endpoint can be reached."""


def _has_visible_text(value: str) -> bool:
    return bool("".join(ch for ch in value if ch.isprintable()).strip())


def parse_sdn_csv(text: str, limit: int | None = None) -> list[dict[str, str]]:
    reader = csv.reader(text.splitlines())
    rows: list[dict[str, str]] = []
    for raw in reader:
        if not raw:
            continue
        # Skip EOF / control-only rows: the SDN flat file terminates with a
        # row whose first field is empty or holds only control characters
        # (for example the legacy \x1a end-of-file marker).
        if not _has_visible_text(raw[0]) or not any(_has_visible_text(field) for field in raw):
            continue
        padded = raw + [""] * (len(SDN_COLUMNS) - len(raw))
        row = {name: padded[idx].strip() for idx, name in enumerate(SDN_COLUMNS)}
        rows.append(
            {
                "source": "OFAC SDN",
                "uid": row["uid"],
                "name": row["name"],
                "type": row["sdn_type"],
                "programs": row["program"],
                "remarks": row["remarks"],
            }
        )
        if limit is not None and len(rows) >= limit:
            break
    return rows


def write_rows(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "uid", "name", "type", "programs", "remarks"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch and normalize OFAC SDN CSV rows.")
    parser.add_argument("output_csv", type=Path)
    parser.add_argument(
        "--url",
        default=None,
        help="Override source URL. Default tries the canonical OFAC endpoint, then the legacy path.",
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    try:
        text = fetch_text(args.url)
    except OFACSourceUnreachable as exc:
        print(exc, file=sys.stderr)
        return 1
    rows = parse_sdn_csv(text, args.limit)
    write_rows(rows, args.output_csv)
    print("OFAC SDN rows written:", {"rows": len(rows), "output": str(args.output_csv)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
