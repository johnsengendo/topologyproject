from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import re
import subprocess
import threading

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
        self.addLink(host1, switch2)  # Adding a link between h1 and s2
        self.addLink(switch1, host2)  # Adding a link between s1 and h2

def create_linear_topology():
    # Creating an instance of the linear topology
    topo = LinearTopology()

    # Starting the Mininet network using the created topology
    net = Mininet(topo)

    # Starting the network
    net.start()

    # Running iperf multiple times between the hosts
    # Opening a file in append mode to write the results
    with open('iperf_results_60_0.5_mutipleiperf', 'a') as results_file:
        duration = 60
        interval = 0.5
        num_runs = 2  # Number of times to run iperf
        num_connections = 5  # Number of simultaneous connections to test

        for i in range(num_runs):
            threads = []
            servers = []

            # Starting iperf servers on host 2 for each connection
            for j in range(num_connections):
                server = net.get('h2').popen(f'iperf -s -p {5000 + j}')
                servers.append(server)
                time.sleep(1)

            # Geting the IP address of h2
            h2_ip = net.get('h2').IP()

            # Running iperf test from host 1 to host 2 for each connection
            for j in range(num_connections):
                thread = threading.Thread(target=run_iperf, args=(net, h1_ip, h2_ip, duration, interval, 5000 + j, results_file))
                threads.append(thread)
                thread.start()

            # Wait for all iperf tests to finish
            for thread in threads:
                thread.join()

            # Stopping iperf servers on host 2
            for server in servers:
                server.terminate()

    # Opening the Mininet command line interface
    CLI(net)
    # Stopping the network once the CLI is closed
    net.stop()

def run_iperf(net, h1_ip, h2_ip, duration, interval, port, results_file):
    # Running iperf test from host 1 to host 2 using the IP address and print the results
    result = net.get('h1').cmd(f'iperf -c {h2_ip} -i {interval} -t {duration} -b 10m -p {port} -d')

    # Splitting the result by newline to get each interval's data
    lines = result.split('\n')
    # Writing the result to the file with a separator for readability
    results_file.write(f"Test (Port: {port}):\n{result}\n")
    results_file.write("-----\n")

    # Parsing the output for each interval
    for line in lines:
        match = re.search(r'(\d+\.\d+)-(\d+\.\d+) sec\s+(\d+\.\d+) MBytes\s+(\d+\.\d+) Mbits/sec', line)
        if match:
            # Extracting the duration, transferred data, and bandwidth
            start_time = float(match.group(1))
            end_time = float(match.group(2))
            duration = end_time - start_time
            transferred_data = float(match.group(3))
            bandwidth = float(match.group(4))

            # Writing the extracted information to the file
            results_file.write(f"Duration: {duration} seconds\n")
            results_file.write(f"Transferred Data: {transferred_data} MBytes\n")
            results_file.write(f"Average Bandwidth: {bandwidth} Mbits/sec\n")
            results_file.write(f"Direction: {'uplink'}\n")  # Assuming uplink for h1 to h2 direction

    print(result)

if __name__ == '__main__':
    setLogLevel('info')
    create_linear_topology()
