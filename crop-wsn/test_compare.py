"""Synthetic parser comparison fixtures only, not measured network results."""
import importlib.util
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

if __name__=="__main__":
    unittest.main()
