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

Each vehicle's "battery" object carries usable capacity (kWh, when new)
and the EPA range for its config; mi/kWh = EPA range / usable kWh, a
battery-to-wheels efficiency figure for comparing energy cost per mile.

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
        battery = v.get("battery", {})
        usable_kwh = battery.get("usable_kwh")
        epa_range = battery.get("epa_range_mi")
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
                "usable_kwh": usable_kwh,
                "epa_range": epa_range,
                "mi_per_kwh": epa_range / usable_kwh
                if usable_kwh and epa_range
                else None,
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
        "| Usable kWh | EPA range | mi/kWh | $/mi optimistic | $/mi conservative |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        conservative = (
            f"${r['conservative']:.3f}" if r["conservative"] is not None else "—"
        )
        life = f"{r['life']['optimistic'] // 1000}k/{r['life']['conservative'] // 1000}k"
        otd = f"${r['otd']:,.0f}" + ("" if r["basis"] == "quoted" else "*")
        kwh = f"{r['usable_kwh']:g}" if r["usable_kwh"] else "—"
        epa = f"{r['epa_range']:,} mi" if r["epa_range"] else "—"
        eff = f"{r['mi_per_kwh']:.2f}" if r["mi_per_kwh"] else "—"
        lines.append(
            f"| {r['vehicle']} | {r['condition']} | ${r['price']:,} | {otd} "
            f"| {r['mileage']:,} | {life} | {kwh} | {epa} | {eff} "
            f"| ${r['optimistic']:.3f} | {conservative} |"
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
quoted numbers. Rows without a GhostX fee schedule use a per-row doc-fee
estimate plus a $233 title/registration default: ~$1,400
destination/order for new Teslas, a typical $497 dealer doc fee for the
new Kia, and $599 for Specialties Auto (per CarEdge's verified-quote
dealer report).

**$/mi** = OTD price ÷ expected remaining miles, where remaining =
assumed service life − odometer. Default life is
{DEFAULT_LIFE['optimistic']:,} optimistic / {DEFAULT_LIFE['conservative']:,}
conservative; per-vehicle `life_miles` overrides apply (the "Life"
column shows the assumption used).

Life assumptions: Teslas use the 300k/250k default (deepest high-mileage
fleet data of any EV); the Kia Niro EV gets 200k/150k via a `life_miles`
override (good pack reputation, thin fleet data). See each vehicle's
`notes`.

**Battery / efficiency**: "Usable kWh" is the pack's usable capacity when
new; "EPA range" is the official rating for that config; **mi/kWh** =
EPA range ÷ usable kWh — battery-to-wheels efficiency, i.e. what a kWh
in the pack buys you in miles. Higher is cheaper to run: our marginal
summer rate is ~$0.138/kWh (Rocky Mountain Power Schedule 1, Jul 2026
bill: 12.01¢ Block 2 + ~11% riders + 3.6% tax), so with ~10% charging
losses 4.5 mi/kWh costs about $0.034/mi in energy vs. $0.041/mi at
3.7 mi/kWh. Winter block rates are lower. For comparison, our 2011
Toyota Sienna (V6, EPA 20 mpg combined) at St. George's ~$3.90/gal
costs about **$0.20/mi in gas** — roughly 5–6× any EV here. We drive
the van ~21,500 mi/yr (odometer 228,111 → 242,767 between 2025-11-03
and 2026-07-10, 14,656 mi in 249 days), so that's ~$4,300/yr in gas
vs. ~$750/yr of home charging — **about $3,500/yr saved** if the EV
absorbs the van's driving.

This compares purchase prices across mileages; it is not a
total-cost-of-ownership model (no financing, insurance, energy, or
maintenance).

## Results

{md_table}

## Caveats

- The service-life assumption dominates the result. EV batteries mostly
  degrade in range rather than failing outright, so "remaining miles" is
  a planning heuristic, not a prediction.
- Battery figures are when-new specs. Tesla doesn't publish pack capacity,
  so usable kWh are community/EV-database estimates (±2–3 kWh depending on
  cell supplier and build window); a used pack typically holds ~88–95% of
  it at these odometer readings. EPA range also varies with wheel size (see the
  2022 Model 3's `battery.note`).
- mi/kWh here is battery-to-wheels (EPA range ÷ usable kWh). Charging
  losses of ~10–15% mean cost-from-the-wall is correspondingly worse;
  EPA's kWh/100mi label figure includes those losses.
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
