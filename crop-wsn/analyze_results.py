#!/usr/bin/env python3
"""Extract measured INET scalar statistics (never invent missing measurements).

Model: twelve UdpBasicApp sensors -> one UdpSink; per-node finite-energy storage.
Energy consumption is computed only when *all 13 actual residual energy readings*
are present, using the explicitly configured 1000 J initial capacity.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shlex
import sys
from pathlib import Path

SRC_RE = re.compile(r"\.sensor\[(\d+)\]\.app\[0\]$")
SINK_RE = re.compile(r"\.sink\.app\[0\]$")
NODE_ENERGY_RE = re.compile(r"\.(sensor\[(\d+)\]|sink)\.energyStorage$")
N = 12
INITIAL_J = 1000.0


def load(path: Path):
    scalars = []
    stats = []
    current = None
    with path.open(encoding="utf-8") as source:
        for number, line in enumerate(source, 1):
            if line.startswith("scalar "):
                parts = shlex.split(line)
                if len(parts) != 4:
                    raise ValueError(f"{path}:{number}: malformed scalar")
                try:
                    val = float(parts[3])
                except ValueError as exc:
                    raise ValueError(f"{path}:{number}: nonnumeric scalar") from exc
                if not math.isfinite(val):
                    raise ValueError(f"{path}:{number}: nonfinite scalar")
                scalars.append((parts[1], parts[2], val))
                current = None
            elif line.startswith("statistic "):
                parts = shlex.split(line)
                if len(parts) < 3:
                    raise ValueError(f"{path}:{number}: malformed statistic")
                current = {"module": parts[1], "name": parts[2], "fields": {}}
                stats.append(current)
            elif line.startswith("field ") and current is not None:
                parts = shlex.split(line)
                if len(parts) >= 3:
                    try:
                        value = float(parts[2])
                        if math.isfinite(value):
                            current["fields"][parts[1]] = value
                    except ValueError:
                        pass
            elif line.strip() and not line.startswith(("bin ", "attr ")):
                current = None
    return scalars, stats


def analyze(path: Path, *, require_energy: bool = False):
    scalars, stats = load(path)
    sent = {}
    delivered_counts = []
    capacities = {}
    for module, name, value in scalars:
        source = SRC_RE.search(module)
        if source and name == "packetSent:count":
            node = int(source.group(1))
            if node in sent:
                raise ValueError(f"duplicate send counter for node {node}")
            sent[node] = value
        if SINK_RE.search(module) and name == "packetReceived:count":
            delivered_counts.append(value)
        energy_node = NODE_ENERGY_RE.search(module)
        if energy_node and name == "residualEnergyCapacity:last":
            node_name = energy_node.group(1)
            if node_name in capacities:
                raise ValueError(f"duplicate residual energy for {node_name}")
            capacities[node_name] = value

    if set(sent) != set(range(N)):
        raise ValueError(f"expected sent-count scalars for 12 nodes; received {sorted(sent)}")
    if len(delivered_counts) != 1:
        raise ValueError(f"expected one sink received count; found {delivered_counts}")
    if any(int(x) != x or x < 0 for x in list(sent.values()) + delivered_counts):
        raise ValueError("packet counters must be nonnegative integers")

    generated = int(sum(sent.values()))
    delivered = int(delivered_counts[0])
    if generated <= 0:
        raise ValueError("zero generated packets")
    if delivered > generated:
        raise ValueError("invalid delivered packet count")

    delay_stats = [
        row for row in stats
        if SINK_RE.search(row["module"]) and row["name"].split(":")[0] == "endToEndDelay"
    ]
    delay_ms = None
    if delivered > 0:
        if len(delay_stats) != 1:
            raise ValueError("missing or duplicate sink delay histogram")
        fields = delay_stats[0]["fields"]
        if int(fields.get("count", -1)) != delivered or "mean" not in fields:
            raise ValueError("sink delay histogram count/mean missing or inconsistent")
        delay_ms = 1000.0 * fields["mean"]
        if not math.isfinite(delay_ms) or delay_ms < 0:
            raise ValueError("invalid sink end-to-end delay")

    expected_nodes = {"sink"} | {f"sensor[{i}]" for i in range(N)}
    energy_consumed_j = None
    sensor_energy_j = None
    sink_energy_j = None
    if capacities:
        if set(capacities) != expected_nodes:
            raise ValueError(f"incomplete energy readings: {sorted(expected_nodes - set(capacities))}")
        if any(value < -1e-6 or value > INITIAL_J + 1e-6 for value in capacities.values()):
            raise ValueError("residual energy lies outside configured capacity")
        per_node = {node: max(0.0, INITIAL_J - residual) for node, residual in capacities.items()}
        sensor_energy_j = sum(v for k, v in per_node.items() if k != "sink")
        sink_energy_j = per_node["sink"]
        energy_consumed_j = sensor_energy_j + sink_energy_j
    elif require_energy:
        raise ValueError("energy recordings absent; cannot report energy consumption")

    return {
        "source_file": str(path),
        "sensors": N,
        "generated_packets": generated,
        "generated_packets_per_sensor": {f"sensor[{i}]": int(sent[i]) for i in range(N)},
        "delivered_packets": delivered,
        "packet_delivery_ratio_percent": 100 * delivered / generated,
        "average_delay_ms": delay_ms,
        "energy_consumption_total_joules": energy_consumed_j,
        "energy_consumption_sensors_joules": sensor_energy_j,
        "energy_consumption_sink_joules": sink_energy_j,
        "energy_initial_capacity_per_node_joules": INITIAL_J,
        "radio_stack": "INET IEEE 802.15.4 narrowband PHY/MAC + manually routed IPv4 (not full ZigBee)",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scalar_file", type=Path)
    parser.add_argument("--require-energy", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    try:
        result = analyze(args.scalar_file, require_energy=args.require_energy)
        if result["delivered_packets"] <= 0:
            raise ValueError("No crop telemetry packets reached sink")
        payload = json.dumps(result, indent=2, ensure_ascii=False)
        print(payload)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
