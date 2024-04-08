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
    h1.popen(f'iperf -c {h2_ip} -p {server_port} -i {interval} -t {duration} -b 10m -d > {result_file}', shell=True)
    time.sleep(duration + 1)  # Wait for the iperf process to finish

    with open(result_file, 'r') as f:
        result = f.read()

    os.remove(result_file)  # Remove the temporary result file

    results_file.write(f"Flow Result:\n{result}\n")
    results_file.write("-----\n")

    match = re.search(r'(\d+\.\d+)-(\d+\.\d+) sec\s+(\d+\.\d+) GBytes\s+(\d+\.\d+) Gbits/sec', result)
    if match:
        start_time = float(match.group(1))
        end_time = float(match.group(2))
        duration = end_time - start_time
        transferred_data = float(match.group(3))
        bandwidth = float(match.group(4))

        results_file.write(f"Duration: {duration} seconds\n")
        results_file.write(f"Transferred Data: {transferred_data} GBytes\n")
        results_file.write(f"Average Bandwidth: {bandwidth} Gbits/sec\n")
        results_file.write(f"Direction: {'uplink'}\n")

    print(result)

def create_linear_topology():
    # Creating an instance of the linear topology
    topo = LinearTopology()

    # Starting the Mininet network using the created topology
    net = Mininet(topo)

    # Starting the network
    net.start()

    # Define the number of parallel flows
    num_flows = 2

    # Opening a file in append mode to write the results
    with open('multi_flows(2)_updated_data', 'a') as results_file:
        durations = [60]#, 20, 30, 40, 50, 60]
        intervals = [3]#, 1, 1.5, 2, 2.5, 3]

        num_runs = 4
        for duration, interval in zip(durations, intervals):
            for j in range(num_runs):
                # Start the iperf servers on host 2 for each flow
                servers = []
                for flow_id in range(num_flows):
                    server_port = 5000 + flow_id
                    server = net.get('h2').popen(f'iperf -s -p {server_port}')
                    servers.append(server)
                    time.sleep(1)

                # Get the IP address of h2
                h2_ip = net.get('h2').IP()

                # Create and start threads for each iperf flow
                threads = []
                for flow_id in range(num_flows):
                    server_port = 5000 + flow_id
                    thread = threading.Thread(target=run_iperf_flow, args=(net.get('h1'), h2_ip, server_port, duration, interval, results_file))
                    thread.start()
                    threads.append(thread)

                # Wait for all threads to finish
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
