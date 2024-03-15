#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
import time
import re

class NetworkSlicingTopo(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Create template host, switch, and link
        host_config = dict(inNamespace=True)
        http_link_config = dict(bw=1)
        video_link_config = dict(bw=10)
        host_link_config = dict()

        # Create switch nodes
        for i in range(4):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%d" % (i + 1), **sconfig)

        # Create host nodes
        for i in range(4):
            self.addHost("h%d" % (i + 1), **host_config)

        # Add switch links
        self.addLink("s1", "s2", **video_link_config)
        self.addLink("s2", "s4", **video_link_config)
        self.addLink("s1", "s3", **http_link_config)
        self.addLink("s3", "s4", **http_link_config)

        # Add host links
        self.addLink("h1", "s1", **host_link_config)
        self.addLink("h2", "s1", **host_link_config)
        self.addLink("h3", "s4", **host_link_config)
        self.addLink("h4", "s4", **host_link_config)

def run_iperf_tests(net):
    # Running iperf multiple times between the hosts
    with open('iperf_results_60_0.5', 'a') as results_file:
        for i in range(2):  # Adjust the range for desired number of tests
            server = net.get('h3').popen('iperf -s')
            time.sleep(1)
            h3_ip = net.get('h3').IP()
            result = net.get('h1').cmd(f'iperf -c {h3_ip} -i 3 -t 60 -b 10m -d')
            
            results_file.write(f"Test {i+1}:\n{result}\n")
            results_file.write("-----\n")
            
            match = re.search(r'(\d+\.\d+)-(\d+\.\d+) sec\s+(\d+\.\d+) GBytes\s+(\d+\.\d+) Gbits/sec', result)
            if match:
                start_time, end_time, transferred_data, bandwidth = match.groups()
                results_file.write(f"Duration: {float(end_time) - float(start_time)} seconds\n")
                results_file.write(f"Transferred Data: {transferred_data} GBytes\n")
                results_file.write(f"Average Bandwidth: {bandwidth} Gbits/sec\n")
                results_file.write("Direction: uplink\n")
            
            print(result)
            server.terminate()

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
    
    run_iperf_tests(net)  # Run the Iperf tests
    
    CLI(net)
    net.stop()
