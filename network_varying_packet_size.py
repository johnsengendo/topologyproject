from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from subprocess import Popen, PIPE
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

def run_parallel_iperf(net, packet_size):
    # Open the file to write the iperf results
    with open('iperf_parallel_results.txt', 'a') as results_file:
        # Start iperf servers on h3 and h4
        h3 = net.get('h3')
        h4 = net.get('h4')
        server_h3 = h3.popen('iperf -s')
        server_h4 = h4.popen('iperf -s')

        # Wait for the servers to start
        time.sleep(1)

        # Start iperf clients on h1 and h2 to connect to h3 and h4 respectively
        h1 = net.get('h1')
        h2 = net.get('h2')
        h3_ip = h3.IP()
        h4_ip = h4.IP()

        # Use Popen to run the clients so that we can run them simultaneously
        client_h1 = h1.popen(['iperf', '-c', h3_ip, '-t', '10', '-l', str(packet_size)], stdout=PIPE)
        client_h2 = h2.popen(['iperf', '-c', h4_ip, '-t', '10', '-l', str(packet_size)], stdout=PIPE)

        # Get the results
        result_h1 = client_h1.stdout.read().decode('utf-8')
        result_h2 = client_h2.stdout.read().decode('utf-8')

        results_file.write(f"Client h1 to h3 with packet size {packet_size} bytes:\n{result_h1}\n-----\n")
        results_file.write(f"Client h2 to h4 with packet size {packet_size} bytes:\n{result_h2}\n-----\n")

        # Terminate the server processes
        server_h3.terminate()
        server_h4.terminate()

        # Wait for the servers to terminate
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

    # Run the parallel Iperf tests with packet size 64
    run_parallel_iperf(net, 128)

    CLI(net)
    net.stop()
