#!/usr/bin/env python3
"""
neo_ingest.py  –  Minimal NeoWs extractor for the NEO Risk Dashboard
-------------------------------------------------------------------
Usage examples
  # default: fetch yesterday and just print two sample rows
  export NASA_API_KEY=your_key_here
  python neo_ingest.py

  # fetch a specific day and save to CSV
  python neo_ingest.py 2025-05-30 output.csv

  # fetch a 3-day window (≤7 days) and save
  python neo_ingest.py 2025-05-29 2025-05-31 neos_may.csv
"""

import os
import sys
import math
import json
import csv
import datetime as dt
from typing import List, Dict

import requests

# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------
API_KEY = os.getenv("NASA_API_KEY")
if not API_KEY:
    raise RuntimeError("Set NASA_API_KEY in your environment first!")

BASE_URL = "https://api.nasa.gov/neo/rest/v1/feed"
DENSITY_KG_M3 = 3_000              # typical stony-asteroid density
J_PER_KT_TNT = 4.184e12            # joules in one kiloton of TNT

# ---------------------------------------------------------------------
# Physics helpers
# ---------------------------------------------------------------------
def sphere_mass(diameter_m: float,
                density: float = DENSITY_KG_M3) -> float:
    """Approximate mass of sphere from diameter (m) & density (kg/m³)."""
    radius = diameter_m / 2.0
    volume = (4 / 3) * math.pi * radius**3
    return volume * density


def kinetic_energy_kt(mass_kg: float,
                      velocity_km_s: float) -> float:
    """Kinetic energy (kilotons TNT) from mass (kg) & speed (km/s)."""
    joules = 0.5 * mass_kg * (velocity_km_s * 1_000) ** 2
    return joules / J_PER_KT_TNT


# ---------------------------------------------------------------------
# NeoWs fetch & parse
# ---------------------------------------------------------------------
def fetch_feed(start: str, end: str) -> dict:
    """Download NeoWs /feed JSON for start–end (<=7 days)."""
    params = {"start_date": start, "end_date": end, "api_key": API_KEY}
    r = requests.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def tidy_rows(feed_json: dict) -> List[Dict]:
    """Flatten and enrich the feed into dashboard-ready dicts."""
    rows = []
    for date_str, neos in feed_json["near_earth_objects"].items():
        for neo in neos:
            # pick the Earth close-approach record
            cad = next(c for c in neo["close_approach_data"]
                       if c["orbiting_body"] == "Earth")

            # median estimated diameter
            est = neo["estimated_diameter"]["meters"]
            diameter_m = (est["estimated_diameter_min"] +
                          est["estimated_diameter_max"]) / 2.0

            # physics
            mass_kg = sphere_mass(diameter_m)
            velocity_km_s = float(cad["relative_velocity"]
                                  ["kilometers_per_second"])
            miss_km = float(cad["miss_distance"]["kilometers"])
            ke_kt = kinetic_energy_kt(mass_kg, velocity_km_s)

            rows.append({
                "neo_id": neo["id"],
                "name": neo["name"],
                "close_approach_date": date_str,
                "miss_distance_km": miss_km,
                "relative_velocity_km_s": velocity_km_s,
                "diameter_m": diameter_m,
                "mass_kg": mass_kg,
                "kinetic_energy_kt_TNT": ke_kt,
                # placeholders for later analytics
                "palermo_proxy": None,
                "risk_cluster": None
            })
    return rows


# ---------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------
def save_csv(rows: List[Dict], path: str) -> None:
    if not rows:
        print("No data – nothing to save.")
        return
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"✓ wrote {len(rows)} rows → {path}")


# ---------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    today = dt.date.today()
    default_start = (today - dt.timedelta(days=1)).isoformat()

    # Parse CLI args
    start_date = sys.argv[1] if len(sys.argv) >= 2 else default_start

    # If only two args and the second ends with .csv, treat it as outfile
    if len(sys.argv) == 2 and start_date.endswith(".csv"):
        outfile = start_date
        start_date = default_start
        end_date = start_date
    else:
        end_date = sys.argv[2] if len(sys.argv) >= 3 else start_date
        outfile = sys.argv[3] if len(sys.argv) >= 4 else None

    # -----------------------------------------------------------------
    # Fetch & tidy
    # -----------------------------------------------------------------
    print(f"Fetching NEOs {start_date} → {end_date} …")
    feed = fetch_feed(start_date, end_date)
    data = tidy_rows(feed)
    print(f"Parsed {len(data)} objects")

    # -----------------------------------------------------------------
    # Output
    # -----------------------------------------------------------------
    if outfile:
        save_csv(data, outfile)
    else:
        print(json.dumps(data[:2], indent=2))
        print("↳ (showing first 2 rows; pass a filename to save all)")
