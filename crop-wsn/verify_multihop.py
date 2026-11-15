#!/usr/bin/env python3
"""Check observed per-node IEEE 802.15.4 MAC frame flow against routing tree.

A strict passing check proves the *aggregate* traffic carried by each relay
matches routing-tree predictions without MAC-level retransmissions. It does
not identify each packet's route individually, nor certify a ZigBee NWK stack.
"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path
from analyze_results import load

HERE = Path(__file__).resolve().parent
N = 12

def expected_flow(topology_path: Path, scenario: str, generated: dict[str, int]):
    with topology_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    parents = {r["node"]: r["next_hop"] for r in rows if r["scenario"] == scenario}
    nodes = {f"sensor[{i}]" for i in range(N)}
    if set(parents) != nodes | {"sink"}:
        raise ValueError(f"{scenario}: topology missing nodes")
    tx = {node: 0 for node in nodes}
    rx = {node: 0 for node in nodes | {"sink"}}
    if set(generated) != nodes:
        raise ValueError("must provide generated packets from all 12 sensors")
    for source, sent in generated.items():
        current = source
        seen = set()
        while current != "sink":
            if current in seen:
                raise ValueError(f"routing loop from {source}")
            seen.add(current)
            nxt = parents[current]
            if nxt not in rx:
                raise ValueError(f"invalid next-hop: {nxt}")
            tx[current] += sent
            rx[nxt] += sent
            current = nxt
    return tx,rx

def validate_trace(path: Path, scenario: str = "Initial"):
    scalar_list, _ = load(path)
    values = {}
    for module, name, raw_value in scalar_list:
        if name in ("packetSent:count","packetReceived:count") or name.startswith("nb"):
            if (module,name) in values:
                raise ValueError(f"duplicate scalar: {module}.{name}")
            if raw_value < 0 or int(raw_value) != raw_value:
                raise ValueError(f"invalid integer counter: {module}.{name}")
            values[module,name] = int(raw_value)
    def get(mod,name):
        key=(f"FarmNetwork.{mod}",name)
        if key not in values:
            raise ValueError(f"missing real scalar {key}")
        return values[key]
    generated = {f"sensor[{i}]":get(f"sensor[{i}].app[0]","packetSent:count") for i in range(N)}
    delivered = get("sink.app[0]","packetReceived:count")
    expected_tx, expected_rx = expected_flow(HERE/"topology.csv",scenario,generated)

    if not any(expected_tx[node] > generated[node] for node in generated):
        raise ValueError("no multi-hop relay predicted by topology")

    actual_tx={}
    actual_rx={}
    for node in generated:
        actual_tx[node]=get(f"{node}.wlan[0].mac","nbTxFrames")
        actual_rx[node]=get(f"{node}.wlan[0].mac","nbRxFrames")
        if actual_tx[node]!=expected_tx[node] or actual_rx[node]!=expected_rx[node]:
            raise ValueError(f"{node}: expected MAC TX/RX {expected_tx[node]}/{expected_rx[node]}, "
                             f"observed {actual_tx[node]}/{actual_rx[node]}")
        for field in ("nbMissedAcks","nbDroppedFrames"):
            drop=get(f"{node}.wlan[0].mac",field)
            if drop:
                raise ValueError(f"{node}: {field}={drop}; strict no-retry evidence invalid")
    sink_rx=get("sink.wlan[0].mac","nbRxFrames")
    if sink_rx != expected_rx["sink"] or sink_rx != delivered:
        raise ValueError(f"sink: expected {expected_rx['sink']} MAC RX/app deliveries, "
                         f"observed MAC={sink_rx} app={delivered}")

    if delivered!=sum(generated.values()):
        raise ValueError("strict path validation requires 100% app delivery")
    return {
        "experiment_scalar_file":str(path),
        "scenario":scenario,
        "generated":sum(generated.values()),
        "delivered":delivered,
        "sink_mac_rx":sink_rx,
        "per_sensor": [
            {"node":node,"generated":generated[node],"mac_tx":actual_tx[node],
             "mac_rx":actual_rx[node],"relay_frames_tx_over_own_app":actual_tx[node]-generated[node]}
            for node in sorted(generated,key=lambda s:int(s[7:-1]))
        ],
        "evidence":"Aggregate MAC TX/RX counts match exact tree forwarding without observed missed ACKs/dropped frames.",
        "limitation":"Not per-packet path traces, distance proof, or full ZigBee NWK implementation.",
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scalar_file",type=Path)
    parser.add_argument("--scenario",default="Initial",choices=["Initial","Optimized"])
    parser.add_argument("--output",type=Path,default=None)
    args=parser.parse_args()
    try:
        report=validate_trace(args.scalar_file,args.scenario)
        payload=json.dumps(report,indent=2)
        print(payload)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(payload+"\\n",encoding="utf-8")
        print(f"PASS: measured aggregate multi-hop forwarding for {args.scenario}")
    except (ValueError,OSError) as exc:
        print("FAIL:",exc,file=sys.stderr)
        raise SystemExit(1) from exc

if __name__=="__main__":
    main()
