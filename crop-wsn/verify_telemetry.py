#!/usr/bin/env python3
"""Validate decoded binary crop telemetry in actual INET scalar output."""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path
from analyze_results import load

N = 12
SINK = "FarmNetwork.sink.app[0]"

def validate(path: Path, expected_per_sensor: int):
    scalars, _ = load(path)
    values = {}
    for module, name, value in scalars:
        key = (module, name)
        if key in values:
            raise ValueError(f"duplicate scalar {key}")
        values[key] = value

    def get(module, name):
        key = (module, name)
        if key not in values:
            raise ValueError(f"missing telemetry scalar {key}")
        return values[key]

    sensors = []
    for i in range(N):
        module = f"FarmNetwork.sensor[{i}].app[0]"
        sent = get(module, "packetSent:count")
        if sent != expected_per_sensor:
            raise ValueError(f"sensor[{i}] generated {sent}; expected {expected_per_sensor}")
        prefix = f"sensor{i}"
        count = get(SINK, prefix + "DecodedPackets")
        if count != expected_per_sensor:
            raise ValueError(f"sensor[{i}] decoded {count}; expected {expected_per_sensor}")
        row = {"sensor_id": i, "decoded_packets": int(count)}
        for field, scalar, low, high in (
            ("mean_temperature_c", "MeanTemperatureC", -20, 80),
            ("mean_relative_humidity_pct", "MeanRelativeHumidityPct", 0, 100),
            ("mean_soil_moisture_pct", "MeanSoilMoisturePct", 0, 100),
        ):
            value = get(SINK, prefix + scalar)
            if not math.isfinite(value) or value < low or value > high:
                raise ValueError(f"sensor[{i}] {field} outside sanity bounds: {value}")
            row[field] = value
        sensors.append(row)

    total = N * expected_per_sensor
    received = get(SINK, "packetReceived:count")
    decoded = get(SINK, "decodedTelemetryPackets")
    if received != total or decoded != total:
        raise ValueError(f"sink counters mismatch: UDP={received}, decoded={decoded}, expected={total}")

    means = {}
    for field, scalar, low, high in (
        ("mean_temperature_c", "meanTemperatureC", -20, 80),
        ("mean_relative_humidity_pct", "meanRelativeHumidityPct", 0, 100),
        ("mean_soil_moisture_pct", "meanSoilMoisturePct", 0, 100),
    ):
        value = get(SINK, scalar)
        if not math.isfinite(value) or value < low or value > high:
            raise ValueError(f"sink {field} outside sanity bounds: {value}")
        means[field] = value

    return {"source_file":str(path),"synthetic_measurements":True,
            "payload_format":"versioned binary, 13 bytes",
            "expected_packets_per_sensor":expected_per_sensor,
            "generated_packets":total,"udp_packets_received":int(received),
            "telemetry_packets_decoded":int(decoded),
            "sink_mean_values":means,"per_sensor":sensors}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("scalar_file",type=Path)
    p.add_argument("--expected-per-sensor",type=int,default=4)
    p.add_argument("--output",type=Path,default=None)
    a=p.parse_args()
    try:
        result=validate(a.scalar_file,a.expected_per_sensor)
        payload=json.dumps(result,indent=2,ensure_ascii=False)
        print(payload)
        if a.output:
            a.output.parent.mkdir(parents=True,exist_ok=True)
            a.output.write_text(payload+"\n",encoding="utf-8")
    except (OSError,ValueError) as e:
        print("FAIL:",e,file=sys.stderr)
        raise SystemExit(1) from e

if __name__=="__main__":
    main()
