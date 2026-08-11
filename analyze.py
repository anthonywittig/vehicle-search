#!/usr/bin/env python3
"""Compute cost per expected remaining mile for the vehicles in data/listings.json.

Usage:
    python3 analyze.py            # print the table to stdout
    python3 analyze.py --write    # also regenerate ANALYSIS.md

The model is deliberately simple: assume a total service life for the
vehicle (default 300k miles optimistic / 250k conservative; a vehicle can
override these with a "life_miles" object in listings.json), subtract the
odometer to get expected remaining miles, and divide the asking price by
that. It ignores financing, insurance, energy, and maintenance — it is a
way to compare purchase prices across mileages, not a
total-cost-of-ownership model.
"""
import argparse
import json
from pathlib import Path

DATA = Path(__file__).parent / "data" / "listings.json"
ANALYSIS = Path(__file__).parent / "ANALYSIS.md"

DEFAULT_LIFE = {"optimistic": 300_000, "conservative": 250_000}


def load():
    with open(DATA) as f:
        return json.load(f)


def rows(vehicles):
    out = []
    for v in vehicles:
        life = {**DEFAULT_LIFE, **v.get("life_miles", {})}
        remaining = life["optimistic"] - v["mileage"]
        if remaining <= 0:
            continue
        conservative_remaining = life["conservative"] - v["mileage"]
        out.append(
            {
                "vehicle": f"{v['year']} {v['make']} {v['model']} {v['trim']}".strip(),
                "condition": v["condition"],
                "price": v["price"],
                "mileage": v["mileage"],
                "life": life,
                "remaining": remaining,
                "optimistic": v["price"] / remaining,
                "conservative": v["price"] / conservative_remaining
                if conservative_remaining > 0
                else None,
            }
        )
    out.sort(key=lambda r: r["optimistic"])
    return out


def table(rows):
    lines = [
        "| Vehicle | Condition | Price | Odometer | Life (opt/cons) "
        "| Remaining | $/mi optimistic | $/mi conservative |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        conservative = (
            f"${r['conservative']:.3f}" if r["conservative"] is not None else "—"
        )
        life = f"{r['life']['optimistic'] // 1000}k/{r['life']['conservative'] // 1000}k"
        lines.append(
            f"| {r['vehicle']} | {r['condition']} | ${r['price']:,} | {r['mileage']:,} "
            f"| {life} | {r['remaining']:,} | ${r['optimistic']:.3f} | {conservative} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate ANALYSIS.md")
    args = parser.parse_args()

    data = load()
    result = rows(data["vehicles"])
    md_table = table(result)

    print(f"Data captured: {data['captured_at']}  ({len(result)} vehicles)\n")
    print(md_table)

    if args.write:
        best = result[0]
        content = f"""# Cost per expected remaining mile

Data captured **{data['captured_at']}** · {len(result)} vehicles · sorted best value first
(by the optimistic figure).
Regenerate with `python3 analyze.py --write` after updating `data/listings.json`.

## Method

Assume a total service life — {DEFAULT_LIFE['optimistic']:,} miles optimistic,
{DEFAULT_LIFE['conservative']:,} conservative by default — subtract the odometer
to get expected remaining miles, and divide the asking price by that. A
vehicle can override the default life with a `life_miles` object in
`data/listings.json`; the "Life" column shows the assumption used. This
compares purchase prices across mileages; it is not a
total-cost-of-ownership model (no financing, insurance, energy, or
maintenance).

Current overrides: **Kia Niro EV at 200k/150k** — the Niro's LG pack has a
good reputation but far less high-mileage fleet data than Tesla
drivetrains, so it gets a materially shorter assumed life.

## Results

{md_table}

## Caveats

- The service-life assumption dominates the result. EV batteries mostly
  degrade in range rather than failing outright, so "remaining miles" is
  a planning heuristic, not a prediction.
- Warranty position matters as much as $/mi: Tesla's battery/drive-unit
  warranty is 8 yr / 100–120k mi (varies by model); Kia's is 10 yr / 100k mi.
  Cars past the cap carry pack-replacement risk (~$10–15k) that the $/mi
  figure does not capture.
- New-car benchmark rows use MSRP; Tesla prices exclude ~$1,400 in
  destination/order fees. The federal $7,500 EV tax credit ended
  2025-09-30, so no subsidy offsets new-car prices.

Current best value: **{best['vehicle']}** at ${best['price']:,} /
{best['mileage']:,} mi → ${best['optimistic']:.3f} per expected remaining mile
(${best['conservative']:.3f} conservative).
"""
        ANALYSIS.write_text(content)
        print(f"\nWrote {ANALYSIS}")


if __name__ == "__main__":
    main()
