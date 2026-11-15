# Smart Crop Monitoring using Wireless Sensor Networks

**Course:** IT484 — Wireless Sensor Networks  
**Simulation stack (target):** OMNeT++ 6.4.0 + INET 4.7.0  
**Project deadline:** 30 November 2026, 23:59 (as stated in the course brief)

## Project objective

Design, simulate, evaluate and optimize a wireless sensor network for smart crop monitoring. The final simulation will include **12 sensor nodes and 1 sink**, a **50 m transmission range**, **5-minute sensing intervals**, multi-hop data forwarding, and a documented ZigBee-compatible communication design.

The final report will compare *initial* and *optimized* scenarios using:
- Packet delivery ratio (PDR)
- Energy consumption
- Average end-to-end delay (ms)

## Current implementation state

**Stage 0 — repository initialized.** The simulation and its performance results are **not yet validated**. Follow the staged milestones in `docs/implementation_plan.md` after the first project scaffold is merged.

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
