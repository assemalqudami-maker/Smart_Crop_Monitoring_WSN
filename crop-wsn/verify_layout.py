#!/usr/bin/env python3
"""Verify the 12+1 farm layout and all 50-m directed next-hop links.

These are static consistency checks, NOT RF or packet-delivery measurements.
"""
import csv
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAX_RANGE = 50.0

def main():
    with (ROOT / "topology.csv").open(newline="", encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    if len(rows) != 26:
        raise AssertionError(f"Expected 13 nodes x 2 scenarios, found {len(rows)} rows")
    paths = {}
    for scenario, xmlfile in (("Initial", "routes-initial.xml"), ("Optimized", "routes-optimized.xml")):
        scoped = {r["node"]: r for r in rows if r["scenario"] == scenario}
        sensors = {f"sensor[{i}]" for i in range(12)}
        if set(scoped) != sensors | {"sink"}:
            raise AssertionError(f"{scenario}: missing/duplicate sensor or sink nodes")
        xml = ET.parse(ROOT / xmlfile).getroot()
        routes = xml.findall("route")
        if len(routes) != 12:
            raise AssertionError(f"{scenario}: requires 12 explicit sink routes")
        by_src = {r.attrib["hosts"]: r for r in routes}
        if set(by_src) != sensors:
            raise AssertionError(f"{scenario}: route hosts mismatch")
        max_hops = 0
        for src in sorted(sensors):
            hops = 0
            cur = src
            seen = set()
            while cur != "sink":
                if cur in seen:
                    raise AssertionError(f"{scenario}: routing loop from {src}")
                seen.add(cur)
                nxt = scoped[cur]["next_hop"]
                if nxt not in scoped:
                    raise AssertionError(f"{scenario}: invalid next hop for {cur}: {nxt}")
                p = scoped[cur]
                q = scoped[nxt]
                dist = math.hypot(float(p["x_m"])-float(q["x_m"]), float(p["y_m"])-float(q["y_m"]))
                if not 0 < dist <= MAX_RANGE:
                    raise AssertionError(f"{scenario}: {cur} -> {nxt} is {dist:.2f}m; limit 50m")
                expected_gateway = "*" if nxt == "sink" else f"10.0.0.{int(nxt.split('[')[1][:-1])+2}"
                if by_src[cur].attrib["gateway"] != expected_gateway:
                    raise AssertionError(f"{scenario}: {cur} XML gateway mismatch")
                cur = nxt
                hops += 1
                if hops > 12:
                    raise AssertionError(f"{scenario}: excessive path length for {src}")
            max_hops = max(max_hops, hops)
        paths[scenario] = max_hops
        print(f"PASS {scenario}: 12 nodes, one sink, all next-hop links <= 50m; max hops={max_hops}")
    if not (paths["Initial"] >= 2 and paths["Optimized"] >= 2):
        raise AssertionError("Both scenarios must genuinely have multi-hop routes")
    print("PASS: static layout and routing consistency only")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, AssertionError, ET.ParseError) as exc:
        print("FAIL:", exc, file=sys.stderr)
        sys.exit(1)
