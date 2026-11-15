# Smart Crop Monitoring using Wireless Sensor Networks

**Course:** IT484 — Wireless Sensor Networks  
**Simulation stack (target):** OMNeT++ 6.3.0 + INET 4.6.0  
**Project deadline:** 30 November 2026, 23:59 (as stated in the course brief)

## Project objective

Design, simulate, evaluate and optimize a wireless sensor network for smart crop monitoring. The final simulation will include **12 sensor nodes and 1 sink**, a **50 m transmission range**, **5-minute sensing intervals**, multi-hop data forwarding, and a documented ZigBee-compatible communication design.

The final report will compare *initial* and *optimized* scenarios using:
- Packet delivery ratio (PDR)
- Energy consumption
- Average end-to-end delay (ms)

## Current implementation state

**Current status (15 November 2026):** Both full 930-second IEEE 802.15.4 farm scenarios have completed successfully. Each delivered 48/48 packets. Measured modeled radio energy fell from 0.315161 J to 0.301669 J (4.2812%), and mean delay fell from 12.568406 ms to 11.560303 ms (8.0209%). Full-run MAC counters for both scenarios match the configured multi-hop tree. See [full experiment evidence](docs/verified_full_experiment.md) and [project plan](docs/implementation_plan.md). The implementation still uses IPv4 above IEEE 802.15.4, not full ZigBee, and generic packets still need crop-reading fields.

**Important protocol distinction:** IEEE 802.15.4 PHY/MAC (provided by INET) is **not** a complete ZigBee protocol stack. We will explicitly verify the network/routing layers before describing the implementation as ZigBee. No measured numbers will be fabricated.

## Deliverables required by the course

1. Editable simulator project and demonstrable data transmission.
2. Report following the provided university assignment template (both Word and PDF).
3. Five-minute demo.
4. Five- to six-slide PowerPoint presentation.
5. Evidence screenshots: mapped environment, node placement and coverage, initial communication paths, optimized layout, and measured results.

## Repository conventions

- All report content and submission material will be in **English**.
- Generated simulation output and binary files are not committed.
- All experimental results must include their configurations, run identifiers and source traces.
- Milestones are verified in order: toolchain smoke test → radio feasibility → complete WSN → optimization → report/demo.

## Sources

- Course handout: `IT484 Project.pdf` (provided separately by the student; do not redistribute without permission).
- [OMNeT++](https://omnetpp.org/)
- [INET](https://inet.omnetpp.org/)
- [INET IEEE 802.15.4 documentation](https://inet.omnetpp.org/docs/4.7/users-guide/ch-802154.html)
