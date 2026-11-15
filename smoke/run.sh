#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v opp_makemake >/dev/null 2>&1; then
  echo "Missing opp_makemake: activate OMNeT++ with 'source setenv'." >&2
  exit 2
fi

opp_makemake -f --deep -o smoke
make -j2
mkdir -p results
./smoke -u Cmdenv -n src -f omnetpp.ini
echo "Inspect smoke/results/ for .sca files containing generatedPackets/deliveredPackets."
