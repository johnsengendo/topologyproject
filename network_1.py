#!/usr/bin/python3
'''
Network topology in Mininet
Constructed with reference from https://git.comnets.net/public-repo/comnetsemu
'''
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from subprocess import Popen, PIPE
import time
import re

class NetworkSlicingTopo(Topo):
    """
    Class defining the network topology.
    """
    def __init__(self):
        # Initializing the topology with the Topo class from Mininet
        Topo.__init__(self)
        
        # Creating template configurations for hosts, switches, and links
        host_config = dict(inNamespace=True) # Host configuration: using network namespaces
        link_config = dict(bw=10) # Link configuration: setting bandwidth to 10 Mbps
        host_link_config = dict(bw=10) # Host-switch link configuration: setting bandwidth to 10 Mbps

        # Creating switch nodes
        for i in range(4):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%d" % (i + 1), **sconfig)

        # Creating host nodes
        for i in range(4):
            self.addHost("h%d" % (i + 1), **host_config)

        # Adding switch links
        self.addLink("s1", "s2", **link_config)
        self.addLink("s2", "s4", **link_config)
        self.addLink("s1", "s3", **link_config)
        self.addLink("s3", "s4", **link_config)

        # Adding host links
        self.addLink("h1", "s1", **host_link_config)
        self.addLink("h2", "s1", **host_link_config)
        self.addLink("h3", "s4", **host_link_config)
        self.addLink("h4", "s4", **host_link_config)

def run_parallel_iperf(net):
    # Opening the file to write the iperf results
    # Starting iperf servers on h3 and h4
    h3 = net.get('h3')
    h4 = net.get('h4')
    server_h3 = h3.popen('iperf -s')
    server_h4 = h4.popen('iperf -s')

    # Waiting for the servers to start
    time.sleep(1)

    # Starting iperf clients on h1 and h2 to connect to h3 and h4 respectively
    h1 = net.get('h1')
    h2 = net.get('h2')
    h3_ip = h3.IP()
    h4_ip = h4.IP()
    with open('iperf_parallel_results_1.txt', 'a') as results_file:

        result_h1 = h1.cmd(f'iperf -c {h3_ip} -t 10 -i 1 -d')
        result_h2 = h2.cmd(f'iperf -c {h4_ip} -t 10 -i 1 -d')

        results_file.write(f"Client h1 to h3:\n{result_h1}\n-----\n")
        results_file.write(f"Client h2 to h4:\n{result_h2}\n-----\n")

        # Terminating the server processes
        server_h3.terminate()
        server_h4.terminate()

        # Waiting for the servers to terminate
        server_h3.wait()
        server_h4.wait()

topos = {"networkslicingtopo": (lambda: NetworkSlicingTopo())}

if __name__ == "__main__":
    topo = NetworkSlicingTopo()
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
    
    # Running the parallel Iperf tests
    run_parallel_iperf(net)
    
    CLI(net)
    net.stop()
