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

## Additional model research — 15 November 2026

### INET finding
The official INET 4.6 guide states that IEEE 802.15.4 specifies PHY and MAC, while ZigBee adds upper layers beyond those. Therefore the current `Ieee802154NarrowbandInterface` plus manually routed IPv4 is an IEEE 802.15.4 WSN simulation, not a standards-complete ZigBee stack.

### Candidate ZigBee implementations reviewed
- `Shtrikh17/ZigBee-attacks-model` (2017-era OMNeT++ code) contains a simplified ZigBee-like NWK/AODV model, but its normal mesh code passes custom MAC-frame objects over direct module gates and explicitly describes the MAC interface as a future replacement. It is not an integrated, validated INET PHY/MAC + ZigBee stack for our current model. Do not simply label it full ZigBee or combine it without substantial engineering and verification.
- A repository named `YuuFii/Simple_Zigbee_Star_Simulation` contains only a bundled ZIP and has not yet been audited for version compatibility, mesh support, or protocol completeness. It is not an approved dependency.
- **CupCarbon Klaines 8.3** official documentation describes its discrete-event WSN engine as supporting ZigBee, Wi-Fi and LoRa, OSM map backgrounds, radio propagation, interference, mobility, energy and battery models. This is currently the strongest candidate if the instructor requires a simulator with native ZigBee and imported-map support.

### Decision gate
Keep OMNeT++/INET for the current verified wireless and performance experiments, but **do not claim the ZigBee requirement is met**. Before final submission, either:
1. obtain explicit instructor approval to accept IEEE 802.15.4 PHY/MAC with a documented custom/manual routing layer as the project communication implementation; or
2. port the final required WSN demonstration and metrics to a simulator/model that actually provides ZigBee (CupCarbon is the first candidate), preserving GitHub as the source/evidence repository.

No final report should describe the current model as ZigBee until this gate is resolved.

### Public references
- INET 4.6 IEEE 802.15.4 guide: https://inet.omnetpp.org/docs/users-guide/ch-802154.html
- CupCarbon Klaines official help: https://cupcarbon.com/help.html
- CupCarbon official site: https://www.cupcarbon.com/
- Simplified third-party NWK research model: https://github.com/Shtrikh17/ZigBee-attacks-model
- Third-party bundled OMNeT++ project, not yet audited: https://github.com/YuuFii/Simple_Zigbee_Star_Simulation
