# Cost per expected remaining mile

Data captured **2026-08-11** · 28 vehicles · sorted best value first
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

Life assumptions vary by vehicle class (each an explicit `life_miles`
override in the data): Teslas keep the 300k/250k default (deepest
high-mileage fleet data of any EV); the Kia Niro EV gets 200k/150k (good
pack reputation, thin fleet data); the Ford Mach-E 250k/200k; full-size
trucks 250k/200k; European ICE vehicles 200k/150k (maintenance costs
typically make 200k the practical ceiling). See each vehicle's `notes`.

This compares purchase prices across mileages; it is not a
total-cost-of-ownership model (no financing, insurance, energy, or
maintenance).

## Results

| Vehicle | Condition | List | OTD | Odometer | Life (opt/cons) | $/mi optimistic | $/mi conservative |
|---|---|---|---|---|---|---|---|
| 2016 Volkswagen Beetle 1.8T S, Wolfsburg Edition, Fleet Edition,Classic | used | $7,500 | $8,826* | 112,561 | 200k/150k | $0.101 | $0.236 |
| 2018 Tesla Model 3 Long Range | used | $17,250 | $19,302* | 110,728 | 300k/250k | $0.102 | $0.139 |
| 2020 Tesla Model 3 Long Range | used | $18,750 | $20,914* | 111,513 | 300k/250k | $0.111 | $0.151 |
| 2020 Tesla Model 3 Long Range | used | $23,250 | $25,749* | 68,659 | 300k/250k | $0.111 | $0.142 |
| 2022 Tesla Model 3 Long Range | used | $23,500 | $26,018* | 81,906 | 300k/250k | $0.119 | $0.155 |
| 2020 Tesla Model Y Long Range | used | $25,690 | $28,371* | 71,542 | 300k/250k | $0.124 | $0.159 |
| 2022 Kia Niro EV S, Ex | used | $15,850 | $17,793 | 59,715 | 200k/150k | $0.127 | $0.197 |
| 2024 Tesla Model 3 Long Range | used | $30,590 | $33,636* | 36,957 | 300k/250k | $0.128 | $0.158 |
| 2023 Tesla Model 3 Long Range (Dual Motor) | used | $30,950 | $34,023* | 36,308 | 300k/250k | $0.129 | $0.159 |
| 2021 Tesla Model Y Long Range | used | $27,980 | $30,832* | 65,717 | 300k/250k | $0.132 | $0.167 |
| 2016 Audi A5 S Line Quattro Premium | used | $11,750 | $13,392* | 100,166 | 200k/150k | $0.134 | $0.269 |
| 2023 Tesla Model 3 Performance | used | $30,250 | $33,271* | 58,353 | 300k/250k | $0.138 | $0.174 |
| 2022 Tesla Model Y Performance | used | $31,750 | $34,882* | 50,714 | 300k/250k | $0.140 | $0.175 |
| 2023 Ford Mustang Mach-E Premium | used | $29,750 | $32,733* | 16,662 | 250k/200k | $0.140 | $0.179 |
| 2023 Tesla Model Y Performance | used | $33,000 | $36,226* | 45,913 | 300k/250k | $0.143 | $0.178 |
| 2026 Tesla Model Y Standard | new | $39,990 | $44,707* | 0 | 300k/250k | $0.149 | $0.179 |
| 2020 Land Rover Range Rover Evoque Se | used | $19,200 | $21,397* | 58,709 | 200k/150k | $0.151 | $0.234 |
| 2016 Volvo XC90 T6 Momentum | used | $17,650 | $19,732* | 71,188 | 200k/150k | $0.153 | $0.250 |
| 2026 Tesla Model Y Long Range RWD | new | $44,990 | $50,079* | 0 | 300k/250k | $0.167 | $0.200 |
| 2023 Ford Mustang Mach-E Gt Performance Edition | used | $31,750 | $34,882* | 49,032 | 250k/200k | $0.174 | $0.231 |
| 2026 Tesla Model Y Long Range AWD | new | $48,990 | $54,377* | 0 | 300k/250k | $0.181 | $0.218 |
| 2020 Chevrolet Silverado Rst | used | $28,750 | $31,659* | 89,920 | 250k/200k | $0.198 | $0.288 |
| 2022 Mercedes-Benz Gle 350 | used | $29,999 | $33,001* | 48,314 | 200k/150k | $0.218 | $0.325 |
| 2026 Kia Niro EV Wind | new | $41,195 | $45,031* | 0 | 200k/150k | $0.225 | $0.300 |
| 2020 Gmc Sierra AT4 Carbon Pro | used | $32,950 | $36,172* | 91,652 | 250k/200k | $0.228 | $0.334 |
| 2023 Audi Q7 Quattro Premium Plus | used | $41,500 | $45,359* | 11,947 | 200k/150k | $0.241 | $0.329 |
| 2020 Land Rover Range Rover Sport | used | $25,299 | $27,951* | 86,317 | 200k/150k | $0.246 | $0.439 |
| 2020 Land Rover Range Rover Hse | used | $28,690 | $31,594* | 74,248 | 200k/150k | $0.251 | $0.417 |

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

Current best value: **2016 Volkswagen Beetle 1.8T S, Wolfsburg Edition, Fleet Edition,Classic** at $8,826 out the door /
112,561 mi → $0.101 per expected remaining mile
($0.236 conservative).
