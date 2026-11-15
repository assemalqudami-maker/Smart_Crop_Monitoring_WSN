"""Synthetic fixtures for strict tree-flow audit; never cite as simulation results."""
import tempfile
import unittest
from pathlib import Path
from verify_multihop import validate_trace, expected_flow

class MacPathAuditTests(unittest.TestCase):
    def make_scalar(self, mismatch=False):
        generated={f"sensor[{i}]":1 for i in range(12)}
        tx,rx=expected_flow(Path(__file__).with_name("topology.csv"),"Initial",generated)
        lines=["version 2","run synthetic_fixture"]
        for node,n in generated.items():
            lines.append(f"scalar FarmNetwork.{node}.app[0] packetSent:count {n}")
            actual=tx[node]+(1 if mismatch and node=="sensor[0]" else 0)
            mac=f"FarmNetwork.{node}.wlan[0].mac"
            lines.extend([
                f"scalar {mac} nbTxFrames {actual}",
                f"scalar {mac} nbRxFrames {rx[node]}",
                f"scalar {mac} nbMissedAcks 0",
                f"scalar {mac} nbDroppedFrames 0",
            ])
        lines.append("scalar FarmNetwork.sink.app[0] packetReceived:count 12")
        lines.append(f"scalar FarmNetwork.sink.wlan[0].mac nbRxFrames {rx['sink']}")
        self.tmp=tempfile.TemporaryDirectory()
        p=Path(self.tmp.name)/"fixture.sca"
        p.write_text("\n".join(lines)+"\n",encoding="utf-8")
        return p

    def tearDown(self):
        if hasattr(self,"tmp"):self.tmp.cleanup()

    def test_valid_relay_tree(self):
        out=validate_trace(self.make_scalar())
        self.assertEqual(out["generated"],12)
        self.assertEqual(out["delivered"],12)
        self.assertEqual(out["per_sensor"][0]["mac_tx"],12)
        self.assertEqual(out["per_sensor"][0]["mac_rx"],11)

    def test_unexpected_mac_retransmissions_are_rejected(self):
        with self.assertRaisesRegex(ValueError,"expected MAC TX/RX"):
            validate_trace(self.make_scalar(mismatch=True))

if __name__=="__main__":
    unittest.main()
