#!/usr/bin/env python3
"""Refresh GhostX Automotive listings in data/listings.json.

GhostX (ghostxauto.com, powered by Keysy) renders client-side and talks to
a tRPC API at /api/trpc. This script queries `listings.list` for the
dealers in DEALER_IDS (currently just dealer 83, St. George UT — the one
whose inventory we're tracking), keeps only the makes in MAKES
(Tesla and Kia), replaces the GhostX-sourced entries in
data/listings.json with the fresh results, refreshes those dealers' fee
schedules, and leaves entries from other sources (e.g. new-car MSRP
benchmarks) untouched. Notes, life_miles overrides, and fees_quoted are
carried forward for listings that survive the refresh.

Usage:
    python3 fetch_ghostx.py                  # refresh DEALER_IDS inventory
    python3 fetch_ghostx.py --dealer-id 83   # refresh a specific dealer

Only standard library is used.
"""
import argparse
import datetime
import json
import urllib.parse
import urllib.request
from pathlib import Path

DATA = Path(__file__).parent / "data" / "listings.json"
BASE = "https://www.ghostxauto.com/api/trpc/listings.list"
FEES = "https://www.ghostxauto.com/api/trpc/dealers.getFeesAndTaxes"

# The dealers whose inventory we track. 83 = St. George, UT.
DEALER_IDS = [83]

# Makes we care about; other makes at the dealer are ignored.
MAKES = {"Tesla", "Kia"}


def fetch_listings(dealer_ids):
    query = urllib.parse.quote(
        json.dumps({"json": {"filters": {"dealerIds": dealer_ids}}})
    )
    req = urllib.request.Request(
        f"{BASE}?input={query}", headers={"User-Agent": "vehicle-search/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["result"]["data"]["json"]


def fetch_dealer_fees(dealer_id):
    query = urllib.parse.quote(json.dumps({"json": {"dealerId": dealer_id}}))
    req = urllib.request.Request(
        f"{FEES}?input={query}", headers={"User-Agent": "vehicle-search/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        rows = json.load(resp)["result"]["data"]["json"]
    out = {"fees": {}, "listed_tax_rate": None}
    keymap = {"doc": "doc", "title": "title", "registration": "registration", "other": "processing"}
    for f in rows:
        if f["type"] == "tax":
            out["listed_tax_rate"] = f["value"]
        elif f["type"] in keymap:
            out["fees"][keymap[f["type"]]] = f["value"] / 100
    return out


def norm(s):
    if not s:
        return s
    return " ".join(
        w if (w.isupper() and any(c.isdigit() for c in w)) else w.title()
        for w in s.split()
    )


def entry(v):
    model = norm(v["model"])
    if model == "Niro":
        model = "Niro EV"  # GhostX lists the Niro EV as just "Niro"
    return {
        "condition": "used",
        "source": "GhostX Automotive",
        "source_url": "https://www.ghostxauto.com/inventory",
        "listing_id": v["id"],
        "dealer_id": v["dealerId"],
        "vin": v["vin"],
        "year": v["year"],
        "make": norm(v["make"]),
        "model": model,
        "trim": norm(v.get("trim") or ""),
        "price": v["price"],
        "mileage": v["mileage"],
        "status": v["status"],
        "notes": "",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dealer-id",
        type=int,
        action="append",
        help="dealer id(s) to refresh (default: DEALER_IDS in this file)",
    )
    args = parser.parse_args()
    dealer_ids = args.dealer_id or DEALER_IDS

    raw = [v for v in fetch_listings(dealer_ids) if norm(v["make"]) in MAKES]

    data = json.loads(DATA.read_text())
    kept = [v for v in data["vehicles"] if v["source"] != "GhostX Automotive"]
    fresh = [entry(v) for v in raw]

    # Carry notes, life overrides, and quoted fees forward for listings
    # that survive the refresh.
    old = {
        v["listing_id"]: v
        for v in data["vehicles"]
        if v["source"] == "GhostX Automotive"
    }
    for v in fresh:
        prev = old.get(v["listing_id"])
        if prev:
            for key in ("notes", "life_miles", "fees_quoted"):
                if prev.get(key):
                    v[key] = prev[key]

    # Refresh fee schedules for the dealers we track.
    dealers = data.setdefault("dealers", {})
    for dealer_id in sorted({v["dealer_id"] for v in fresh}):
        dealer = dealers.setdefault(str(dealer_id), {})
        try:
            dealer.update(fetch_dealer_fees(dealer_id))
        except Exception as e:
            print(f"warning: fee fetch failed for dealer {dealer_id}: {e}")

    data["vehicles"] = fresh + kept
    data["captured_at"] = datetime.date.today().isoformat()
    DATA.write_text(json.dumps(data, indent=2) + "\n")
    gone = sorted(set(old) - {v["listing_id"] for v in fresh})
    print(
        f"Refreshed {len(fresh)} GhostX listings from dealer(s) "
        f"{', '.join(map(str, dealer_ids))} "
        f"(+{len(kept)} entries from other sources kept)."
    )
    if gone:
        print(f"Dropped {len(gone)} listing(s) no longer in inventory: {gone}")
    print("Now run: python3 analyze.py --write")


if __name__ == "__main__":
    main()
