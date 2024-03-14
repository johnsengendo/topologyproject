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

# Assuming the CustomTopology class should use TrafficSlicing
class CustomTopology(TrafficSlicing):
    def __init__(self):
        super(CustomTopology, self).__init__()
        self.net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink,
                           autoSetMacs=True, autoStaticArp=True)
        c0 = self.net.addController(name='c0', controller=RemoteController, ip='127.0.0.1', port=6633)
        # ... rest of your initializations for hosts and switches ...
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
        self.net.start()
        CLI(self.net)
        self.net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topo = CustomTopology()
    topo.run()
