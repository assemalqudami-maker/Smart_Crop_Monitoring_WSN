"""Parser unit tests. All records below are fabricated fixtures, NOT measurements."""
import tempfile
import unittest
from pathlib import Path
from analyze_results import analyze


class ScalarAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def make_file(self, *, delivered=9, missing_sensor=None, energy=True,
                  missing_energy=None, histogram=True):
        rows = ["version 2", "run fixture"]
        for i in range(12):
            if i != missing_sensor:
                rows.append(f"scalar FarmNetwork.sensor[{i}].app[0] packetSent:count 1")
        rows.append(f"scalar FarmNetwork.sink.app[0] packetReceived:count {delivered}")
        if histogram:
            rows += [
                "statistic FarmNetwork.sink.app[0] endToEndDelay:histogram",
                f"field count {delivered}",
                "field mean 0.0045",
            ]
        if energy:
            for i in range(12):
                if missing_energy != f"sensor[{i}]":
                    rows.append(f"scalar FarmNetwork.sensor[{i}].energyStorage residualEnergyCapacity:last 999.75")
            if missing_energy != "sink":
                rows.append("scalar FarmNetwork.sink.energyStorage residualEnergyCapacity:last 999.5")
        path = Path(self.tmp.name) / "fixture.sca"
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        return path

    def test_packet_counts_delay_and_measured_battery_formula(self):
        stats = analyze(self.make_file(), require_energy=True)
        self.assertEqual(stats["generated_packets"], 12)
        self.assertEqual(stats["delivered_packets"], 9)
        self.assertEqual(stats["packet_delivery_ratio_percent"], 75)
        self.assertAlmostEqual(stats["average_delay_ms"], 4.5)
        self.assertAlmostEqual(stats["energy_consumption_sensors_joules"], 3)
        self.assertAlmostEqual(stats["energy_consumption_sink_joules"], 0.5)
        self.assertAlmostEqual(stats["energy_consumption_total_joules"], 3.5)

    def test_missing_sensor_is_failure(self):
        with self.assertRaisesRegex(ValueError, "expected sent-count"):
            analyze(self.make_file(missing_sensor=3))

    def test_impossible_packet_delivery_is_failure(self):
        with self.assertRaisesRegex(ValueError, "invalid delivered"):
            analyze(self.make_file(delivered=20))

    def test_missing_delay_is_failure(self):
        with self.assertRaisesRegex(ValueError, "sink delay histogram"):
            analyze(self.make_file(histogram=False))

    def test_missing_energy_is_failure(self):
        with self.assertRaisesRegex(ValueError, "incomplete energy"):
            analyze(self.make_file(missing_energy="sensor[8]"), require_energy=True)

    def test_absent_energy_cannot_be_claimed(self):
        stats = analyze(self.make_file(energy=False))
        self.assertIsNone(stats["energy_consumption_total_joules"])
        with self.assertRaisesRegex(ValueError, "energy recordings absent"):
            analyze(self.make_file(energy=False), require_energy=True)


if __name__ == "__main__":
    unittest.main()
