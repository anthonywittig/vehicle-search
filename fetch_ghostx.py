#!/usr/bin/env python3
"""Refresh GhostX Automotive listings in data/listings.json.

GhostX (ghostxauto.com, powered by Keysy) renders client-side and talks to
a tRPC API at /api/trpc. This script queries `listings.list`, replaces the
GhostX-sourced entries in data/listings.json with the fresh results, and
leaves entries from other sources (e.g. new-car MSRP benchmarks) untouched.

Usage:
    python3 fetch_ghostx.py                 # refresh Tesla (make 48) + Kia (make 25?) — see MAKE_IDS
    python3 fetch_ghostx.py --make-id 48    # refresh a single make
    python3 fetch_ghostx.py --all           # fetch with no make filter (server may page results)

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

# Make IDs observed on GhostX. Add more as the search widens.
MAKE_IDS = {"Tesla": 48}


def fetch(make_id=None):
    filters = {"makeIds": [make_id]} if make_id is not None else {}
    query = urllib.parse.quote(json.dumps({"json": {"filters": filters}}))
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
    parser.add_argument("--make-id", type=int, help="refresh a single GhostX make id")
    parser.add_argument(
        "--all", action="store_true", help="fetch with no make filter"
    )
    args = parser.parse_args()

    if args.all:
        raw = fetch()
    elif args.make_id is not None:
        raw = fetch(args.make_id)
    else:
        raw, seen = [], set()
        for make_id in MAKE_IDS.values():
            for v in fetch(make_id):
                if v["id"] not in seen:
                    seen.add(v["id"])
                    raw.append(v)
        # The Niro isn't reachable via the Tesla make filter; grab it from
        # the unfiltered list too.
        for v in fetch():
            if v["id"] not in seen and "niro" in (v.get("searchField") or ""):
                seen.add(v["id"])
                raw.append(v)

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

    # Refresh fee schedules for every dealer in the fresh listings,
    # keeping any location info already recorded.
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
    print(
        f"Refreshed {len(fresh)} GhostX listings "
        f"(+{len(kept)} entries from other sources kept). "
        f"Now run: python3 analyze.py --write"
    )


if __name__ == "__main__":
    main()
