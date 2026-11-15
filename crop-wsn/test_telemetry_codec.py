import unittest
from telemetry_codec import encode,decode,SIZE

class TelemetryCodecTests(unittest.TestCase):
    def test_fixed_13_byte_layout_round_trip(self):
        payload=encode(7,3,24.35,55.25,38.75,905123)
        self.assertEqual(len(payload),13)
        result=decode(payload)
        self.assertEqual(result["sensor_id"],7)
        self.assertEqual(result["sequence"],3)
        self.assertAlmostEqual(result["temperature_c"],24.35)
        self.assertAlmostEqual(result["relative_humidity_pct"],55.25)
        self.assertAlmostEqual(result["soil_moisture_pct"],38.75)
        self.assertEqual(result["sample_time_ms"],905123)

    def test_invalid_payload_size_rejected(self):
        with self.assertRaisesRegex(ValueError,"expected 13 bytes"):
            decode(b"short")

    def test_out_of_range_reading_rejected(self):
        with self.assertRaisesRegex(ValueError,"percentage"):
            encode(1,0,25,120,30,1000)

    def test_version_mismatch_rejected(self):
        payload=bytearray(encode(1,0,25,50,30,1000))
        payload[0]=2
        with self.assertRaisesRegex(ValueError,"unsupported telemetry version"):
            decode(bytes(payload))

if __name__=="__main__": unittest.main()
