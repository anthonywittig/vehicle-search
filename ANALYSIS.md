# Cost per expected remaining mile

Data captured **2026-08-11** · 22 vehicles · sorted best value first.
Regenerate with `python3 analyze.py --write` after updating `data/listings.json`.

## Method

Assume a total service life of 300,000 miles (with a conservative
250,000-mile alternative), subtract the odometer to get expected
remaining miles, and divide the asking price by that. This compares
purchase prices across mileages; it is not a total-cost-of-ownership
model (no financing, insurance, energy, or maintenance).

## Results

| Vehicle | Condition | Price | Odometer | Remaining (of 300k) | $/mi @300k | $/mi @250k |
|---|---|---|---|---|---|---|
| 2022 Kia Niro EV S, Ex | used | $15,850 | 59,715 | 240,285 | $0.066 | $0.083 |
| 2019 Tesla Model 3 Long Range | used | $17,490 | 94,003 | 205,997 | $0.085 | $0.112 |
| 2018 Tesla Model 3 Long Range | used | $17,250 | 110,728 | 189,272 | $0.091 | $0.124 |
| 2019 Tesla Model 3 Long Range | used | $21,250 | 83,776 | 216,224 | $0.098 | $0.128 |
| 2020 Tesla Model 3 Long Range | used | $18,750 | 111,513 | 188,487 | $0.099 | $0.135 |
| 2020 Tesla Model 3 Long Range | used | $23,250 | 68,659 | 231,341 | $0.101 | $0.128 |
| 2022 Tesla Model 3 Long Range | used | $23,500 | 81,906 | 218,094 | $0.108 | $0.140 |
| 2020 Tesla Model Y Long Range | used | $25,690 | 71,542 | 228,458 | $0.112 | $0.144 |
| 2022 Tesla Model Y Long Range | used | $25,895 | 76,504 | 223,496 | $0.116 | $0.149 |
| 2016 Tesla Model X P90D P90D | used | $22,995 | 102,130 | 197,870 | $0.116 | $0.156 |
| 2024 Tesla Model 3 Long Range | used | $30,590 | 36,957 | 263,043 | $0.116 | $0.144 |
| 2023 Tesla Model 3 Long Range (Dual Motor) | used | $30,950 | 36,308 | 263,692 | $0.117 | $0.145 |
| 2021 Tesla Model Y Long Range | used | $27,980 | 65,717 | 234,283 | $0.119 | $0.152 |
| 2023 Tesla Model 3 Performance | used | $30,250 | 58,353 | 241,647 | $0.125 | $0.158 |
| 2022 Tesla Model Y Performance | used | $31,750 | 50,714 | 249,286 | $0.127 | $0.159 |
| 2023 Tesla Model Y Performance | used | $33,000 | 45,913 | 254,087 | $0.130 | $0.162 |
| 2019 Tesla Model S Performance | used | $36,490 | 22,880 | 277,120 | $0.132 | $0.161 |
| 2026 Tesla Model Y Standard | new | $39,990 | 0 | 300,000 | $0.133 | $0.160 |
| 2026 Kia Niro EV Wind | new | $41,195 | 0 | 300,000 | $0.137 | $0.165 |
| 2020 Tesla Model X Long Range | used | $29,568 | 95,967 | 204,033 | $0.145 | $0.192 |
| 2026 Tesla Model Y Long Range RWD | new | $44,990 | 0 | 300,000 | $0.150 | $0.180 |
| 2026 Tesla Model Y Long Range AWD | new | $48,990 | 0 | 300,000 | $0.163 | $0.196 |

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

Current best value: **2022 Kia Niro EV S, Ex** at $15,850 /
59,715 mi → $0.066 per expected remaining mile.
