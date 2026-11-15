#!/usr/bin/env python3
"""Validate actual UDP delivery at 49m, 50m and 51m from scalar results."""
from __future__ import annotations
import argparse
import json
import shlex
import sys
from pathlib import Path

def read_scalars(path: Path):
    values = {}
    with path.open(encoding="utf-8") as f:
        for line_no,line in enumerate(f,1):
            if not line.startswith("scalar "):
                continue
            p=shlex.split(line)
            if len(p)!=4:
                raise ValueError(f"{path}:{line_no}: malformed scalar")
            values[(p[1],p[2])] = float(p[3])
    return values

def validate(path: Path, distance_m: int, expected_delivered: int):
    values=read_scalars(path)
    source=("FarmNetwork.sensor[0].app[0]","packetSent:count")
    sink=("FarmNetwork.sink.app[0]","packetReceived:count")
    if source not in values or sink not in values:
        raise ValueError("missing sensor[0] sent or sink received scalar")
    sent=int(values[source])
    received=int(values[sink])
    if sent!=1:
        raise ValueError(f"expected one packet generated at {distance_m}m, got {sent}")
    if received!=expected_delivered:
        raise ValueError(f"at {distance_m}m expected {expected_delivered} delivered packet(s), got {received}")
    return {"source_file":str(path),"distance_m":distance_m,
            "generated_packets":sent,"delivered_packets":received,
            "packet_delivery_ratio_percent":100.0*received/sent,
            "expected_result":"received" if expected_delivered else "blocked",
            "status":"PASS"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("scalar_file",type=Path)
    p.add_argument("--distance",type=int,choices=[49,50,51],required=True)
    p.add_argument("--expected-delivered",type=int,choices=[0,1],required=True)
    p.add_argument("--output",type=Path,default=None)
    a=p.parse_args()
    try:
        result=validate(a.scalar_file,a.distance,a.expected_delivered)
        data=json.dumps(result,indent=2)
        print(data)
        if a.output:
            a.output.parent.mkdir(parents=True,exist_ok=True)
            a.output.write_text(data+"\n",encoding="utf-8")
    except (OSError,ValueError) as e:
        print("FAIL:",e,file=sys.stderr)
        raise SystemExit(1) from e

if __name__=="__main__":
    main()
