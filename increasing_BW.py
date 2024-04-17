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

# Define a function to run iperf flow with dynamic bandwidth adjustment
def run_iperf_flow(h1, h2_ip, server_port, duration, interval, results_file, bandwidth):
    result_file = f"/tmp/iperf_flow_{server_port}.txt"
    h1.popen(f'iperf -c {h2_ip} -p {server_port} -i {interval} -t {duration} -b {bandwidth} -d > {result_file}', shell=True)
    time.sleep(duration + 1)  # Wait for the iperf process to finish

    with open(result_file, 'r') as f:
        result = f.read()

    os.remove(result_file)  # Remove the temporary result file

    results_file.write(f"Flow Result:\n{result}\n")
    results_file.write("-----\n")

    match = re.search(r'(\d+\.\d+)-(\d+\.\d+) sec\s+(\d+\.\d+) MBytes\s+(\d+\.\d+) Mbits/sec', result)
    if match:
        start_time = float(match.group(1))
        end_time = float(match.group(2))
        duration = end_time - start_time
        transferred_data = float(match.group(3))
        bandwidth = float(match.group(4))

        results_file.write(f"Duration: {duration} seconds\n")
        results_file.write(f"Transferred Data: {transferred_data} MBytes\n")
        results_file.write(f"Average Bandwidth: {bandwidth} Mbits/sec\n")
        results_file.write(f"Direction: {'uplink'}\n")

    print(result)

def create_linear_topology():
    topo = LinearTopology()

    # Starting the Mininet network
    net = Mininet(topo)

    # Starting the network
    net.start()
    # Your existing code for creating topology, starting Mininet, etc.


    # Defining the number of parallel flows
    num_flows = 1

    # Opening a file in append mode to write results
    with open('Multi_flows5', 'a') as results_file:

        durations = [20]  # Durations over which iperf is run
        intervals = [1]  # Intervals at which data is captured for each duration
        num_runs = 1  # Number of repetitions for which iperf is run for each duration

        for duration, interval in zip(durations, intervals):
            for j in range(num_runs):
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
                    # Calculate dynamic bandwidth based on duration
                    bandwidth = (j + 1) * 10  # Adjust as needed
                    thread = threading.Thread(target=run_iperf_flow, args=(net.get('h1'), h2_ip, server_port, duration, interval, results_file, f"{bandwidth}M"))
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

    # Your existing code for CLI and stopping Mininet network
    # Opening the Mininet command line interface
    CLI(net)
    # Stopping the network once the CLI is closed
    net.stop()
if __name__ == '__main__':
    setLogLevel('info')
    create_linear_topology()
