from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

class TrafficSlicing:
    def __init__(self, *args, **kwargs):
        super(TrafficSlicing, self).__init__(*args, **kwargs)
        self.slice_to_port = {
            1: {1:3, 3:1, 2:4, 4:2},
            4: {1:3, 3:1, 2:4, 4:2},
            2: {1:2, 2:1},
            3: {1:2, 2:1}
        }

class CustomTopology(TrafficSlicing):
    def __init__(self):
        super(CustomTopology, self).__init__()
        self.net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink,
                           autoSetMacs=True, autoStaticArp=True)
        self.c0 = self.net.addController(name='c0', controller=RemoteController, ip='127.0.0.1', port=6633)

        # Create switches
        self.s1 = self.net.addSwitch('s1', cls=OVSSwitch)
        self.s2 = self.net.addSwitch('s2', cls=OVSSwitch)
        self.s3 = self.net.addSwitch('s3', cls=OVSSwitch)
        self.s4 = self.net.addSwitch('s4', cls=OVSSwitch)

        # Create hosts
        self.h1 = self.net.addHost('h1', ip='10.0.0.1')
        self.h2 = self.net.addHost('h2', ip='10.0.0.2')
        self.h3 = self.net.addHost('h3', ip='10.0.1.1')
        self.h4 = self.net.addHost('h4', ip='10.0.1.2')

        # Add links
        self.net.addLink(self.h1, self.s1)
        self.net.addLink(self.h2, self.s2)
        self.net.addLink(self.h3, self.s3)
        self.net.addLink(self.h4, self.s4)

        # Connect switches
        self.net.addLink(self.s1, self.s3)
        self.net.addLink(self.s2, self.s4)

    def run(self):
        self.net.start()
        # Now, we add the flow rules manually for demonstration purposes.
        self.s1.cmd('ovs-ofctl add-flow s1 ip,nw_src=10.0.0.1,nw_dst=10.0.1.1,actions=output:2')
        self.s3.cmd('ovs-ofctl add-flow s3 ip,nw_src=10.0.1.1,nw_dst=10.0.0.1,actions=output:1')
        self.s2.cmd('ovs-ofctl add-flow s2 ip,nw_src=10.0.0.2,nw_dst=10.0.1.2,actions=output:2')
        self.s4.cmd('ovs-ofctl add-flow s4 ip,nw_src=10.0.1.2,nw_dst=10.0.0.2,actions=output:1')
        CLI(self.net)
        self.net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topo = CustomTopology()
    topo.run()