# Protocol decision record — WSN/ZigBee feasibility

Status: **unverified; awaiting wireless demonstration and routing-layer implementation**.

## Course requirement
A 10–12-sensor WSN (we will use 12) must use ZigBee communication, 50 m transmission range, 5-minute sensing interval and multi-hop routing to a sink.

## Official library assessment
- OMNeT++ 6.3.0 is supported by INET 4.6.0.
- INET 4.6.0 includes an IEEE 802.15.4 radio/MAC family (e.g., `Ieee802154NarrowbandInterface`).
- IEEE 802.15.4 specifies PHY and MAC; ZigBee further specifies network/application-layer capabilities. **Do not label an IEEE 802.15.4-only scenario as full ZigBee.**
- The INET sensor-network showcase explains that WSN-specific routing such as Collection Tree Protocol is not included in the showcase; use a clearly specified forwarding design rather than implying such a protocol exists.

## Required evaluation before choosing the final stack
1. Reproduce the official INET 4.6 IEEE 802.15.4 showcase in a controlled environment.
2. Establish a verified 50 m radio-range configuration by empirical test at slightly shorter/longer separation; do not equate a setting with proved effective range.
3. Implement/document multi-hop forwarding and packet IDs, timestamps, hop count and sink reception.
4. Verify that the chosen layers constitute the ZigBee communication protocol requested by the instructor. If we implement only an 802.15.4-derived subset, call out the limitation and seek instructor approval or switch simulators/models.
5. Add energy and radio state accounting, reproducible seeds, and before/after scenarios only after wireless tests pass.

## References
- https://inet.omnetpp.org/Download.html (version compatibility)
- https://inet.omnetpp.org/docs/users-guide/ch-802154.html (802.15.4 model)
- https://inet.omnetpp.org/docs/showcases/wireless/ieee802154/doc/index.html (official PHY example)
- https://inet.omnetpp.org/docs/showcases/wireless/sensornetwork/doc/ (WSN routing caveat)

## Scope of the current smoke test
The wired 3-source/1-sink model confirms only compilation, execution and scalar production. It provides **no wireless, ZigBee, radio range, energy, collision or multi-hop evidence**.
