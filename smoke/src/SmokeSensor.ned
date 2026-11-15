package wsn.smoke;

simple SmokeSensor
{
    parameters:
        int nodeId;
        double interval @unit(s) = default(1s);
        @display("i=device/sensor");
    gates:
        output out;
}
