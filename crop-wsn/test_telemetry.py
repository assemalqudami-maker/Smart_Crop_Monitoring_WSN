"""Synthetic fixtures only; not simulation measurements."""
import tempfile
import unittest
from pathlib import Path
from verify_telemetry import validate

class TelemetryValidationTests(unittest.TestCase):
    def setUp(self): self.tmp=tempfile.TemporaryDirectory()
    def tearDown(self): self.tmp.cleanup()

    def fixture(self, missing_sensor=None, corrupt_value=False):
        lines=["version 2","run telemetry_fixture"]
        n=4
        for i in range(12):
            lines.append(f"scalar FarmNetwork.sensor[{i}].app[0] packetSent:count {n}")
            prefix=f"sensor{i}"
            count=3 if i==missing_sensor else n
            lines.append(f"scalar FarmNetwork.sink.app[0] {prefix}DecodedPackets {count}")
            for name,value in (("MeanTemperatureC",24.5),("MeanRelativeHumidityPct",55.0),("MeanSoilMoisturePct",38.0)):
                actual=150 if corrupt_value and i==0 and name=="MeanSoilMoisturePct" else value
                lines.append(f"scalar FarmNetwork.sink.app[0] {prefix}{name} {actual}")
        lines += [
            "scalar FarmNetwork.sink.app[0] packetReceived:count 48",
            "scalar FarmNetwork.sink.app[0] decodedTelemetryPackets 48",
            "scalar FarmNetwork.sink.app[0] meanTemperatureC 24.5",
            "scalar FarmNetwork.sink.app[0] meanRelativeHumidityPct 55",
            "scalar FarmNetwork.sink.app[0] meanSoilMoisturePct 38",
        ]
        path=Path(self.tmp.name)/"telemetry.sca"
        path.write_text("\n".join(lines)+"\n",encoding="utf-8")
        return path

    def test_valid_sensor_measurements(self):
        result=validate(self.fixture(),4)
        self.assertEqual(result["telemetry_packets_decoded"],48)
        self.assertEqual(result["payload_format"],"versioned binary, 13 bytes")
        self.assertEqual(len(result["per_sensor"]),12)

    def test_missing_sensor_packets_rejected(self):
        with self.assertRaisesRegex(ValueError,r"decoded 3(?:\.0)?; expected 4"):
            validate(self.fixture(missing_sensor=4),4)

    def test_out_of_range_measurement_rejected(self):
        with self.assertRaisesRegex(ValueError,"outside sanity bounds"):
            validate(self.fixture(corrupt_value=True),4)

if __name__=="__main__": unittest.main()
