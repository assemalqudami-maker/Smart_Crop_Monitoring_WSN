"""Synthetic parser comparison fixtures only, not measured network results."""
import pathlib
import tempfile
import unittest
from compare_results import compare

class ComparisonTests(unittest.TestCase):
    def test_no_fabricated_missing_energy(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)
            for filename in ["Initial.sca","Optimized.sca"]:
                (p/filename).write_text(
                    "\n".join([f"scalar FarmNetwork.sensor[{i}].app[0] packetSent:count 1" for i in range(12)])
                    +"\nscalar FarmNetwork.sink.app[0] packetReceived:count 10\n"
                    +"statistic FarmNetwork.sink.app[0] endToEndDelay:histogram\n"
                    +"field count 10\nfield mean 0.01\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"energy recordings absent"):
                compare(p/"Initial.sca",p/"Optimized.sca")


    @staticmethod
    def complete_scalar(path, residual, delay):
        lines=["version 2","run synthetic_complete_fixture"]
        for i in range(12):
            lines.append(f"scalar FarmNetwork.sensor[{i}].app[0] packetSent:count 4")
            lines.append(f"scalar FarmNetwork.sensor[{i}].energyStorage residualEnergyCapacity:last {residual}")
        lines.append("scalar FarmNetwork.sink.app[0] packetReceived:count 48")
        lines.append(f"scalar FarmNetwork.sink.energyStorage residualEnergyCapacity:last {residual}")
        lines.append("statistic FarmNetwork.sink.app[0] endToEndDelay:histogram")
        lines.append("field count 48")
        lines.append(f"field mean {delay}")
        path.write_text("\n".join(lines)+"\n",encoding="utf-8")

    def test_full_run_comparison_uses_only_complete_samples(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            self.complete_scalar(root/"Initial.sca",999.8,0.01)
            self.complete_scalar(root/"Optimized.sca",999.9,0.008)
            report=compare(root/"Initial.sca",root/"Optimized.sca")
            self.assertEqual(len(report["comparison"]),3)
            pdr=report["comparison"][0]
            self.assertEqual(pdr["Initial Value"],100)
            self.assertEqual(pdr["Optimized Value"],100)
            energy=report["comparison"][1]
            self.assertGreater(energy["Improvement"],0)
            delay=report["comparison"][2]
            self.assertAlmostEqual(delay["Improvement"],2)

    def test_short_trial_is_not_accepted_as_final_comparison(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d)
            self.complete_scalar(root/"Initial.sca",999.8,0.01)
            self.complete_scalar(root/"Optimized.sca",999.9,0.008)
            text=(root/"Initial.sca").read_text(encoding="utf-8")
            text=text.replace("packetSent:count 4","packetSent:count 1")
            text=text.replace("packetReceived:count 48","packetReceived:count 12")
            text=text.replace("field count 48","field count 12")
            (root/"Initial.sca").write_text(text,encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"expected 4 telemetry packets"):
                compare(root/"Initial.sca",root/"Optimized.sca")

if __name__=="__main__":
    unittest.main()
