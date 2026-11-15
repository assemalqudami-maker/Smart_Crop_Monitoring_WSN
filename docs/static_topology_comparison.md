# Static topology comparison — Initial vs Optimized

**Scope:** design-only metrics derived from `crop-wsn/topology.csv` and directed parent next hops. This section is separate from the radio simulations and the final PDR/delay/energy evaluation.

## Reproducible geometric results

| Design-only metric | Initial | Optimized |
| --- | ---: | ---: |
| Sensor nodes | 12 | 12 |
| Sink nodes | 1 | 1 |
| Sum of directed source-to-sink hop counts | 38 | 36 |
| Maximum source-to-sink hop count | 5 | 5 |
| Sum of Euclidean source-to-sink path lengths | 1,460.00 m | 1,090.07 m |
| Mean source-to-sink path length | 121.67 m | 90.84 m |

The redesigned layout reduces the **sum of directed source-to-sink hop counts by 5.26%**, and the **sum of Euclidean source-to-sink path lengths by 25.34%**. Both designs remain within the 50 m limit for each defined next-hop link.

## How the numbers were calculated

For each of the 12 sources, start at its own node, follow the `next_hop` field until the sink, count edges, and sum the Euclidean distances of those edges. The aggregate path length is the sum of these *twelve source-specific path lengths*; a relay link is deliberately counted multiple times when it carries multiple sources' paths. This is not the length of distinct deployed cable or the area of radio coverage.

To reproduce:

```bash
python3 crop-wsn/compare_topology.py
```

## Evidence limitation

These are purely geometric routing-design indicators and **NOT** verified energy savings, throughput improvements, lower measured delay, or ZigBee-compliant network-layer routing. The actual `.sca` and `.vec` output from full radio experiments must be used to calculate the real network performance changes. If the real optimized scenario performs worse, the final report must disclose that result without alteration.
