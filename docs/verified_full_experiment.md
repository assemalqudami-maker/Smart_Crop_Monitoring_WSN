# Verified full-length WSN experiment results

**Run:** [GitHub Actions 43668567880](https://github.com/assemalqudami-maker/Smart_Crop_Monitoring_WSN/actions/runs/43668567880)  
**Artifact:** [inet-radio-upstream-results.zip](https://github.com/assemalqudami-maker/Smart_Crop_Monitoring_WSN/actions/runs/43668567880/artifacts/14144120600)  
**Runtime:** OMNeT++ 6.3.0 + INET 4.6.0  
**Simulation:** 930 simulated seconds per scenario; seed-set 5  
**Network:** 12 sensor nodes + 1 sink; IEEE 802.15.4 narrowband PHY/MAC, manually configured IPv4 multi-hop routes; 50 m medium range cap; 300 s sample interval.

## Measured comparison

| Metric | Initial | Optimized | Change |
| --- | ---: | ---: | ---: |
| Generated packets | 48 | 48 | — |
| Delivered packets | 48 | 48 | — |
| Packet Delivery Ratio | 100.00% | 100.00% | 0.00 percentage points |
| Modeled radio energy consumed (sensors + sink) | 0.315161 J | 0.301669 J | 4.2812% lower |
| Mean sink end-to-end delay | 12.568406 ms | 11.560303 ms | 8.0209% lower |

Each of the 12 sensors generated exactly four packets (one in each of the four configured sample cycles). The sink received all 48 in both scenarios.

## Energy breakdown

| Energy component | Initial | Optimized |
| --- | ---: | ---: |
| Sensors | 0.291202 J | 0.278707 J |
| Sink | 0.023960 J | 0.022961 J |
| Total | 0.315161 J | 0.301669 J |

The energy metric is **radio-state energy modeled by INET's SensorStateBasedEpEnergyConsumer**, integrated by SimpleEpEnergyStorage with 1000 J initial capacity for each of 13 nodes. It is not a measurement of CPU, sensing circuitry, or a physical sensor board.

## Full-run multi-hop evidence

The raw `.sca` files from the same run were independently audited using `crop-wsn/verify_multihop.py`. For both Initial and Optimized, all twelve sensors' measured application packet counts and their MAC `nbTxFrames` / `nbRxFrames` counters exactly matched the directed next-hop tree's aggregate forwarding predictions. The sink MAC RX count was 48, matching its application RX count. All audited sensor nodes reported zero missed ACKs and zero dropped frames.

This verifies aggregate multi-hop forwarding for both complete scenarios; it is stronger than checking route files alone. It does not provide a timestamped path trace for each individual packet.

## Interpretation and limitations

- The Optimized layout reduces measured radio energy by 4.2812% and mean delay by 8.0209%, while PDR remains 100% in both runs.
- The 50 m setting is enforced as the radio medium's maximum communication-range filter and all next-hop geometry links are within that cap. A separate boundary-calibration experiment at 49 m and 51 m is still recommended before describing effective RF range as experimentally calibrated.
- INET 4.6 implements IEEE 802.15.4 PHY/MAC, **not the ZigBee NWK/APS stack**. The current routed IPv4 layer must not be called full ZigBee.
- Telemetry packets are currently generic packets named `CropTelemetry`; temperature, humidity, and soil-moisture fields still need to be encoded and recorded by the application layer before the project can claim to simulate those three crop measurements specifically.
- The 930-second results are valid for the current model and configuration, not a physical deployment prediction.

## Reproduction

```bash
bash inet-radio/run.sh
```

The script builds INET, runs the official IEEE 802.15.4 showcase, executes both farm scenarios, extracts metrics, verifies measured multi-hop MAC flow, and creates the before/after CSV.
