from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import threading
import os

class LinearTopology(Topo):
    def build(self):
        super(LinearTopology, self).build()
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        self.addLink(host1, switch1)
        self.addLink(switch1, switch2)
        self.addLink(switch2, host2)

def run_iperf_flow(h1, h2_ip, server_port, duration, interval, results_filename):
    result_file_path = f"/tmp/iperf_flow_{server_port}.txt"
    h1.cmd(f'iperf -c {h2_ip} -p {server_port} -i {interval} -t {duration} -b 1M > {result_file_path} &')
    h1.cmd(f'wait $(pgrep -f "iperf -c {h2_ip} -p {server_port}")')
    
    # Read and store the results
    with open(result_file_path, 'r') as file:
        results = file.read()
    
    with open(results_filename, 'a') as results_file:
        results_file.write(f"Flow Result:\n{results}\n")
        results_file.write("-----\n")
    
    # Clean up the temporary file
    os.remove(result_file_path)

def schedule_flows(net):
    h1, h2 = net.get('h1'), net.get('h2')
    h2_ip = h2.IP()

    # Continuous flow setup
    threading.Thread(target=run_iperf_flow, args=(h1, h2_ip, 5000, 300, 0.5, "continuous_flow_results.txt")).start()

    # First burst
    time.sleep(30)
    run_iperf_flow(h1, h2_ip, 5001, 10, 1, "first_burst_results.txt")
    
    # First random flows
    time.sleep(15)  # Wait for first burst to finish + 5 seconds
    run_iperf_flow(h1, h2_ip, 5002, 20, 1, "first_random_flows_results.txt")
    
    # Second burst
    time.sleep(30)  # Wait for first random to finish + 10 seconds
    run_iperf_flow(h1, h2_ip, 5003, 10, 1, "second_burst_results.txt")
    
    # Second random flows
    time.sleep(15)  # Wait for second burst to finish + 5 seconds
    run_iperf_flow(h1, h2_ip, 5004, 10, 1, "second_random_flows_results.txt")

def setup_network():
    topo = LinearTopology()
    net = Mininet(topo)
    net.start()
    schedule_flows(net)
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    setup_network()
