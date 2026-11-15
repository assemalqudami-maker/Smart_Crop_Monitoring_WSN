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

Gate 0: PASSED (repository initialized).
Gate 1: PASSED (GitHub Actions run 43663722934; 30 generated and 30 delivered packets on a **wired** smoke network).
Gate 2: IN PROGRESS: official INET 4.6 / IEEE 802.15.4 radio showcase build and crop-radio validation (see GitHub Actions `inet-radio.yml`). There is NO validated ZigBee NWK stack yet.
Gate 3/4: DESIGN FILES PRESENT; static layout validation PASSED in run 43664678667: 12 sensors, one sink, link lengths <= 50m, loop-free routes, maximum five planned hops in both designs. A real geographic map and radio range tests are NOT complete.
Gate 5/6: experiments and radio PDR/delay/energy results NOT YET VERIFIED.
Metrics parser: 3 synthetic-fixture unit tests PASSED in run 43664678667 (these fixture counts are NOT experiment measurements).


## Implementation update — 15 November 2026

- Reproducible farm graph scenarios created under `crop-wsn/`.
- Defined finite initial battery capacities (1000 J per simulated node) and guarded measured energy accounting. This is not a physical-device battery measurement.
- Added strict scalar analyzers and a `compare_results.py` utility that accepts **real Initial/Optimized .sca data only** and rejects missing energy/delay statistics.
- GitHub Actions run [43665022475](https://github.com/assemalqudami-maker/Smart_Crop_Monitoring_WSN/actions/runs/43665022475) passed layout checks and **7 synthetic-fixture parser unit tests**. Synthetic test values must never be described as measured project results.
- The full INET radio workflow is still pending a definitive successful run; do not mark Gate 2 or the full wireless/energy experiment as complete until its GitHub Actions artifacts prove it.
- The current scenario uses `Ieee802154NarrowbandInterface` plus manual IPv4 routes, **not the full ZigBee stack**. Instructor confirmation or a compatible ZigBee model remains a required gate.
- Required mapped city/landmark screenshot, packet-transmission visualization, full-length before/after radio trials, energy/PDR/delay table, 5-minute demo and formatted report are still outstanding.
