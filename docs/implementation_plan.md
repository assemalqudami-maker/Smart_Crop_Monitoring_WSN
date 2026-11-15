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

- OMNeT++ 6.3 NED parser validation PASSED in GitHub Actions run [43665209805](https://github.com/assemalqudami-maker/Smart_Crop_Monitoring_WSN/actions/runs/43665209805). This validates NED syntax, not dependent INET module resolution or runtime.
- Stronger cross-file checks verify `FarmNetwork.ned`, `omnetpp.ini`, `topology.csv` and both routing XML files agree on 12 sensors, 1 sink, 300s sample interval, 50m medium cap and initial/optimized coordinates; PASSED in run [43665356064](https://github.com/assemalqudami-maker/Smart_Crop_Monitoring_WSN/actions/runs/43665356064).
- Radio build concurrency and a longer CI timeout were configured; INET build and real radio metrics remain unverified until its workflow completes successfully.

## Measurement-integrity gate — 15 November 2026

- Test suite on the updated farm branch: **11/11 tests PASSED** in [GitHub Actions run 43667163368](https://github.com/assemalqudami-maker/Smart_Crop_Monitoring_WSN/actions/runs/43667163368).
- `analyze_results.py` now exposes generated packet counts per sensor. `compare_results.py` rejects a final comparison unless **each of the twelve sensors produced four recorded readings** in *both* 930-second runs (initial sample at 1–5s, then +300s, +600s, +900s), with measured delay and finite-energy values.
- This check makes a one-cycle 30-second smoke test insufficient for the final report. Improvement may be zero or negative; no metric will be changed to imply success.
- Full-run trial [GitHub Actions 43666881469](https://github.com/assemalqudami-maker/Smart_Crop_Monitoring_WSN/actions/runs/43666881469) was *in progress* at the time of verification. The passing synthetic-fixture test suite must not be mistaken for a passing 930-second simulation.


## Verified full radio experiment — 15 November 2026

- [GitHub Actions run 43668567880](https://github.com/assemalqudami-maker/Smart_Crop_Monitoring_WSN/actions/runs/43668567880) completed successfully after enabling NodeStatus on all 13 nodes.
- Both Initial and Optimized completed 930 simulated seconds. Each of 12 sensors generated four packets; sink received 48/48 in each scenario.
- Measured PDR: 100% both; modeled radio energy: 0.315161 J Initial vs 0.301669 J Optimized (4.2812% lower); average delay: 12.568406 ms vs 11.560303 ms (8.0209% lower).
- Raw artifacts: [artifact 14144120600](https://github.com/assemalqudami-maker/Smart_Crop_Monitoring_WSN/actions/runs/43668567880/artifacts/14144120600). Detailed interpretation in `docs/verified_full_experiment.md`.
- Independent full-run MAC counter audit performed on raw .sca files for both scenarios: expected and measured aggregate per-node MAC TX/RX counts match, sink MAC RX = 48, no missed ACKs or dropped frames. Reproduction is added to the run script.
- Energy is modeled radio-state energy only (not CPU/sensor-board power). Current upper layers are manually routed IPv4, not a ZigBee NWK/APS stack. Generic telemetry still needs actual temperature/humidity/soil fields.
- Outstanding: implement/obtain ZigBee-compatible NWK model, encode crop readings, empirically validate 50m boundary, import a real map and capture screenshots, prepare Word/PDF report, 5–6 slides and 5-minute demo.
