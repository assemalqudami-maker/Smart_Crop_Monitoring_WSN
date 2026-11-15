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
The `.sca` files contain measured packet counts, end-to-end delay statistics and energy-state readings (depending on model output). `analyze_results.py` fails if any of the 12 source packet counts or the sink counter are missing, and **never fabricates energy or delay**. A verified energy baseline and current range calibration are required for an academically defensible before/after table.
