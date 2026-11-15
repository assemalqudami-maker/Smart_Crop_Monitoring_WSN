#!/usr/bin/env python3
"""Inspect historical 30-second radio evidence; NEVER use its energy for final report.

This script is diagnostic only: the archived INET run used ideal battery storage
and a single sampling interval, so it is not the final experiment.
"""
import argparse
from pathlib import Path
from analyze_results import load

def main():
    p=argparse.ArgumentParser()
    p.add_argument("file",type=Path)
    a=p.parse_args()
    scalars,stats=load(a.file)
    sent={}
    sink=None
    for module,name,value in scalars:
        if module.endswith(".app[0]") and ".sensor[" in module and name=="packetSent:count":
            sent[module]=int(value)
        if module.endswith(".sink.app[0]") and name=="packetReceived:count":
            sink=int(value)
    total=sum(sent.values())
    delay=[x["fields"] for x in stats if x["module"].endswith(".sink.app[0]") and x["name"].startswith("endToEndDelay")]
    forward=[(m,n,v) for m,n,v in scalars if ".sensor[" in m and ("forward" in n.lower() or "forward" in m.lower() or "passedup" in n.lower() or "passeddown" in n.lower())]
    print("EVIDENCE: actual previous 30-second radio run, NOT final comparison")
    print("Source node count:",len(sent),"generated:",total,"sink received:",sink)
    print("Packet delivery ratio:",round(100*sink/total,4) if sink is not None and total else "unavailable")
    print("Sink delay statistics:",delay)
    mac_tx=[(m,int(v)) for m,n,v in scalars if ".sensor[" in m and ".wlan[0].mac" in m and n=="nbTxFrames"]
    mac_rx=[(m,int(v)) for m,n,v in scalars if ".sensor[" in m and ".wlan[0].mac" in m and n=="nbRxFrames"]
    print("Per-relay MAC data-frame transmissions:",mac_tx)
    print("Per-relay MAC data-frame receptions:",mac_rx)
    print("Note: frame counts may include retransmissions; packet-path proof needs dedicated trace.")
    print("Selected forwarding/relay scalar counters (first 40):")
    for m,n,v in forward[:40]: print(m,n,v)
    print("ENERGY INVALID FOR FINAL REPORT: original ideal battery model; negative residual values")
    if len(sent)!=12 or total<=0 or sink is None:
        raise SystemExit("FAIL: required counters missing")

if __name__ == "__main__":
    main()
