#!/usr/bin/env python3
"""Compute cost per expected remaining mile for the vehicles in data/listings.json.

Usage:
    python3 analyze.py            # print the table to stdout
    python3 analyze.py --write    # also regenerate ANALYSIS.md

Two models stack here:

1. Out-the-door (OTD) price: list price + doc/processing fees + title +
   registration + sales tax. Fees come from the dealer's schedule in the
   "dealers" table; tax uses config.buyer_tax_rate applied to
   (price + doc fees), since tax and registration follow the buyer's
   state, not the dealer's. A vehicle with "fees_quoted" (an actual
   checkout quote) uses those exact numbers instead. New-car benchmark
   rows use their "fees_estimate".

2. Expected remaining miles: assume a total service life (default 300k
   optimistic / 250k conservative; per-vehicle "life_miles" overrides),
   subtract the odometer. $/mi = OTD price / remaining miles.

It ignores financing, insurance, energy, and maintenance — it compares
purchase prices across mileages, not total cost of ownership.
"""
import argparse
import json
from pathlib import Path

DATA = Path(__file__).parent / "data" / "listings.json"
ANALYSIS = Path(__file__).parent / "ANALYSIS.md"

DEFAULT_LIFE = {"optimistic": 300_000, "conservative": 250_000}
DEFAULT_TITLE_REG = 233.00  # fallback when no dealer schedule applies


def load():
    with open(DATA) as f:
        return json.load(f)


def otd_price(v, dealers, tax_rate):
    """Out-the-door price and how it was derived ("quoted" or "estimated")."""
    price = v["price"]
    quoted = v.get("fees_quoted")
    if quoted:
        return price + quoted["doc"] + quoted["tax_title_registration"], "quoted"

    dealer = dealers.get(str(v.get("dealer_id", "")))
    if dealer:
        fees = dealer["fees"]
        doc = fees.get("doc", 0) + fees.get("processing", 0)
        title_reg = fees.get("title", 0) + fees.get("registration", 0)
    else:
        est = v.get("fees_estimate", {})
        doc = est.get("doc", 0)
        title_reg = DEFAULT_TITLE_REG
    tax = tax_rate * (price + doc)
    return price + doc + title_reg + tax, "estimated"


def rows(data):
    dealers = data.get("dealers", {})
    tax_rate = data.get("config", {}).get("buyer_tax_rate", 0.0)
    out = []
    for v in data["vehicles"]:
        life = {**DEFAULT_LIFE, **v.get("life_miles", {})}
        remaining = life["optimistic"] - v["mileage"]
        if remaining <= 0:
            continue
        conservative_remaining = life["conservative"] - v["mileage"]
        otd, basis = otd_price(v, dealers, tax_rate)
        out.append(
            {
                "vehicle": f"{v['year']} {v['make']} {v['model']} {v['trim']}".strip(),
                "condition": v["condition"],
                "price": v["price"],
                "otd": otd,
                "basis": basis,
                "mileage": v["mileage"],
                "life": life,
                "remaining": remaining,
                "optimistic": otd / remaining,
                "conservative": otd / conservative_remaining
                if conservative_remaining > 0
                else None,
            }
        )
    out.sort(key=lambda r: r["optimistic"])
    return out


def table(rows):
    lines = [
        "| Vehicle | Condition | List | OTD | Odometer | Life (opt/cons) "
        "| $/mi optimistic | $/mi conservative |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        conservative = (
            f"${r['conservative']:.3f}" if r["conservative"] is not None else "—"
        )
        life = f"{r['life']['optimistic'] // 1000}k/{r['life']['conservative'] // 1000}k"
        otd = f"${r['otd']:,.0f}" + ("" if r["basis"] == "quoted" else "*")
        lines.append(
            f"| {r['vehicle']} | {r['condition']} | ${r['price']:,} | {otd} "
            f"| {r['mileage']:,} | {life} | ${r['optimistic']:.3f} | {conservative} |"
        )
    lines.append("")
    lines.append(
        "\\* estimated (dealer fee schedule + buyer-state tax); "
        "no asterisk = actual checkout quote."
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate ANALYSIS.md")
    args = parser.parse_args()

    data = load()
    result = rows(data)
    md_table = table(result)
    config = data.get("config", {})

    print(f"Data captured: {data['captured_at']}  ({len(result)} vehicles)\n")
    print(md_table)

    if args.write:
        best = result[0]
        content = f"""# Cost per expected remaining mile

Data captured **{data['captured_at']}** · {len(result)} vehicles · sorted best value first
(by the optimistic figure).
Regenerate with `python3 analyze.py --write` after updating `data/listings.json`.

## Method

**Out-the-door price** = list price + doc/processing fees + title +
registration + sales tax. Fee schedules come from each dealer via the
GhostX API (`dealers.getFeesAndTaxes`); tax is
{config.get('buyer_tax_rate', 0):.2%} ({config.get('buyer_state', '?')},
the buyer's state) applied to (price + doc fees). This model reproduced
the actual Niro checkout quote within $5; the Niro row uses the exact
quoted numbers. New-car rows estimate Tesla's ~$1,400 destination/order
fee and a typical $497 dealer doc fee for the Kia.

**$/mi** = OTD price ÷ expected remaining miles, where remaining =
assumed service life − odometer. Default life is
{DEFAULT_LIFE['optimistic']:,} optimistic / {DEFAULT_LIFE['conservative']:,}
conservative; per-vehicle `life_miles` overrides apply (the "Life"
column shows the assumption used).

Current overrides: **Kia Niro EV at 200k/150k** — the Niro's LG pack has a
good reputation but far less high-mileage fleet data than Tesla
drivetrains, so it gets a materially shorter assumed life.

This compares purchase prices across mileages; it is not a
total-cost-of-ownership model (no financing, insurance, energy, or
maintenance).

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
- Estimated OTD prices assume the buyer's tax rate on (price + doc);
  actual tax, title, and registration are set at registration time and
  can differ (e.g. Utah's age-based uniform fee and EV registration
  surcharge shift the fixed part by roughly ±$100).
- The federal $7,500 EV tax credit ended 2025-09-30, so no subsidy
  offsets new-car prices.

Current best value: **{best['vehicle']}** at ${best['otd']:,.0f} out the door /
{best['mileage']:,} mi → ${best['optimistic']:.3f} per expected remaining mile
(${best['conservative']:.3f} conservative).
"""
        ANALYSIS.write_text(content)
        print(f"\nWrote {ANALYSIS}")


if __name__ == "__main__":
    main()
