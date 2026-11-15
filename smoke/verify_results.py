#!/usr/bin/env python3
"""Fail CI unless the real OMNeT++ smoke-run scalar data are complete and correct.

This only verifies a directly wired framework smoke test. It is NOT a radio,
IEEE 802.15.4, or ZigBee validation.
"""

from __future__ import annotations

import argparse
import math
import re
import shlex
import sys
from pathlib import Path

SENSOR_PATTERN = re.compile(r"^SmokeNetwork\.sensor\[([0-2])\]$")
SINK_MODULE = "SmokeNetwork.sink"
EXPECTED_PER_SENSOR = 10  # t=1,2,...,10s; simulation ends at t=10.5s


def load_scalars(path: Path) -> dict[tuple[str, str], float]:
    scalars: dict[tuple[str, str], float] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("scalar "):
            continue
        fields = shlex.split(line)
        if len(fields) < 4:
            raise ValueError(f"{path}:{number}: invalid scalar record")
        _, module, name, raw_value = fields[:4]
        key = (module, name)
        if key in scalars:
            raise ValueError(f"{path}:{number}: duplicate scalar: {key}")
        value = float(raw_value)
        if not math.isfinite(value):
            raise ValueError(f"{path}:{number}: non-finite scalar: {key}")
        scalars[key] = value
    return scalars


def validate(results_dir: Path) -> None:
    results = sorted(results_dir.glob("*.sca"))
    if len(results) != 1:
        raise ValueError(f"Expected exactly 1 .sca file in {results_dir}, found {len(results)}")
    scalars = load_scalars(results[0])
    sensors = {}
    for (module, name), value in scalars.items():
        match = SENSOR_PATTERN.fullmatch(module)
        if match and name == "generatedPackets":
            sensors[int(match.group(1))] = value

    if set(sensors) != {0, 1, 2}:
        raise ValueError(f"Missing sensor scalars, received indices: {sorted(sensors)}")
    for node_id, generated in sensors.items():
        if generated != EXPECTED_PER_SENSOR:
            raise ValueError(f"Sensor {node_id} generated {generated} instead of {EXPECTED_PER_SENSOR}")

    sink_value = scalars.get((SINK_MODULE, "deliveredPackets"))
    if sink_value is None:
        raise ValueError(f"Missing {SINK_MODULE}.deliveredPackets")

    generated = sum(sensors.values())
    if sink_value != generated:
        raise ValueError(f"Sink received {sink_value} of {generated} packets")

    print(f"PASS: {len(sensors)} source nodes generated {int(generated)} packets")
    print(f"PASS: sink delivered {int(sink_value)} packets")
    print("PASS: framework smoke test only; no wireless/ZigBee validation")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_dir", type=Path)
    args = parser.parse_args()
    try:
        validate(args.result_dir)
    except (OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
