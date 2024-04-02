from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import re
import subprocess

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
    with open('iperf_results_60_0.5_21', 'a') as results_file:
        duration = 60
        interval = 0.5
        num_runs = 2  # Number of times to run iperf

        for i in range(num_runs):
            # Starting the iperf server on host 2
            server = net.get('h2').popen('iperf -s')
            # Allowing time for the server to start
            time.sleep(1)
            # Geting the IP address of h2
            h2_ip = net.get('h2').IP()

            # Starting a file transfer from host 1 to host 2
            net.get('h1').cmd(f'scp /largefile {h2_ip}:/dev/null &')

            # Running iperf test from host 1 to host 2 using the IP address and print the results
            result = net.get('h1').cmd(f'iperf -c {h2_ip} -i {interval} -t {duration} -b 10m -d')

            # Splitting the result by newline to get each interval's data
            lines = result.split('\n')
            # Writing the result to the file with a separator for readability
            results_file.write(f"Test {i+1}:\n{result}\n")
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
            # Stoping the iperf server
            server.terminate()

    # Opening the Mininet command line interface
    CLI(net)
    # Stopping the network once the CLI is closed
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_linear_topology()
