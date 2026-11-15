package wsn.crop;

import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import inet.node.inet.SensorNode;
import inet.physicallayer.wireless.ieee802154.packetlevel.Ieee802154NarrowbandScalarRadioMedium;
import inet.visualizer.canvas.integrated.IntegratedMultiCanvasVisualizer;

// Twelve IEEE 802.15.4 sensor nodes and a single sink.
// IP manual routes provide explicit MULTI-HOP forwarding, not ZigBee NWK.
network FarmNetwork
{
    @display("bgb=260,205");
    submodules:
        sink: SensorNode {
            @display("p=10,100;i=misc/sensorgateway");
        }
        sensor[12]: SensorNode {
            @display("p=60,100,row,65;i=misc/sensor2");
        }
        configurator: Ipv4NetworkConfigurator {
            @display("p=225,15");
        }
        radioMedium: Ieee802154NarrowbandScalarRadioMedium {
            @display("p=225,45");
        }
        visualizer: IntegratedMultiCanvasVisualizer {
            @display("p=225,75");
        }
}
