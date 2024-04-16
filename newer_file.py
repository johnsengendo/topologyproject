# importing mininet libraries 
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import threading
import re
import os

class LinearTopology(Topo):
    def __init__(self):
        Topo.__init__(self)

        # Adding nodes to the topology
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')

        # Adding links between the nodes
        self.addLink(host1, switch1)
        self.addLink(switch1, switch2)
        self.addLink(switch2, host2)

def run_iperf_flow(h1, h2_ip, server_port, duration, interval, results_file):
    result_file = f"/tmp/iperf_flow_{server_port}.txt"
    bandwidth_factor = 0

    result_output = ""  # Store output for all intervals

    for time_elapsed in range(0, duration, 1):
        # Start iperf with dynamically changing bandwidth
        iperf_output = h1.popen(f'iperf -c {h2_ip} -p {server_port} -i {interval} -t 1 -b {bandwidth_factor}m -d', shell=True).communicate()[0].decode()
        result_output += iperf_output
        time.sleep(1)  # Wait for 1 second
        bandwidth_factor += 1

    results_file.write(result_output)

def create_linear_topology():
    # Creating an instance of the linear topology defined at the start
    topo = LinearTopology()

    # Starting the Mininet network
    net = Mininet(topo)

    # Starting the network
    net.start()

    # Defining the number of parallel flows(this can be changed)
    num_flows = 1

    # Opening a file in append mode to write our results
    with open('New_file', 'a') as results_file:
        duration = 60
        interval = 0.5

        # Starting the iperf servers on host 2 for each flow
        servers = []
        for flow_id in range(num_flows):
            server_port = 5000 + flow_id
            server = net.get('h2').popen(f'iperf -s -p {server_port}')
            servers.append(server)
            time.sleep(1)

        # Getting the IP address of h2
        h2_ip = net.get('h2').IP()

        # Creating and starting threads for each iperf flow
        threads = []
        for flow_id in range(num_flows):
            server_port = 5000 + flow_id
            thread = threading.Thread(target=run_iperf_flow, args=(net.get('h1'), h2_ip, server_port, duration, interval, results_file))
            thread.start()
            threads.append(thread)

        # Waiting for all threads to finish
        for thread in threads:
            thread.join()

        # Stopping the iperf servers
        for server in servers:
            server.terminate()

        results_file.write(f"End of {duration} seconds run\n")
        results_file.write("-----\n")

    # Opening the Mininet command line interface
    CLI(net)
    # Stopping the network once the CLI is closed
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_linear_topology()
