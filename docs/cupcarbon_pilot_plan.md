# CupCarbon pilot plan — map and ZigBee compliance gate

**Purpose:** evaluate a small alternative/pilot for the exact IT484 rubric items that are not currently demonstrated by the OMNeT++/INET branch. This document does not claim that CupCarbon has been installed or that a pilot has passed.

## Why evaluate CupCarbon?

The official CupCarbon Klaines 8.3 site documents:
- OpenStreetMap-based map canvas and offline map backgrounds.
- A discrete-event WSN simulation mode using SenScript.
- ZigBee, Wi-Fi and LoRa radio choices in its WSN engine.
- Energy/battery models and CSV output at `results/wisen_simulation.csv`.
- Java 17+ for application launch; Python 3 is needed for the separate IoT-node scripts.

The assignment asks to import a city map, highlight key zones, use 10–12 sensors plus one sink, set 50 m range, ZigBee and five-minute sensing, demonstrate multi-hop routing, compare before/after, and include screenshots.

## Important distinction in CupCarbon

A project is either:
- **Classical WSN nodes** programmed with SenScript and run by the discrete-event WSN engine; or
- **IoT nodes** programmed with Python `cup_*` functions and run by the IoT simulation.

The two modes cannot be mixed in one CupCarbon project. For this assignment's WSN + ZigBee requirement, the pilot must use the **classical WSN / SenScript** mode, not assume Python IoT nodes are equivalent.

## Pilot acceptance checklist

1. Install CupCarbon Klaines 8.3 on Windows with Java 17+.
2. Create a new project and choose classical WSN sensor nodes (SenScript).
3. Open the OSM map for the selected agricultural study area; if internet tiles are unavailable, test an offline background.
4. Mark farm plots, access roads, water source/irrigation channel and a sink location. Do not invent real farm features: identify them as schematic if no verified local map data is available.
5. Add 12 sensor nodes and one sink. Record their GPS coordinates.
6. Select ZigBee radio in the WSN engine and configure/test a 50 m range. Verify at least one pair just inside and outside the boundary; do not assume a UI radius setting alone proves effective radio range.
7. Configure a 300-second sensing/transmission interval.
8. Demonstrate a multi-hop path from the farthest sensor to the sink. Preserve the route/path evidence and packet counters.
9. Run the Initial layout and save the CSV and screenshots.
10. Rearrange nodes or alter a documented routing/interval parameter for Optimized. Keep other experimental factors controlled.
11. Run Optimized with the same seed/settings where the simulator supports it. Compare PDR, energy/battery, and average delay. If the CSV does not expose a required metric, record that limitation; do not invent it.
12. Decide whether CupCarbon can replace OMNeT++ for the final deliverable only after all the above gates pass.

## Current status

- OMNeT++/INET remains the reproducible baseline already implemented.
- INET is IEEE 802.15.4 PHY/MAC plus manually configured IPv4 routing, **not a complete ZigBee NWK/APS implementation**.
- CupCarbon is a documented candidate for the map and ZigBee requirements, but its 50 m, five-minute, multi-hop and metric-export behavior for this exact 12-node crop scenario has not yet been tested.
- Do not merge unverified CupCarbon screenshots or results into the OMNeT++ results table.

## Official references

- https://www.cupcarbon.com/
- https://www.cupcarbon.com/help.html
- https://www.cupcarbon.com/installation.html
- https://www.cupcarbon.com/tutorials.html
- https://inet.omnetpp.org/docs/users-guide/ch-802154.html
