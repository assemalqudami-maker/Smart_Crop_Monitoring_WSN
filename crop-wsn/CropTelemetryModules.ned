package wsn.crop;

import inet.applications.udpapp.UdpBasicApp;
import inet.applications.udpapp.UdpSink;

simple CropTelemetryApp extends UdpBasicApp
{
    parameters:
        @class(CropTelemetryApp);
        int sensorId = default(0);
        double baseTemperatureC = default(22);
        double baseHumidityPct = default(45);
        double baseSoilMoisturePct = default(30);
}

simple CropTelemetrySink extends UdpSink
{
    parameters:
        @class(CropTelemetrySink);
}
