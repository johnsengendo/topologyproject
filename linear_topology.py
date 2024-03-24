# =============================================================================
# Mininet Iperf Test Script
# -----------------------------------------------------------------------------
# This script runs iperf tests between two hosts in a Mininet network using a
# linear topology. The script runs the iperf test for multiple durations and
# collects data at half a second interval. The results of the tests are
# written to a textfile for later analysis.
#
# The script uses the Mininet library to create and start the network, and the
# iperf command to run the tests.
#
# The script could be customized to run the iperf test multiple times for each
# duration, and to specify the number of runs and the durations to be tested.
# =============================================================================

'''
Performing imports for Mininet-based network simulation:
- Topo: Class from mininet.topo module for creating custom network topologies.
- Mininet: Class from mininet.net module, the core of the network simulation.
- CLI: Class from mininet.cli module to enable command line interaction within the network simulation.
- setLogLevel: Function from mininet.log module for setting the verbosity of log messages.
- time: A standard Python module for handling time-related tasks, such as delays.
- re: Standard Python module for regular expression operations, useful for string searching and manipulation.
'''
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import re

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

def create_linear_topology():
    # Creating an instance of the linear topology
    topo = LinearTopology()

    # Starting the Mininet network using the created topology
    net = Mininet(topo)

    # Starting the network
    net.start()

    # Running iperf multiple times between the hosts
    # Opening a file in append mode to write the results
    with open('iperf_results_10_0.5', 'a') as results_file:
        durations = 20 #[10, 20, 30, 40, 50, 60]
        
        num_runs = 1 # We can change this value to the desired number of runs
        for i, duration in enumerate(durations):
            for j in range(num_runs):
                # Starting the iperf server on host 2
                server = net.get('h2').popen('iperf -s')
                # Allowing time for the server to start
                time.sleep(1)
                # Geting the IP address of h2
                h2_ip = net.get('h2').IP()
                # Running iperf test from host 1 to host 2 using the IP address and print the results
                result = net.get('h1').cmd(f'iperf -c {h2_ip} -i 1 -t {duration} -b 10m -d')

                # Writing the result to the file with a separator for readability
                results_file.write(f"Test {i+1}:\n{result}\n")
                results_file.write("-----\n")

                # Using regular expressions to parse the output for the relevant information
                match = re.search(r'(\d+\.\d+)-(\d+\.\d+) sec\s+(\d+\.\d+) GBytes\s+(\d+\.\d+) Gbits/sec', result)
                if match:
                    # Extracting the duration, transferred data, and bandwidth
                    start_time = float(match.group(1))
                    end_time = float(match.group(2))
                    duration = end_time - start_time
                    transferred_data = float(match.group(3))
                    bandwidth = float(match.group(4))

                    # Writing the extracted information to the file
                    results_file.write(f"Duration: {duration} seconds\n")
                    results_file.write(f"Transferred Data: {transferred_data} GBytes\n")
                    results_file.write(f"Average Bandwidth: {bandwidth} Gbits/sec\n")
                    results_file.write(f"Direction: {'uplink'}\n")  # Assuming uplink for h1 to h2 direction

                print(result)
                # Stoping the iperf server
                server.terminate()

    # Opening the Mininet command line interface
    CLI(net)
    # Stopping the network once the CLI is closed
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_linear_topology()
