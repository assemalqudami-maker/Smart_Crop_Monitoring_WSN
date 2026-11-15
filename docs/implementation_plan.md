# Implementation roadmap — IT484

## Phase gates

| Gate | Work | Acceptance evidence |
| --- | --- | --- |
| 0 | Initialize repository and scope | README and implementation plan |
| 1 | Validate OMNeT++ toolchain | Compile and run 3-source/1-sink smoke network; machine-readable scalar results |
| 2 | Verify suitable IEEE 802.15.4 + ZigBee models | Written compatibility assessment; no unsupported protocol claims |
| 3 | Import/map crop-monitoring environment | Map screenshot with key areas marked |
| 4 | Build full WSN | 12 sensor nodes, 1 sink, 50 m range, ZigBee, five-minute sensing |
| 5 | Multi-hop initial experiment | Simulation trace, connectivity, PDR, energy, delay |
| 6 | Optimization experiment | Controlled change to placement, routing and transmission interval |
| 7 | Comparative analysis | Source-derived before/after table, graphs and uncertainty |
| 8 | Submission | English report in assignment template (Word + PDF), 5–6 slide presentation, 5-minute demo |

## Acceptance policy

A green unit test does not prove radio connectivity, ZigBee correctness, or successful deployment. Results are accepted only with runnable scripts/configurations, raw simulation evidence and reproducible analysis.

## Key course requirements

- Project idea: option A, crop monitoring (temperature, humidity and soil).
- Nodes: 10–12 sensors and one sink; choose 12.
- Transmission range: 50 m.
- Communication: ZigBee (IEEE 802.15.4 alone is not equivalent).
- Sensing interval: 5 minutes.
- Connect sensors to sink by multi-hop routing.
- Before/after analysis: packet delivery ratio, energy consumption, and average delay in milliseconds.
- Images: key zones on map, coverage and placement, running data flow, optimized layout.
- Original assignment document requires use of the provided template and Times New Roman font; do not substitute a separate report format.

## Experimental integrity

Keep the total simulated time, node population, traffic assumptions, channel model and seeds documented. If sensing and transmission intervals are decoupled, document exactly which interval is changed during optimization. Do not claim wireless or ZigBee behavior from the wired smoke-test modules.

## Current gate

Gate 0: initialized. Gate 1: scaffold only, until an actual OMNeT++ run is verified.
