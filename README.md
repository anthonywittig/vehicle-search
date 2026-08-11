# vehicle-search

Working data and analysis for our next-vehicle search. The core question:
**what does a candidate cost per expected remaining mile?** A cheap car
with high mileage and an expensive car with none can be compared on the
same axis.

## Layout

- [`data/listings.json`](data/listings.json) — the candidate list: used
  listings (currently GhostX Automotive's Tesla inventory plus their Kia
  Niro EV) and new-car MSRP benchmark rows.
- [`fetch_ghostx.py`](fetch_ghostx.py) — refreshes the GhostX entries from
  the dealer's tRPC API (`ghostxauto.com/api/trpc/listings.list`), keeping
  entries from other sources untouched.
- [`analyze.py`](analyze.py) — computes $/expected-remaining-mile and
  regenerates [`ANALYSIS.md`](ANALYSIS.md).
- [`ANALYSIS.md`](ANALYSIS.md) — the current results table, method, and
  caveats. Generated; don't edit by hand.

## Usage

```sh
python3 fetch_ghostx.py       # refresh GhostX listings in data/listings.json
python3 analyze.py --write    # recompute and regenerate ANALYSIS.md
```

Both scripts are standard-library only. To add candidates from other
dealers or private sellers, append entries to `data/listings.json` by hand
(match the existing shape; use `"condition": "used"` and a descriptive
`"source"`), then rerun `analyze.py --write`.

## Method (short version)

**Out-the-door price** = list + doc/processing + title + registration +
sales tax. Per-dealer fee schedules come from the GhostX API
(`dealers.getFeesAndTaxes`); tax is the buyer-state rate (UT, 7.45%)
applied to price + doc, which reproduced our actual Niro checkout quote
within $5 — the Niro uses the exact quoted numbers.

**$/mi** = OTD price ÷ expected remaining miles, assuming a total service
life — 300k miles optimistic, 250k conservative by default; a vehicle can
override this with a `life_miles` object in `data/listings.json`. It's a
purchase-price comparison, not total cost of ownership; see
[`ANALYSIS.md`](ANALYSIS.md) for the caveats (battery warranty position
is the big one the number doesn't capture).

Current overrides: the Kia Niro EV is assumed to last 200k/150k miles —
its LG pack has a good reputation but far less high-mileage fleet data
than Tesla drivetrains.

## Findings so far (2026-08-11)

All $/mi figures use out-the-door prices (fees + UT tax), optimistic life.

- The **used high-mileage Model 3 Long Ranges ($19.3–26k OTD,
  9.5–12¢/mi)** lead on value, though they're at or past Tesla's 120k
  battery warranty cap.
- The **2022 Kia Niro EV — $17,793 OTD per actual checkout quote —**
  lands mid-pack at ~12.7¢/mi under its shortened 200k/150k life
  assumption, level with used Model Y Long Ranges; its conservative
  figure (~19.7¢/mi) is among the worst tracked. Cheap sticker, but the
  value case hinges on the pack lasting.
- Fees and tax add ~9–12% to sticker across the board (doc $444–497,
  title + registration ~$160–230, a $189 platform processing fee at some
  dealers, 7.45% UT tax), so they don't reorder much — but they widen
  the gap between cheap and expensive cars in absolute dollars.
- Used 2020–2022 Model Y Long Ranges (~$28–31k OTD, 12.4–13.2¢/mi)
  modestly beat a new Model Y Standard (~$44.7k OTD, ~14.9¢/mi); the new
  car's full warranty and zero degradation nearly close that gap.
- A new 2026 Niro EV (~$45k OTD, ~22.5¢/mi under the shorter life) is
  the most expensive per-mile option tracked, though the 2026 adds a
  NACS port with Supercharger access.
- The federal $7,500 EV tax credit ended 2025-09-30 — no subsidy tilts
  the math toward new.
