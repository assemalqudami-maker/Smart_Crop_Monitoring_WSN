#!/usr/bin/env python3
"""Calculate design-only path geometry for the two farm layouts.

This analyzes parent next-hop routes and XY distances from topology.csv.
It does NOT simulate packets, estimate radio quality or calculate PDR,
delay, energy consumption, 802.15.4 performance, or ZigBee performance.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENSOR_COUNT = 12
SCENARIOS = ("Initial", "Optimized")
RADIO_LINK_LIMIT_METRES = 50.0


def compute_design(path: Path = HERE / "topology.csv") -> dict:
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    report = {}
    for scenario in SCENARIOS:
        matches = [row for row in rows if row["scenario"] == scenario]
        if len(matches) != 13:
            raise ValueError(f"{scenario}: expected 12 sensors and 1 sink")
        nodes = {row["node"]: row for row in matches}
        expected = {"sink", *(f"sensor[{i}]" for i in range(SENSOR_COUNT))}
        if set(nodes) != expected:
            raise ValueError(f"{scenario}: missing or duplicated nodes")
        total_hops = 0
        cumulative_m = 0.0
        source_details = []
        for i in range(SENSOR_COUNT):
            source_name = f"sensor[{i}]"
            cur = source_name
            seen = set()
            hops, length = 0, 0.0
            path_names = [cur]
            while cur != "sink":
                if cur in seen:
                    raise ValueError(f"{scenario}: forwarding loop starting at {source_name}")
                seen.add(cur)
                point = nodes[cur]
                nxt = point["next_hop"]
                if nxt not in nodes:
                    raise ValueError(f"{scenario}: next hop {nxt} does not exist")
                to = nodes[nxt]
                d = math.hypot(float(point["x_m"])-float(to["x_m"]),
                               float(point["y_m"])-float(to["y_m"]))
                if not 0 < d <= RADIO_LINK_LIMIT_METRES:
                    raise ValueError(f"{scenario}: link {cur}->{nxt} is {d}m")
                hops += 1
                length += d
                cur = nxt
                path_names.append(cur)
                if hops > SENSOR_COUNT:
                    raise ValueError(f"{scenario}: excessive hops")
            source_details.append({"source": source_name, "hops": hops,
                                   "path_length_m": round(length, 6),
                                   "route": path_names})
            total_hops += hops
            cumulative_m += length
        report[scenario] = {
            "sensor_count": SENSOR_COUNT,
            "sink_count": 1,
            "sum_source_to_sink_hops": total_hops,
            "max_source_to_sink_hops": max(item["hops"] for item in source_details),
            "sum_source_to_sink_path_lengths_m": round(cumulative_m, 6),
            "mean_source_to_sink_path_length_m": round(cumulative_m / SENSOR_COUNT, 6),
            "sources": source_details,
        }
    old = report["Initial"]
    new = report["Optimized"]
    hop_delta = old["sum_source_to_sink_hops"] - new["sum_source_to_sink_hops"]
    distance_delta = (old["sum_source_to_sink_path_lengths_m"]
                      - new["sum_source_to_sink_path_lengths_m"])
    report["design_difference"] = {
        "total_hops_reduction": hop_delta,
        "total_hops_reduction_percent": round(100 * hop_delta / old["sum_source_to_sink_hops"], 4),
        "cumulative_path_length_reduction_m": round(distance_delta, 6),
        "cumulative_path_length_reduction_percent": round(
            100 * distance_delta / old["sum_source_to_sink_path_lengths_m"], 4),
    }
    report["interpretation"] = (
        "Static design comparison only: Euclidean path lengths and directed hop counts. "
        "Not an RF result, packet trace, energy/delay/PDR measurement, or ZigBee verification.")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topology", type=Path, default=HERE / "topology.csv")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    report = compute_design(args.topology)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
        print(f"Saved design-only topology report to {args.out}")
    else:
        print(payload)
    for scenario in SCENARIOS:
        row = report[scenario]
        print(f"PASS: {scenario}: {row['sum_source_to_sink_hops']} aggregate path hops, "
              f"{row['sum_source_to_sink_path_lengths_m']:.2f} cumulative path metres")


if __name__ == "__main__":
    main()
