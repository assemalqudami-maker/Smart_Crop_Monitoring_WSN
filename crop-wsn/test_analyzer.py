"""Unit-test parsing, not radio simulation performance.

The 12 synthetic counters below are only fixtures for automated parser tests.
They must never be used as experiment results or quoted in the final report.
"""
import tempfile
import unittest
from pathlib import Path
from analyze_results import analyze


class ScalarAnalyzerTests(unittest.TestCase):
    def make_scalar_file(self, sink_received=9, missing_sensor=None):
        rows = ["version 2", 'run test_fixture']
        for i in range(12):
            if i != missing_sensor:
                rows.append(f"scalar FarmNetwork.sensor[{i}].app[0] packetSent:count 1")
        rows.append(f"scalar FarmNetwork.sink.app[0] packetReceived:count {sink_received}")
        rows.extend([
            "statistic FarmNetwork.sink.app[0] endToEndDelay",
            "field count 9",
            "field mean 0.0045",
        ])
        f = Path(self.temp_dir.name) / "fixture.sca"
        f.write_text("\n".join(rows) + "\n", encoding="utf-8")
        return f

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_counts_pdr_delay(self):
        result = analyze(self.make_scalar_file())
        self.assertEqual(result["generated_packets"], 12)
        self.assertEqual(result["delivered_packets"], 9)
        self.assertEqual(result["packet_delivery_ratio_percent"], 75)
        self.assertAlmostEqual(result["average_delay_ms"], 4.5)
        self.assertIsNone(result["energy_consumption_total_joules"])

    def test_missing_sensor_is_failure(self):
        with self.assertRaisesRegex(ValueError, "expected sent-count scalars for 12 nodes"):
            analyze(self.make_scalar_file(missing_sensor=2))

    def test_invalid_delivery_is_failure(self):
        with self.assertRaisesRegex(ValueError, "invalid delivered"):
            analyze(self.make_scalar_file(sink_received=20))


if __name__ == "__main__":
    unittest.main()
