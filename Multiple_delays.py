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

    # Introduce artificial delays using tc command
    delays = [10, 50, 100, 200]  # Delays in milliseconds
    num_loops = 12  # Number of loops to repeat the process

    for loop in range(1, num_loops + 1):
        for delay in delays:
            # Add delay to link between switch1 and switch2
            net.get('s1').cmd(f'tc qdisc add dev s1-eth2 root netem delay {delay}ms')
            net.get('s2').cmd(f'tc qdisc add dev s2-eth1 root netem delay {delay}ms')

            # Running iperf multiple times between the hosts
            # Opening a file in append mode to write the results
            with open('iperf_results_60_0.5', 'a') as results_file:
                duration = 60
                interval = 0.5
                num_runs = 1  # Number of times to run iperf

                for i in range(num_runs):
                    threads = []
                    servers = []

                    # Starting iperf servers on host 2
                    server = net.get('h2').popen('iperf -s')
                    servers.append(server)
                    time.sleep(1)

                    # Geting the IP address of h2
                    h2_ip = net.get('h2').IP()

                    # Running iperf test from host 1 to host 2
                    thread = threading.Thread(target=run_iperf, args=(net.get('h1'), h2_ip, duration, interval, results_file, delay, loop))
                    threads.append(thread)
                    thread.start()

                    # Wait for all iperf tests to finish
                    for thread in threads:
                        thread.join()

                    # Stopping iperf servers on host 2
                    for server in servers:
                        server.terminate()

            # Remove delay from link between switch1 and switch2
            net.get('s1').cmd('tc qdisc del dev s1-eth2 root')
            net.get('s2').cmd('tc qdisc del dev s2-eth1 root')

    # Opening the Mininet command line interface
    CLI(net)
    # Stopping the network once the CLI is closed
    net.stop()

def run_iperf(h1, h2_ip, duration, interval, results_file, delay, loop):
    # Running iperf test from host 1 to host 2 using the IP address and print the results
    result = h1.cmd(f'iperf -c {h2_ip} -i {interval} -t {duration} -b 10m -d')

    # Splitting the result by newline to get each interval's data
    lines = result.split('\n')
    # Writing the result to the file with a separator for readability
    results_file.write(f"Test:\n{result}\n")
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
            results_file.write(f"Loop: {loop}\n")
            results_file.write(f"Delay: {delay} ms\n")
            results_file.write(f"Duration: {duration} seconds\n")
            results_file.write(f"Transferred Data: {transferred_data} MBytes\n")
            results_file.write(f"Average Bandwidth: {bandwidth} Mbits/sec\n")
            results_file.write(f"Direction: {'uplink'}\n")  # Assuming uplink for h1 to h2 direction

    print(result)

if __name__ == '__main__':
    setLogLevel('info')
    create_linear_topology()
