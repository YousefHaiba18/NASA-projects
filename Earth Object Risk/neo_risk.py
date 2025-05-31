#!/usr/bin/env python3
"""
neo_risk.py  –  Enrich NEO CSV with quick-and-dirty risk tags
----------------------------------------------------------------
1. Read a CSV created by neo_ingest.py   (arg 1)
2. Compute:
      • palermo_proxy  – a toy placeholder
      • risk_cluster   – Low / Medium / High
3. Print a one-line summary count per cluster
4. Save to a new CSV                         (arg 2, optional)

Usage
  python neo_risk.py output.csv              # prints and rewrites in-place
  python neo_risk.py output.csv ready.csv    # writes to ready.csv instead

You can swap the toy rules for k-means or any model later.
"""

import sys
import math
import pandas as pd

# ---------------------------------------------------------------------
# Simple risk heuristics (tweak later!)
# ---------------------------------------------------------------------
KE_HIGH   = 1_000      # kilotons TNT
KE_MEDIUM =   100
MISS_NEAR =   750_000  # km   (≈ 2 lunar distances)
MISS_MID  = 5_000_000  # km

def palermo_proxy(row) -> float:
    """
    Totally made-up proxy:
        log10( (kinetic-energy / 1e3)  /  miss_distance_AU )
    where miss_distance_AU = km / 149,597,870.7
    """
    miss_au = row.miss_distance_km / 149_597_870.7
    return math.log10( (row.kinetic_energy_kt_TNT / 1_000.0) / miss_au )


def tag_cluster(row) -> str:
    if row.miss_distance_km < MISS_NEAR and row.kinetic_energy_kt_TNT > KE_HIGH:
        return "High"
    elif row.miss_distance_km < MISS_MID and row.kinetic_energy_kt_TNT > KE_MEDIUM:
        return "Medium"
    else:
        return "Low"

# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main(infile: str, outfile: str | None = None):
    df = pd.read_csv(infile)

    # Compute new columns
    df["palermo_proxy"] = df.apply(palermo_proxy, axis=1)
    df["risk_cluster"]  = df.apply(tag_cluster, axis=1)

    # Console summary
    counts = df["risk_cluster"].value_counts()
    print("Cluster counts:")
    for label, n in counts.items():
        print(f"  {label:<6}: {n}")

    # Decide output path
    out_path = outfile or infile
    df.to_csv(out_path, index=False)
    print(f"✓ enriched CSV saved → {out_path}")

# ---------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage:  python neo_risk.py input.csv  [output.csv]")
    inp  = sys.argv[1]
    outp = sys.argv[2] if len(sys.argv) >= 3 else None
    main(inp, outp)
