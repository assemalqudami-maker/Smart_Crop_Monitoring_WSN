#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>

#include "inet/applications/base/ApplicationPacket_m.h"
#include "inet/applications/udpapp/UdpBasicApp.h"
#include "inet/applications/udpapp/UdpSink.h"
#include "inet/common/TimeTag_m.h"
#include "inet/common/packet/Packet.h"
#include "inet/common/packet/chunk/BytesChunk.h"

using namespace inet;
using namespace omnetpp;

class CropTelemetryApp : public UdpBasicApp
{
  protected:
    void sendPacket() override
    {
        const int sensorId = par("sensorId").intValue();
        const int sequence = numSent;
        const double temperatureC = par("baseTemperatureC").doubleValue() + 0.15 * sequence;
        const double humidityPct = std::max(0.0, std::min(100.0,
            par("baseHumidityPct").doubleValue() - 0.20 * sequence));
        const double soilMoisturePct = std::max(0.0, std::min(100.0,
            par("baseSoilMoisturePct").doubleValue() + 0.35 * sequence));

        std::ostringstream payloadText;
        payloadText << "sensor_id=" << sensorId
                    << ";sequence=" << sequence
                    << ";sim_time_s=" << std::fixed << std::setprecision(3) << simTime().dbl()
                    << ";temperature_c=" << std::setprecision(2) << temperatureC
                    << ";relative_humidity_pct=" << humidityPct
                    << ";soil_moisture_pct=" << soilMoisturePct
                    << ";source=synthetic";

        const std::string packetNameWithSequence =
            std::string(packetName ? packetName : "CropTelemetry") + "-" + std::to_string(sequence);
        auto *packet = new Packet(packetNameWithSequence.c_str());

        const auto& header = makeShared<ApplicationPacket>();
        header->setChunkLength(B(4));
        header->setSequenceNumber(sequence);
        header->addTag<CreationTimeTag>()->setCreationTime(simTime());
        packet->insertAtBack(header);

        const std::string text = payloadText.str();
        const std::vector<uint8_t> bytes(text.begin(), text.end());
        packet->insertAtBack(makeShared<BytesChunk>(bytes));

        emit(registerSignal("packetSent"), packet);
        socket.sendTo(packet, chooseDestAddr(), destPort);
        numSent++;
    }
};
Define_Module(CropTelemetryApp);

class CropTelemetrySink : public UdpSink
{
  private:
    static constexpr int SENSOR_COUNT = 12;
    int decodedPackets = 0;
    std::array<int, SENSOR_COUNT> packetsPerSensor{};
    std::array<double, SENSOR_COUNT> temperatureSums{};
    std::array<double, SENSOR_COUNT> humiditySums{};
    std::array<double, SENSOR_COUNT> soilMoistureSums{};
    double totalTemperature = 0;
    double totalHumidity = 0;
    double totalSoilMoisture = 0;

    static bool readField(const std::string& payload, const std::string& key, double& value)
    {
        const std::string marker = key + "=";
        const auto start = payload.find(marker);
        if (start == std::string::npos)
            return false;
        const auto valueStart = start + marker.size();
        const auto end = payload.find(';', valueStart);
        const auto text = payload.substr(valueStart,
            end == std::string::npos ? std::string::npos : end - valueStart);
        try {
            size_t consumed = 0;
            value = std::stod(text, &consumed);
            return consumed == text.size() && std::isfinite(value);
        }
        catch (...) {
            return false;
        }
    }

  protected:
    void processPacket(Packet *packet) override
    {
        const auto& chunk = packet->peekAtBack<BytesChunk>();
        if (!chunk)
            throw cRuntimeError("CropTelemetrySink received a packet without a telemetry BytesChunk");

        const auto& bytes = chunk->getBytes();
        const std::string payload(bytes.begin(), bytes.end());

        double sensorIdValue = 0;
        double temperatureC = 0;
        double humidityPct = 0;
        double soilMoisturePct = 0;
        if (!readField(payload, "sensor_id", sensorIdValue) ||
            !readField(payload, "temperature_c", temperatureC) ||
            !readField(payload, "relative_humidity_pct", humidityPct) ||
            !readField(payload, "soil_moisture_pct", soilMoisturePct))
            throw cRuntimeError("Malformed crop telemetry payload: %s", payload.c_str());

        const int sensorId = static_cast<int>(sensorIdValue);
        if (sensorIdValue != sensorId || sensorId < 0 || sensorId >= SENSOR_COUNT)
            throw cRuntimeError("Invalid crop telemetry sensor_id: %g", sensorIdValue);
        if (temperatureC < -20 || temperatureC > 80 ||
            humidityPct < 0 || humidityPct > 100 ||
            soilMoisturePct < 0 || soilMoisturePct > 100)
            throw cRuntimeError("Crop telemetry value outside configured sanity bounds: %s", payload.c_str());

        packetsPerSensor[sensorId]++;
        temperatureSums[sensorId] += temperatureC;
        humiditySums[sensorId] += humidityPct;
        soilMoistureSums[sensorId] += soilMoisturePct;
        totalTemperature += temperatureC;
        totalHumidity += humidityPct;
        totalSoilMoisture += soilMoisturePct;
        decodedPackets++;

        EV_INFO << "Decoded crop telemetry: " << payload << endl;
        UdpSink::processPacket(packet);
    }

    void finish() override
    {
        UdpSink::finish();
        recordScalar("decodedTelemetryPackets", decodedPackets);
        if (decodedPackets > 0) {
            recordScalar("meanTemperatureC", totalTemperature / decodedPackets);
            recordScalar("meanRelativeHumidityPct", totalHumidity / decodedPackets);
            recordScalar("meanSoilMoisturePct", totalSoilMoisture / decodedPackets);
        }
        for (int i = 0; i < SENSOR_COUNT; i++) {
            const std::string prefix = "sensor" + std::to_string(i);
            recordScalar((prefix + "DecodedPackets").c_str(), packetsPerSensor[i]);
            if (packetsPerSensor[i] > 0) {
                recordScalar((prefix + "MeanTemperatureC").c_str(),
                    temperatureSums[i] / packetsPerSensor[i]);
                recordScalar((prefix + "MeanRelativeHumidityPct").c_str(),
                    humiditySums[i] / packetsPerSensor[i]);
                recordScalar((prefix + "MeanSoilMoisturePct").c_str(),
                    soilMoistureSums[i] / packetsPerSensor[i]);
            }
        }
    }
};
Define_Module(CropTelemetrySink);
