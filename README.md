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

Assume a total service life — 300k miles optimistic, 250k conservative by
default; a vehicle can override this with a `life_miles` object in
`data/listings.json` — subtract the odometer, and divide asking price by
the remaining miles. It's a purchase-price comparison, not total cost of
ownership; see [`ANALYSIS.md`](ANALYSIS.md) for the caveats (battery
warranty position is the big one the number doesn't capture).

Current overrides: the Kia Niro EV is assumed to last 200k/150k miles —
its LG pack has a good reputation but far less high-mileage fleet data
than Tesla drivetrains.

## Findings so far (2026-08-11)

- With the Niro's life assumption revised down to 200k/150k, the **used
  high-mileage Model 3 Long Ranges ($17–23k, 8.5–11¢/mi)** lead on value,
  though they're at or past Tesla's 120k battery warranty cap.
- The **2022 Kia Niro EV at $15,850 / 59,715 mi** lands mid-pack at
  ~11.3¢/mi optimistic — level with used Model Y Long Ranges — but its
  conservative figure (17.6¢/mi at a 150k life) is among the worst on the
  lot. Cheap sticker, but the value case now hinges on the pack lasting.
- Used 2020–2022 Model Y Long Ranges (~$25–28k, 11–12¢/mi) modestly beat
  a new Model Y Standard ($39,990, ~13.3¢/mi); the new car's full
  warranty and zero degradation nearly close that gap.
- A new 2026 Niro EV ($41,195, ~20.6¢/mi under the shorter life) is the
  most expensive per-mile option tracked, though the 2026 adds a NACS
  port with Supercharger access.
- The federal $7,500 EV tax credit ended 2025-09-30 — no subsidy tilts
  the math toward new.
