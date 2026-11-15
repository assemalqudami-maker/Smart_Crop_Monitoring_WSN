#include <omnetpp.h>

using namespace omnetpp;

class SmokeSensor : public cSimpleModule
{
  private:
    cMessage *timer = nullptr;
    long sent = 0;
  protected:
    void initialize() override {
        sent = 0;
        timer = new cMessage("sampleTimer");
        scheduleAt(simTime() + par("interval"), timer);
    }
    void handleMessage(cMessage *msg) override {
        if (msg != timer)
            throw cRuntimeError("Unexpected message in SmokeSensor");
        auto *packet = new cPacket("sample");
        packet->setByteLength(32);
        send(packet, "out");
        ++sent;
        scheduleAt(simTime() + par("interval"), timer);
    }
    void finish() override {
        recordScalar("generatedPackets", sent);
    }
  public:
    ~SmokeSensor() override {
        cancelAndDelete(timer);
    }
};
Define_Module(SmokeSensor);

class SmokeSink : public cSimpleModule
{
  private:
    long received = 0;
  protected:
    void initialize() override {
        received = 0;
    }
    void handleMessage(cMessage *msg) override {
        ++received;
        delete msg;
    }
    void finish() override {
        recordScalar("deliveredPackets", received);
    }
};
Define_Module(SmokeSink);
