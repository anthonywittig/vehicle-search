# Cost per expected remaining mile

Data captured **2026-08-11** · 22 vehicles · sorted best value first
(by the optimistic figure).
Regenerate with `python3 analyze.py --write` after updating `data/listings.json`.

## Method

**Out-the-door price** = list price + doc/processing fees + title +
registration + sales tax. Fee schedules come from each dealer via the
GhostX API (`dealers.getFeesAndTaxes`); tax is
7.45% (UT,
the buyer's state) applied to (price + doc fees). This model reproduced
the actual Niro checkout quote within $5; the Niro row uses the exact
quoted numbers. New-car rows estimate Tesla's ~$1,400 destination/order
fee and a typical $497 dealer doc fee for the Kia.

**$/mi** = OTD price ÷ expected remaining miles, where remaining =
assumed service life − odometer. Default life is
300,000 optimistic / 250,000
conservative; per-vehicle `life_miles` overrides apply (the "Life"
column shows the assumption used).

Current overrides: **Kia Niro EV at 200k/150k** — the Niro's LG pack has a
good reputation but far less high-mileage fleet data than Tesla
drivetrains, so it gets a materially shorter assumed life.

This compares purchase prices across mileages; it is not a
total-cost-of-ownership model (no financing, insurance, energy, or
maintenance).

## Results

| Vehicle | Condition | List | OTD | Odometer | Life (opt/cons) | $/mi optimistic | $/mi conservative |
|---|---|---|---|---|---|---|---|
| 2019 Tesla Model 3 Long Range | used | $17,490 | $19,632* | 94,003 | 300k/250k | $0.095 | $0.126 |
| 2018 Tesla Model 3 Long Range | used | $17,250 | $19,302* | 110,728 | 300k/250k | $0.102 | $0.139 |
| 2019 Tesla Model 3 Long Range | used | $21,250 | $23,600* | 83,776 | 300k/250k | $0.109 | $0.142 |
| 2020 Tesla Model 3 Long Range | used | $18,750 | $20,914* | 111,513 | 300k/250k | $0.111 | $0.151 |
| 2020 Tesla Model 3 Long Range | used | $23,250 | $25,749* | 68,659 | 300k/250k | $0.111 | $0.142 |
| 2022 Tesla Model 3 Long Range | used | $23,500 | $26,018* | 81,906 | 300k/250k | $0.119 | $0.155 |
| 2020 Tesla Model Y Long Range | used | $25,690 | $28,371* | 71,542 | 300k/250k | $0.124 | $0.159 |
| 2022 Kia Niro EV S, Ex | used | $15,850 | $17,793 | 59,715 | 200k/150k | $0.127 | $0.197 |
| 2022 Tesla Model Y Long Range | used | $25,895 | $28,391* | 76,504 | 300k/250k | $0.127 | $0.164 |
| 2024 Tesla Model 3 Long Range | used | $30,590 | $33,636* | 36,957 | 300k/250k | $0.128 | $0.158 |
| 2023 Tesla Model 3 Long Range (Dual Motor) | used | $30,950 | $34,023* | 36,308 | 300k/250k | $0.129 | $0.159 |
| 2016 Tesla Model X P90D P90D | used | $22,995 | $25,547* | 102,130 | 300k/250k | $0.129 | $0.173 |
| 2021 Tesla Model Y Long Range | used | $27,980 | $30,832* | 65,717 | 300k/250k | $0.132 | $0.167 |
| 2023 Tesla Model 3 Performance | used | $30,250 | $33,271* | 58,353 | 300k/250k | $0.138 | $0.174 |
| 2022 Tesla Model Y Performance | used | $31,750 | $34,882* | 50,714 | 300k/250k | $0.140 | $0.175 |
| 2023 Tesla Model Y Performance | used | $33,000 | $36,226* | 45,913 | 300k/250k | $0.143 | $0.178 |
| 2019 Tesla Model S Performance | used | $36,490 | $40,047* | 22,880 | 300k/250k | $0.145 | $0.176 |
| 2026 Tesla Model Y Standard | new | $39,990 | $44,707* | 0 | 300k/250k | $0.149 | $0.179 |
| 2020 Tesla Model X Long Range | used | $29,568 | $32,609* | 95,967 | 300k/250k | $0.160 | $0.212 |
| 2026 Tesla Model Y Long Range RWD | new | $44,990 | $50,079* | 0 | 300k/250k | $0.167 | $0.200 |
| 2026 Tesla Model Y Long Range AWD | new | $48,990 | $54,377* | 0 | 300k/250k | $0.181 | $0.218 |
| 2026 Kia Niro EV Wind | new | $41,195 | $45,031* | 0 | 200k/150k | $0.225 | $0.300 |

\* estimated (dealer fee schedule + buyer-state tax); no asterisk = actual checkout quote.

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

Current best value: **2019 Tesla Model 3 Long Range** at $19,632 out the door /
94,003 mi → $0.095 per expected remaining mile
($0.126 conservative).
