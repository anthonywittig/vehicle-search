# vehicle-search

Working data and analysis for our next-vehicle search. The core question:
**what does a candidate cost per expected remaining mile?** A cheap car
with high mileage and an expensive car with none can be compared on the
same axis.

## Layout

**Scope:** the Teslas and the Kia Niro EV at GhostX Automotive dealer 83
(St. George, UT) — the dealer we're actually shopping at — plus new-car
MSRP benchmark rows for comparison, and hand-added candidates from other
local dealers (currently one from Specialties Automotive Group, also
St. George). Other makes at dealer 83 are ignored.

- [`data/listings.json`](data/listings.json) — the candidate list: dealer
  83's inventory plus the new-car benchmarks, the dealer's fee schedule,
  and buyer-state tax config.
- [`fetch_ghostx.py`](fetch_ghostx.py) — refreshes dealer 83's Tesla and
  Kia Niro listings and its fee schedule from the GhostX tRPC API
  (`ghostxauto.com/api/trpc/listings.list`), keeping entries from other
  sources untouched and reporting listings that left inventory.
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

**Battery / mi/kWh**: each vehicle carries a `battery` object (usable kWh
when new + EPA range for its config); the table derives **mi/kWh** =
EPA range ÷ usable kWh as a battery-to-wheels efficiency figure for
comparing energy cost per mile. Capacities are community estimates —
Tesla doesn't publish them — and EPA range varies with wheel size; see
the caveats in [`ANALYSIS.md`](ANALYSIS.md).

Life assumptions by class (each an explicit `life_miles` override in the
data, so any single vehicle can be adjusted):

| Class | Life (opt/cons) | Reasoning |
|---|---|---|
| Tesla | 300k/250k | most high-mileage fleet data of any EV |
| Kia Niro EV | 200k/150k | good pack reputation, thin fleet data |

## Findings so far (2026-08-17)

All $/mi figures use out-the-door prices (fees + UT tax), optimistic life.

- The **used high-mileage Model 3 Long Ranges ($19.3–26k OTD,
  10.1–12¢/mi)** lead on value, though most are at or past Tesla's 120k
  battery warranty cap.
- Correction (2026-08-17): the **2019 M3 LR never sold** — the GhostX
  API paginates at 24 rows and our fetch only read page 1, so the
  oldest listing silently fell off when newer arrivals pushed it to
  page 2 (fetch now paginates). It's back in the table at $20,900 /
  ~$23,224 OTD, 83,776 mi → **10.7¢/mi**, 3rd place — and it's the
  **best warranty position of the cheap rows**: dual-motor AWD, ~36k
  miles left under the 120k cap *and* the 8-year clock runs to ~2027.
  The 2018s that beat it on $/mi have effectively no warranty left.
- New leader (added 2026-08-16): a **2018 M3 LR at Specialties Auto**
  (St. George) — $19,900 list / ~$22,259 OTD est., 80,012 mi (per dash
  screenshot; listing text says 79,914) → **10.1¢/mi optimistic,
  13.1¢/mi conservative**. It edges out the GhostX 2018 on both figures
  with ~31k fewer miles, still under the 120k battery warranty mileage
  cap (though the 8-year clock has likely run out on a 2018). The
  listing text claims FSD included, but the dash Software screenshot
  shows only the FSD *computer* (HW3) with basic Autopilot
  ("Traffic-Aware Cruise Control and Autosteer") as the included
  package — **FSD software apparently not included**; negotiation
  material. OTD is estimated: $599 doc (CarEdge's verified-quote report
  on this dealer) + $233 title/reg default + 7.45% UT tax.
- The **2022 Kia Niro EV — $17,793 OTD per actual checkout quote —**
  lands mid-pack at ~12.7¢/mi under its shortened 200k/150k life
  assumption, level with used Model Y Long Ranges; its conservative
  figure (~19.7¢/mi) is among the worst of the EVs. Cheap sticker, but
  the value case hinges on the pack lasting.
- Used 2020–2021 Model Y Long Ranges (~$28–31k OTD, 12.4–13.2¢/mi)
  modestly beat a new Model Y Standard (~$44.7k OTD, ~14.9¢/mi); the new
  car's full warranty and zero degradation nearly close that gap.
- A new 2026 Niro EV (~$45k OTD, ~22.5¢/mi under the shorter life) is
  the most expensive per-mile option tracked, though the 2026 adds a
  NACS port with Supercharger access.
- The federal $7,500 EV tax credit ended 2025-09-30 — no subsidy tilts
  the math toward new.
- Efficiency spread: both Niros (3.7–3.9 mi/kWh) trail every Tesla here
  (4.0–4.8), which adds roughly 0.3–0.9¢ per mile in energy at our
  ~13.8¢/kWh marginal summer rate (Rocky Mountain Power Schedule 1) —
  real but small next to the purchase-price $/mi spread. The 2024
  Model 3 Long Range (4.84, the single-motor Highland) and the 2022
  Model 3 Long Range (4.59) are the efficiency standouts.
- Gas baseline: our 2011 Toyota Sienna (V6, EPA 20 mpg combined) runs
  ~$0.20/mi in fuel at St. George's ~$3.90/gal — roughly 5–6× the
  3–4¢/mi any of these EVs costs on home charging. We put ~23,250 mi/yr
  on the van (odometer log, Nov 2024–Jul 2026; ~24,450/yr the first
  year, ~21,500/yr since), so shifting its driving to an EV saves about
  $3,700/yr in energy (~$4,500 gas vs. ~$800 charging).
