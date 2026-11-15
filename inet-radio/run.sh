#!/usr/bin/env bash
set -euo pipefail

# Run inside a *Linux container that already includes OMNeT++ 6.3.0*.
# This verifies the upstream IEEE 802.15.4 example (NOT complete ZigBee).
UPSTREAM_DIR="${UPSTREAM_DIR:-/tmp/inet-wsn-upstream}"
RESULT_DIR="${RESULT_DIR:-/root/models/inet-radio/results}"

if ! command -v opp_makemake >/dev/null 2>&1; then
  echo "ERROR: OMNeT++ is not on PATH" >&2
  exit 2
fi

if [[ ! -d "$UPSTREAM_DIR/.git" ]]; then
  git clone --depth 1 --branch v4.6.0 https://github.com/inet-framework/inet.git "$UPSTREAM_DIR"
fi
cd "$UPSTREAM_DIR"
source setenv -q
make MODE=release -j2

mkdir -p "$RESULT_DIR"
cd showcases/wireless/ieee802154
inet --release \
  -u Cmdenv \
  -c Ieee802154Power \
  -f omnetpp.ini \
  --sim-time-limit=15s \
  --output-scalar-file="$RESULT_DIR/upstream-802154.sca" \
  --output-vector-file="$RESULT_DIR/upstream-802154.vec"

test -s "$RESULT_DIR/upstream-802154.sca"
grep -q '^scalar ' "$RESULT_DIR/upstream-802154.sca"
echo "PASS: upstream INET IEEE 802.15.4 example ran and produced scalar data"
echo "NOTE: this does not prove 50m range, multi-hop or complete ZigBee"
