#!/usr/bin/env python3
"""Compute cost per expected remaining mile for the vehicles in data/listings.json.

Usage:
    python3 analyze.py            # print the table to stdout
    python3 analyze.py --write    # also regenerate ANALYSIS.md

The model is deliberately simple: assume a total service life for the
vehicle (default 300k miles, with a conservative 250k alternative),
subtract the odometer to get expected remaining miles, and divide the
asking price by that. It ignores financing, insurance, energy, and
maintenance — it is a way to compare purchase prices across mileages,
not a total-cost-of-ownership model.
"""
import argparse
import json
from pathlib import Path

DATA = Path(__file__).parent / "data" / "listings.json"
ANALYSIS = Path(__file__).parent / "ANALYSIS.md"

LIFESPANS = [300_000, 250_000]


def load():
    with open(DATA) as f:
        return json.load(f)


def rows(vehicles, primary_life, secondary_life):
    out = []
    for v in vehicles:
        remaining = primary_life - v["mileage"]
        if remaining <= 0:
            continue
        out.append(
            {
                "vehicle": f"{v['year']} {v['make']} {v['model']} {v['trim']}".strip(),
                "condition": v["condition"],
                "price": v["price"],
                "mileage": v["mileage"],
                "remaining": remaining,
                "primary": v["price"] / remaining,
                "secondary": v["price"] / (secondary_life - v["mileage"])
                if secondary_life > v["mileage"]
                else None,
            }
        )
    out.sort(key=lambda r: r["primary"])
    return out


def table(rows, primary_life, secondary_life):
    lines = [
        f"| Vehicle | Condition | Price | Odometer | Remaining (of {primary_life // 1000}k) "
        f"| $/mi @{primary_life // 1000}k | $/mi @{secondary_life // 1000}k |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        secondary = f"${r['secondary']:.3f}" if r["secondary"] is not None else "—"
        lines.append(
            f"| {r['vehicle']} | {r['condition']} | ${r['price']:,} | {r['mileage']:,} "
            f"| {r['remaining']:,} | ${r['primary']:.3f} | {secondary} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate ANALYSIS.md")
    parser.add_argument(
        "--life",
        type=int,
        default=LIFESPANS[0],
        help="primary expected total service life in miles (default 300000)",
    )
    args = parser.parse_args()

    data = load()
    primary, secondary = args.life, LIFESPANS[1]
    result = rows(data["vehicles"], primary, secondary)
    md_table = table(result, primary, secondary)

    print(f"Data captured: {data['captured_at']}  ({len(result)} vehicles)\n")
    print(md_table)

    if args.write:
        best = result[0]
        content = f"""# Cost per expected remaining mile

Data captured **{data['captured_at']}** · {len(result)} vehicles · sorted best value first.
Regenerate with `python3 analyze.py --write` after updating `data/listings.json`.

## Method

Assume a total service life of {primary:,} miles (with a conservative
{secondary:,}-mile alternative), subtract the odometer to get expected
remaining miles, and divide the asking price by that. This compares
purchase prices across mileages; it is not a total-cost-of-ownership
model (no financing, insurance, energy, or maintenance).

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
{best['mileage']:,} mi → ${best['primary']:.3f} per expected remaining mile.
"""
        ANALYSIS.write_text(content)
        print(f"\nWrote {ANALYSIS}")


if __name__ == "__main__":
    main()
