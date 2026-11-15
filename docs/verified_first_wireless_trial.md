# First verified wireless delivery — 15 November 2026

## Evidence provenance

- Simulation: `wsn.crop.FarmNetwork`, `Initial` configuration.
- Runtime: OMNeT++ 6.3.0, INET 4.6.0, IEEE 802.15.4 narrowband interface.
- Simulation duration: **30 simulated seconds**, initial diagnostic only.
- Source: [original GitHub Actions run 43664625600](https://github.com/assemalqudami-maker/Smart_Crop_Monitoring_WSN/actions/runs/43664625600) and its artifact `inet-radio-upstream-results` (`crop-wsn/results/Initial.sca`).
- Analysis reproduction: [workflow 43666398097](https://github.com/assemalqudami-maker/Smart_Crop_Monitoring_WSN/actions/runs/43666398097), script `crop-wsn/inspect_legacy_artifact.py`.

## Actual observed data

| Metric | Observed |
| --- | ---: |
| Source nodes with sent packet counts | 12 |
| Total packets generated | 12 |
| Packets received by sink application | 12 |
| Packet delivery ratio, app-to-app | 100% |
| Sink end-to-end mean delay | 12.528405835667 ms |
| Received packet delay sample count | 12 |

The source run sent one packet from each source in its first sampling cycle. Consequently, this result is **not** a 5-minute repeated-sampling evaluation, even though the configured interval is 300s.

## What this does and does not prove

It **does prove** that the farm's IEEE 802.15.4 / IPv4-based nodes sent and delivered UDP telemetry to the sink in the recorded initial trial. The previous parser rejected this run because of the original ideal battery model; the raw result contains the above actual counters.

It **does NOT prove** full ZigBee NWK compliance, accurately calibrated 50m physical coverage, verified paths taken by every packet, or any improvement from optimization. The original ideal-storage energy readings included small negative residual values. They are **not valid energy-capacity measurements** and must never appear in the final energy comparison.

The full 930-second `Initial` and `Optimized` trial workflow with finite energy storage and strict measured-metric comparison is configured in `inet-radio/run.sh`. That full trial is pending its own conclusive passing GitHub Actions run.

## Before publishing a final table

1. Verify the full trial runs complete for both scenarios.
2. Verify all 13 real finite-energy residual readings are present for each scenario.
3. Confirm multi-hop routing from observable per-hop packet evidence, not solely XML next-hop routes.
4. Check the ZigBee requirement against the actual implemented stack; IEEE 802.15.4 with IPv4 is not the full ZigBee stack.
5. Preserve the raw scalar/vector files alongside generated CSV/JSON and simulator version/commit metadata.

## Independent MAC-level relay indicators

A reinspection of the **same raw scalar artifact**, with [GitHub Actions run 43666521951](https://github.com/assemalqudami-maker/Smart_Crop_Monitoring_WSN/actions/runs/43666521951), found the following IEEE 802.15.4 MAC frame counters:

| Sensor | `nbRxFrames` | `nbTxFrames` | Own app messages sent |
| --- | ---: | ---: | ---: |
| sensor[0] | 11 | 12 | 1 |
| sensor[1] | 2 | 3 | 1 |
| sensor[2] | 1 | 2 | 1 |
| sensor[4] | 3 | 4 | 1 |
| sensor[8] | 3 | 4 | 1 |

These frame counts are consistent with intermediate relaying; for example, sensor[0] sent twelve MAC frames while originating only one application packet. This independently supports multi-hop behavior, but the counts alone may include retransmission effects. Packet-level path evidence is still required for definitive per-packet hop attribution.
