#!/usr/bin/env python3
"""Compare two *measured* INET scalar files.

Missing metrics are not filled in. This program refuses to create a final
comparison table until both scenarios have real PDR, delay and energy data.
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path
from analyze_results import analyze

def compare(initial_file: Path, optimized_file: Path):
    initial = analyze(initial_file, require_energy=True)
    optimized = analyze(optimized_file, require_energy=True)
    result = []
    for key, label, unit, better in [
        ("packet_delivery_ratio_percent", "Packet Delivery Ratio", "%", "higher"),
        ("energy_consumption_total_joules", "Energy Consumption", "J", "lower"),
        ("average_delay_ms", "Average Delay", "ms", "lower"),
    ]:
        a = initial[key]
        b = optimized[key]
        if a is None or b is None:
            raise ValueError(f"missing actual {label} metric")
        absolute = (b-a) if better == "higher" else (a-b)
        relative = None if a == 0 else 100*absolute/a
        result.append({
            "Metric": label, "Unit":unit,
            "Initial Value":round(a,6), "Optimized Value":round(b,6),
            "Improvement":round(absolute,6),
            "Improvement (%)":round(relative,4) if relative is not None else None
        })
    return {
        "source_files": {"initial":str(initial_file),"optimized":str(optimized_file)},
        "comparison":result,
        "caveat":"IEEE 802.15.4 + IPv4 simulation. Not a full ZigBee stack.",
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("initial",type=Path)
    p.add_argument("optimized",type=Path)
    p.add_argument("--out",type=Path,default=Path("results/validated-comparison.csv"))
    args=p.parse_args()
    try:
        report=compare(args.initial,args.optimized)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=list(report["comparison"][0]))
            writer.writeheader()
            writer.writerows(report["comparison"])
        print(json.dumps(report,indent=2))
        print(f"PASS: measured comparison saved in {args.out}")
    except (ValueError,OSError) as exc:
        print(f"FAIL: {exc}",file=sys.stderr)
        raise SystemExit(1) from exc

if __name__=="__main__":
    main()
