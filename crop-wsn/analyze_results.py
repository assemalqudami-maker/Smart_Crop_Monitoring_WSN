#!/usr/bin/env python3
"""Summarize REAL INET .sca scalars. Never estimate missing performance data."""
import argparse
import json
import math
import re
import shlex
import sys
from pathlib import Path
SRC_RE = re.compile(r"\.sensor\[(\d+)\]\.app\[0\]$")
SINK_RE = re.compile(r"\.sink\.app\[0\]$")

def load(path):
    scalars = []
    stats = []
    current = None
    with path.open(encoding="utf-8") as f:
        for ln in f:
            if ln.startswith("scalar "):
                parts = shlex.split(ln)
                if len(parts) >= 4:
                    try: v = float(parts[3])
                    except ValueError: continue
                    scalars.append((parts[1],parts[2],v))
            elif ln.startswith("statistic "):
                parts = shlex.split(ln)
                current = {"module":parts[1], "name":parts[2], "fields":{}}
                stats.append(current)
            elif ln.startswith("field ") and current:
                parts = shlex.split(ln)
                if len(parts) >= 3:
                    try: current["fields"][parts[1]] = float(parts[2])
                    except ValueError: pass
            elif ln and not ln.startswith("field "):
                current = None
    return scalars,stats

def analyze(path):
    scalars,stats=load(path)
    sent={int(m.group(1)):v for mod,name,v in scalars if name=="packetSent:count" and (m:=SRC_RE.search(mod))}
    got=[v for mod,name,v in scalars if name=="packetReceived:count" and SINK_RE.search(mod)]
    if set(sent)!=set(range(12)):
        raise ValueError(f"{path}: expected sent-count scalars for 12 nodes; received {sorted(sent)}")
    if len(got)!=1:
        raise ValueError(f"{path}: expected one sink received count; got {got}")
    generated=sum(sent.values())
    if generated<=0: raise ValueError("zero generated packets")
    delivered=got[0]
    if not (0<=delivered<=generated): raise ValueError("invalid delivered packet count")
    delays=[x for x in stats if x["name"]=="endToEndDelay" and SINK_RE.search(x["module"])]
    delay_ms=None
    if len(delays)==1 and "mean" in delays[0]["fields"] and delays[0]["fields"].get("count",0)>0:
        delay_ms=1000*delays[0]["fields"]["mean"]
    energy=[{"module":mod,"value":val} for mod,name,val in scalars if name=="residualEnergyCapacity:last" and (".sensor[" in mod or ".sink." in mod)]
    return {
        "raw_file": str(path), "generated_packets": generated, "delivered_packets":delivered,
        "packet_delivery_ratio_percent": 100*delivered/generated,
        "average_delay_ms":delay_ms,
        "energy_capacity_last_joules":energy,
        "energy_consumption_total_joules":None,
        "notes": "Energy consumption needs validated subtraction from initial capacities; not inferred from capacity-last alone."
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("scalar_file",type=Path)
    a=p.parse_args()
    try:
        result=analyze(a.scalar_file)
        print(json.dumps(result,indent=2))
        if result["delivered_packets"]<=0:
            raise ValueError("No crop telemetry packets reached sink")
    except (ValueError,OSError) as e:
        print("FAIL:", e,file=sys.stderr)
        sys.exit(1)
