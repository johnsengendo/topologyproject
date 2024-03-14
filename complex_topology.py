from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch, RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

class CustomTopology:
    def __init__(self):
        self.net = Mininet(controller=Controller, switch=OVSSwitch, link=TCLink)

        # Add controller
        self.net.addController('c0')

        # Host configuration (needs to be defined, example given)
        host_config = {'cpu': 0.5}

        # Create hosts
        for i in range(4):
            self.net.addHost('h%d' % (i+1), **host_config)

        # Create switches
        for i in range(4):
            sconfig = {'dpid': "%016x" % (i+1)}
            self.net.addSwitch('s%d' % (i+1), **sconfig)

        # Define links
        http_link_config = dict(bw=1)
        video_link_config = dict(bw=10)

        # Add switch links
        self.net.addLink('s1', 's2', **video_link_config)
        self.net.addLink('s2', 's4', **video_link_config)
        self.net.addLink('s1', 's3', **http_link_config)
        self.net.addLink('s3', 's4', **http_link_config)

        # Add host links
        for i in range(4):
            self.net.addLink('h1', 's1', **host_config)
            self.net.addLink('h2', 's1', **host_config)
            self.net.addLink('h3', 's4', **host_config)
            self.net.addLink('h4', 's4', **host_config)

    def run(self):
        # Setting up the Mininet instance to use the RemoteController
        self.net = Mininet(
            controller=RemoteController,
            switch=OVSSwitch,
            link=TCLink,
            autoSetMacs=True,  # This sets the MACs as per IP addresses
            autoStaticArp=True # This populates the ARP table with all pairs to prevent ARP broadcasts
        )

        # Add the remote controller with the IP and port specified
        c0 = RemoteController('c1', ip='127.0.0.1', port=6633)
        self.net.addController(c0)

        self.net.start()
        CLI(self.net)
        self.net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topo = CustomTopology()
    topo.run()
