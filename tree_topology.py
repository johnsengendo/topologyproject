
#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

class TreeTopology(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Create template host, switch, and link
        host_config = dict(inNamespace=True)
        switch_link_config = dict(bw=10)  # Assuming all switch links are 10Mbps
        host_link_config = dict(bw=1)  # Assuming all host links are 1Mbps

        # Create switch nodes
        for i in range(4):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%d" % (i + 1), **sconfig)

        # Create host nodes
        for i in range(5):  # Adding an extra host for connection to s1
            self.addHost("h%d" % (i + 1), **host_config)

        # Add switch links to form a tree topology
        self.addLink("s1", "s2", **switch_link_config)
        self.addLink("s1", "s3", **switch_link_config)
        self.addLink("s3", "s4", **switch_link_config)

        # Add host links, including a host directly to the root switch s1
        self.addLink("h1", "s2", **host_link_config)
        self.addLink("h2", "s2", **host_link_config)
        self.addLink("h3", "s3", **host_link_config)
        self.addLink("h4", "s4", **host_link_config)
        self.addLink("h5", "s1", **host_link_config)  # Host connected to root switch

topos = {"treetopology": (lambda: TreeTopology())}

if __name__ == "__main__":
    topo = TreeTopology()
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        build=False,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )
    controller = RemoteController("c1", ip="127.0.0.1", port=6633)
    net.addController(controller)
    net.build()
    net.start()
    CLI(net)
    net.stop()
