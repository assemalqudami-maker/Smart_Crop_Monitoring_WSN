# Crop-monitoring WSN simulation — 12 nodes + 1 sink

## Scope and stage
This repository models a farm with twelve `SensorNode` modules and a single `sink` module. Each sensor emits a 24-byte **synthetic telemetry packet** every 300 simulated seconds. Relay sensors forward to the sink via IPv4 routes configured over INET's **IEEE 802.15.4 narrowband PHY/MAC**.

> This is **not yet full ZigBee**: standard ZigBee NWK/application layers and a measurement-content payload have not been implemented. The simulator generates generic bytes named CropTelemetry; temperature, humidity and soil readings are planned features.

## Current fixed parameters
- Sensor nodes: **12**; Sink nodes: **1**
- Sensing/transmission period: **300 s**
- Maximum simulated radio-medium communication distance: **50 m** (via `rangeFilter` and `mediumLimitCache`, empirical radio-boundary check is still required)
- Static multi-hop routes: `routes-initial.xml` and `routes-optimized.xml`
- Initial vs Optimized: controlled node-placement and routing changes; sensing interval, number of nodes and traffic volume stay constant.

## Reproducible topology
`topology.csv` contains exact node coordinates in meters and parent next-hop edges for both scenarios. `verify_layout.py` checks the graph, routes, and 50 m geometric limits.

## How to run once INET 4.6 is built
```bash
cd inet-4.6.0
source setenv
cd /path/to/Smart_Crop_Monitoring_WSN/crop-wsn
inet --release -u Cmdenv -n . -c Initial -f omnetpp.ini
inet --release -u Cmdenv -n . -c Optimized -f omnetpp.ini
```

Use Qtenv for screenshots by removing `-u Cmdenv` and running from an environment with a desktop. The GitHub workflow tests through the command-line simulator only; graphical screenshots must be genuine captures from a running simulator later.

## Evidence and quality gates
The `.sca` files are expected to contain measured packet counts, the UDP sink's delay histogram, and 13 residual-energy values from `SimpleEpEnergyStorage`. Each node begins at **1000 J**; `analyze_results.py` computes total energy used as `13 × 1000 J − sum(residual capacities)` only if all 13 values exist. The CLI `--require-energy` rejects incomplete energy evidence. This is a model-based energy measurement, not a laboratory battery test. The 50 m communication boundary still needs empirical validation.

## Before/after comparison
When **both full-length runs have finished and all 13 energy capacities are recorded**, calculate a submission-ready table with:

```bash
python3 compare_results.py results/Initial.sca results/Optimized.sca --out results/validated-comparison.csv
```

The comparison command **fails** rather than inventing numbers when measured PDR, delay or energy are absent. GitHub's first 30-second bring-up should never be substituted for the required full 930-second experiment. Before submitting, also verify that multi-hop forwarding occurred in packet/event traces rather than only in static route files.
