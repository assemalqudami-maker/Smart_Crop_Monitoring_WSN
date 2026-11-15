#!/usr/bin/env python3
"""Verify the 12+1 farm layout and all 50-m directed next-hop links.

These are static consistency checks, NOT RF or packet-delivery measurements.
"""
import configparser
import csv
import re
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MAX_RANGE = 50.0

def verify_simulator_configuration():
    ini = configparser.ConfigParser(interpolation=None)
    ini.optionxform = str
    if not ini.read(ROOT / "omnetpp.ini", encoding="utf-8"):
        raise AssertionError("Missing OMNeT++ INI")
    general = ini["General"]
    assert general["network"] == "wsn.crop.FarmNetwork"
    assert general["*.sensor[*].app[0].sendInterval"] == "300s", "5-minute sensing period changed"
    assert general["*.radioMedium.mediumLimitCache.maxCommunicationRange"] == "50m", "communication bound changed"
    assert general["*.sensor[*].forwarding"] == "true", "relay forwarding disabled"
    assert general["*.sensor[*].numApps"] == "1"
    assert general["*.sink.numApps"] == "1"
    ned = (ROOT / "FarmNetwork.ned").read_text(encoding="utf-8")
    assert re.search(r"\bsensor\[12\]\s*:\s*SensorNode", ned), "network must have 12 sensors"
    assert re.search(r"\bsink\s*:\s*SensorNode", ned), "sink module missing"
    print("PASS: NED count and INI traffic, forwarding and 50m cap agree")
    return ini


def main():
    ini = verify_simulator_configuration()
    with (ROOT / "topology.csv").open(newline="", encoding="utf-8") as fp:
        rows = list(csv.DictReader(fp))
    if len(rows) != 26:
        raise AssertionError(f"Expected 13 nodes x 2 scenarios, found {len(rows)} rows")
    paths = {}
    for scenario, xmlfile in (("Initial", "routes-initial.xml"), ("Optimized", "routes-optimized.xml")):
        scoped = {r["node"]: r for r in rows if r["scenario"] == scenario}
        section = ini[f"Config {scenario}"]
        for idx in range(12):
            expected = scoped[f"sensor[{idx}]"]
            for axis, col in (("X", "x_m"), ("Y", "y_m")):
                actual = section[f"*.sensor[{idx}].mobility.initial{axis}"]
                if actual != f"{expected[col]}m":
                    raise AssertionError(f"{scenario}: sensor[{idx}] coordinate {axis} mismatch: {actual}")
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
