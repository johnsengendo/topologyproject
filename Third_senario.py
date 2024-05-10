from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import threading
import random
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

def run_iperf_flow(h1, h2_ip, server_port, duration, interval, results_file, bandwidth):
    result_file = f"/tmp/iperf_flow_{server_port}.txt"
    h1.popen(f'iperf -c {h2_ip} -p {server_port} -i {interval} -t {duration} -b {bandwidth} -d > {result_file}', shell=True)
    time.sleep(duration + 1)  # Waiting for the iperf process to finish

    with open(result_file, 'r') as f:
        result = f.read()

    os.remove(result_file)  # Removing the temporary result file

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

    # Defining the number of parallel flows (since here an only testing bandwidth increase, num_flows is set to 1)
    num_flows = 1

    # Opening a file in append mode to write the results
    with open('Third_senario_BW', 'a') as results_file:

        durations = [10]  # Durations over which iperf is run
        intervals = [0.5]  # Intervals at which data is captured for each duration
        num_steps = 150  #  Number of steps (after each step, the bandwidth is increased by a factor of 10)

# Start the continuous flow
        h1, h2 = net.get('h1'), net.get('h2')
        h2_ip = h2.IP()
        server_port = 5000

# Define the server
        server = h2.popen(f'iperf -s -p {server_port}')

# Start the server in a thread
        threading.Thread(target=server.start, args=(1,)).start()

# Start the iperf flow in a thread
        threading.Thread(target=run_iperf_flow, args=(h1, h2_ip, server_port, 900, 1, results_file, "10M")).start()


        # Schedule the burst traffic to start after a certain period
        time.sleep(30)
        server_port += 1
        h2.popen(f'iperf -s -p {server_port}')
        threading.Thread(target=run_iperf_flow, args=(h1, h2_ip, server_port, 10, 1, results_file, "100M")).start()

        # Implement the random smaller flows using a script that randomly starts and stops traffic flows
        def start_random_flow():
            server_port += 1
            h2.popen(f'iperf -s -p {server_port}')
            duration = random.uniform(1, 5)
            bandwidth = f"{random.randint(1, 100)}M"
            threading.Thread(target=run_iperf_flow, args=(h1, h2_ip, server_port, duration, 1, results_file, bandwidth)).start()
            time.sleep(random.uniform(1, 5))

        # Start the random smaller flows
        for _ in range(10):
            threading.Thread(target=start_random_flow).start()

    # Opening the Mininet command line interface
    CLI(net)
    # Stopping the network once the CLI is closed
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_linear_topology()
