# Gate 2 — IEEE 802.15.4 upstream radio feasibility

**Status: Pending actual CI execution.**

The GitHub Action uses the officially published `ghcr.io/omnetpp/omnetpp:u24.04-6.3.0` image, clones INET `v4.6.0`, compiles the official source and launches the **official** `showcases/wireless/ieee802154` `Ieee802154Power` configuration in command-line mode.

This is an upstream showcase validation; **not** the project's final network, and **not** full ZigBee. A passing CI check means INET's 802.15.4 radio/MAC simulator runs in our toolchain. It does not measure crop-specific performance or implement a 12-node ZigBee mesh.

Resources:
- https://github.com/inet-framework/inet/tree/v4.6.0/showcases/wireless/ieee802154
- https://inet.omnetpp.org/docs/showcases/wireless/ieee802154/doc/index.html
- https://inet.omnetpp.org/Download.html
