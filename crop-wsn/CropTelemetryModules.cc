#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
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

namespace {
constexpr uint8_t TELEMETRY_VERSION = 1;
constexpr size_t TELEMETRY_BYTES = 13;

void putU16(std::vector<uint8_t>& out, uint16_t value)
{
    out.push_back(static_cast<uint8_t>((value >> 8) & 0xff));
    out.push_back(static_cast<uint8_t>(value & 0xff));
}

void putU32(std::vector<uint8_t>& out, uint32_t value)
{
    out.push_back(static_cast<uint8_t>((value >> 24) & 0xff));
    out.push_back(static_cast<uint8_t>((value >> 16) & 0xff));
    out.push_back(static_cast<uint8_t>((value >> 8) & 0xff));
    out.push_back(static_cast<uint8_t>(value & 0xff));
}

uint16_t getU16(const std::vector<uint8_t>& in, size_t offset)
{
    return (static_cast<uint16_t>(in.at(offset)) << 8) |
           static_cast<uint16_t>(in.at(offset + 1));
}

uint32_t getU32(const std::vector<uint8_t>& in, size_t offset)
{
    return (static_cast<uint32_t>(in.at(offset)) << 24) |
           (static_cast<uint32_t>(in.at(offset + 1)) << 16) |
           (static_cast<uint32_t>(in.at(offset + 2)) << 8) |
           static_cast<uint32_t>(in.at(offset + 3));
}
}

class CropTelemetryApp : public UdpBasicApp
{
  protected:
    void sendPacket() override
    {
        const int sensorId = par("sensorId").intValue();
        const int sequence = numSent;
        const double temperatureC = par("baseTemperatureC").doubleValue() + 0.15 * sequence;
        const double humidityPct = std::clamp(
            par("baseHumidityPct").doubleValue() - 0.20 * sequence, 0.0, 100.0);
        const double soilMoisturePct = std::clamp(
            par("baseSoilMoisturePct").doubleValue() + 0.35 * sequence, 0.0, 100.0);

        if (sensorId < 0 || sensorId > 255 || sequence < 0 || sequence > 255)
            throw cRuntimeError("Crop telemetry sensor ID/sequence does not fit uint8");

        std::vector<uint8_t> payload;
        payload.reserve(TELEMETRY_BYTES);
        payload.push_back(TELEMETRY_VERSION);
        payload.push_back(static_cast<uint8_t>(sensorId));
        payload.push_back(static_cast<uint8_t>(sequence));
        putU16(payload, static_cast<uint16_t>(static_cast<int16_t>(std::lround(temperatureC * 100.0))));
        putU16(payload, static_cast<uint16_t>(std::lround(humidityPct * 100.0)));
        putU16(payload, static_cast<uint16_t>(std::lround(soilMoisturePct * 100.0)));
        putU32(payload, static_cast<uint32_t>(std::llround(simTime().dbl() * 1000.0)));

        auto *packet = new Packet((std::string(packetName ? packetName : "CropTelemetry")
                                   + "-" + std::to_string(sequence)).c_str());
        const auto& header = makeShared<ApplicationPacket>();
        header->setChunkLength(B(4));
        header->setSequenceNumber(sequence);
        header->addTag<CreationTimeTag>()->setCreationTime(simTime());
        packet->insertAtBack(header);
        packet->insertAtBack(makeShared<BytesChunk>(payload));

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
    std::array<unsigned int, SENSOR_COUNT> sequenceMasks{};
    std::array<double, SENSOR_COUNT> temperatureSums{};
    std::array<double, SENSOR_COUNT> humiditySums{};
    std::array<double, SENSOR_COUNT> soilMoistureSums{};
    double totalTemperature = 0;
    double totalHumidity = 0;
    double totalSoilMoisture = 0;

  protected:
    void processPacket(Packet *packet) override
    {
        const auto& chunk = packet->peekAtBack<BytesChunk>();
        if (!chunk)
            throw cRuntimeError("CropTelemetrySink received a packet without BytesChunk");
        const auto& bytes = chunk->getBytes();
        if (bytes.size() != TELEMETRY_BYTES)
            throw cRuntimeError("Invalid crop telemetry payload size: %zu", bytes.size());
        if (bytes[0] != TELEMETRY_VERSION)
            throw cRuntimeError("Unsupported crop telemetry version: %u", bytes[0]);

        const int sensorId = bytes[1];
        const int sequence = bytes[2];
        const int16_t temperatureRaw = static_cast<int16_t>(getU16(bytes, 3));
        const double temperatureC = temperatureRaw / 100.0;
        const double humidityPct = getU16(bytes, 5) / 100.0;
        const double soilMoisturePct = getU16(bytes, 7) / 100.0;
        const uint32_t sampleTimeMs = getU32(bytes, 9);

        if (sensorId < 0 || sensorId >= SENSOR_COUNT)
            throw cRuntimeError("Invalid crop telemetry sensor ID: %d", sensorId);
        if (temperatureC < -20 || temperatureC > 80 ||
            humidityPct < 0 || humidityPct > 100 ||
            soilMoisturePct < 0 || soilMoisturePct > 100)
            throw cRuntimeError("Crop telemetry value outside sanity bounds");
        if (sequence < 0 || sequence >= 32)
            throw cRuntimeError("Crop telemetry sequence outside supported window");
        const unsigned int mask = 1u << sequence;
        if (sequenceMasks[sensorId] & mask)
            throw cRuntimeError("Duplicate crop telemetry sample: sensor=%d sequence=%d", sensorId, sequence);
        sequenceMasks[sensorId] |= mask;

        packetsPerSensor[sensorId]++;
        temperatureSums[sensorId] += temperatureC;
        humiditySums[sensorId] += humidityPct;
        soilMoistureSums[sensorId] += soilMoisturePct;
        totalTemperature += temperatureC;
        totalHumidity += humidityPct;
        totalSoilMoisture += soilMoisturePct;
        decodedPackets++;

        EV_INFO << "Decoded crop telemetry: sensor=" << sensorId
                << " sequence=" << sequence
                << " temperature_C=" << temperatureC
                << " humidity_pct=" << humidityPct
                << " soil_moisture_pct=" << soilMoisturePct
                << " sample_time_ms=" << sampleTimeMs << endl;
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
