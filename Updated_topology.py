from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import re

class LinearTopology(Topo):
    def __init__(self):
        Topo.__init__(self)

        # Adding nodes
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')

        # Adding links
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
    # Opening a file in append mode
    with open('iperf_results_30.txt', 'a') as results_file:
        for i in range(10):  # running the test 5 times
            # Starting the iperf server on host 2
            server = net.get('h2').popen('iperf -s')
            # Allowing time for the server to start
            time.sleep(1)
            # Get the IP address of h2
            h2_ip = net.get('h2').IP()
            # Run iperf test from host 1 to host 2 using the IP address and print the results
            # running the test for 1 secon
            #result = net.get('h1').cmd(f'iperf -c {h2_ip} -i 1 -b 10m')
            # running the test for 20 seconds and collect data at intervals of 2 seconds
            #result = net.get('h1').cmd(f'iperf -c {h2_ip} -i 2 -t 20 -b 10m')
            # running the test for 30 seconds and collect data at intervals of 2 seconds
            result = net.get('h1').cmd(f'iperf -c {h2_ip} -i 1.5 -t 30 -b 10m')
            
            # Writing the result to the file with a separator for readability
            results_file.write(f"Test {i+1}:\n{result}\n")
            results_file.write("-----\n")
            
            # Use regular expressions to parse the output for the relevant information
            match = re.search(r'(\d+\.\d+)-(\d+\.\d+) sec\s+(\d+\.\d+) GBytes\s+(\d+\.\d+) Gbits/sec', result)
            if match:
                # Extract the duration, transferred data, and bandwidth
                start_time = float(match.group(1))
                end_time = float(match.group(2))
                duration = end_time - start_time
                transferred_data = float(match.group(3))
                bandwidth = float(match.group(4))
                
                # Write the extracted information to the file
                results_file.write(f"Duration: {duration} seconds\n")
                results_file.write(f"Transferred Data: {transferred_data} GBytes\n")
                results_file.write(f"Average Bandwidth: {bandwidth} Gbits/sec\n")
                results_file.write(f"Direction: {'uplink'}\n")  # Assuming uplink for h1 to h2 direction
            
            print(result)
            # Stopping the iperf server
            server.terminate()

    # Opening the Mininet command line interface
    CLI(net)
    # Stopping the network once the CLI is closed
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_linear_topology()
