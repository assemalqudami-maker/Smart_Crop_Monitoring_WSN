package wsn.smoke;

// Smoke test ONLY. These are direct wired links, not radio or ZigBee links.
network SmokeNetwork
{
    parameters:
        @display("bgb=620,360");
    submodules:
        sink: SmokeSink {
            @display("p=480,180");
        }
        sensor[3]: SmokeSensor {
            parameters:
                nodeId = index;
                @display("p=120,100,row,130");
        }
    connections allowunconnected:
        for i=0..2 {
            sensor[i].out --> { delay = 1ms; } --> sink.in++;
        }
}
