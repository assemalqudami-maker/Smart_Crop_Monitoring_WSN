"""Tests for static design comparison — NOT measurements of network performance."""
import unittest
from compare_topology import compute_design


class TopologyComparisonTests(unittest.TestCase):
    def test_12_sensors_and_1_sink_both_scenarios(self):
        r = compute_design()
        for name in ("Initial", "Optimized"):
            self.assertEqual(r[name]["sensor_count"], 12)
            self.assertEqual(r[name]["sink_count"], 1)

    def test_reproducible_static_hop_and_distance_comparison(self):
        r = compute_design()
        self.assertEqual(r["Initial"]["sum_source_to_sink_hops"], 38)
        self.assertEqual(r["Optimized"]["sum_source_to_sink_hops"], 36)
        self.assertAlmostEqual(r["Initial"]["sum_source_to_sink_path_lengths_m"], 1460, places=4)
        self.assertAlmostEqual(r["Optimized"]["sum_source_to_sink_path_lengths_m"],
                               1090.073138, places=4)
        self.assertGreater(r["design_difference"]["cumulative_path_length_reduction_percent"], 25)
        self.assertEqual(r["Initial"]["max_source_to_sink_hops"], 5)
        self.assertEqual(r["Optimized"]["max_source_to_sink_hops"], 5)


if __name__ == "__main__":
    unittest.main()
