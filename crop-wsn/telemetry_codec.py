"""Reference codec for the 13-byte CropTelemetry v1 C++ wire format."""
from __future__ import annotations
import math
import struct

FORMAT = ">BBBhHHI"
SIZE = struct.calcsize(FORMAT)
VERSION = 1

def encode(sensor_id:int, sequence:int, temperature_c:float,
           relative_humidity_pct:float, soil_moisture_pct:float,
           sample_time_ms:int)->bytes:
    if not 0 <= sensor_id <= 255 or not 0 <= sequence <= 255:
        raise ValueError("sensor ID and sequence must fit uint8")
    if not -20 <= temperature_c <= 80:
        raise ValueError("temperature outside supported range")
    if not 0 <= relative_humidity_pct <= 100 or not 0 <= soil_moisture_pct <= 100:
        raise ValueError("percentage outside supported range")
    if not 0 <= sample_time_ms <= 0xFFFFFFFF:
        raise ValueError("timestamp outside uint32")
    return struct.pack(FORMAT, VERSION, sensor_id, sequence,
        round(temperature_c*100), round(relative_humidity_pct*100),
        round(soil_moisture_pct*100), sample_time_ms)

def decode(payload:bytes)->dict:
    if len(payload)!=SIZE:
        raise ValueError(f"expected {SIZE} bytes, got {len(payload)}")
    version,sensor,sequence,temp,humidity,soil,time_ms=struct.unpack(FORMAT,payload)
    if version!=VERSION:
        raise ValueError(f"unsupported telemetry version {version}")
    return {"version":version,"sensor_id":sensor,"sequence":sequence,
        "temperature_c":temp/100.0,"relative_humidity_pct":humidity/100.0,
        "soil_moisture_pct":soil/100.0,"sample_time_ms":time_ms}
