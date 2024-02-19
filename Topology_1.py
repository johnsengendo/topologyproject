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
    with open('iperf_results.txt', 'a') as results_file:
        for i in range(5):  # running the test 5 times
            # Starting the iperf server on host 2
            server = net.get('h2').popen('iperf -s')
            # Allowing time for the server to start
            time.sleep(1)
            # Get the IP address of h2
            h2_ip = net.get('h2').IP()
            # Run iperf test from host 1 to host 2 using the IP address and print the results
            client_output = net.get('h1').cmd('iperf -c {} -t 1'.format(h2_ip))
            # Parse the output to extract relevant information
            match = re.search(r'\[SUM\].*?(\d+\.\d+)\s+Mbits/sec\s+(\d+)\s+KBytes', client_output)
            if match:
                avg_flow_rate = float(match.group(1))
                duration = int(match.group(2))
                direction = "Uplink" if avg_flow_rate > 0 else "Downlink"
                # Print results to console
                print(f"Average Flow Rate: {avg_flow_rate:.2f} Mbits/sec")
                print(f"Duration: {duration} seconds")
                print(f"Source IP: {net.get('h1').IP()}")
                print(f"Destination IP: {h2_ip}")
                print(f"Direction: {direction}")
                # Write results to file
                results_file.write(f"Average Flow Rate: {avg_flow_rate:.2f} Mbits/sec\n")
                results_file.write(f"Duration: {duration} seconds\n")
                results_file.write(f"Source IP: {net.get('h1').IP()}\n")
                results_file.write(f"Destination IP: {h2_ip}\n")
                results_file.write(f"Direction: {direction}\n")
            else:
                print("Error parsing iperf output")
            # Stop the iperf server
            server.terminate()
    # Opening the Mininet command line interface
    CLI(net)
    # Stopping the network once the CLI is closed
    net.stop()       

if __name__ == '__main__':
    setLogLevel('info')
    create_linear_topology()
    #CLI()