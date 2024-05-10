from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import threading

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

def run_traffic_flow(h1, h2_ip, duration, interval, bandwidth, output_file):
    print(f"Starting flow: {output_file} for {duration} seconds at {bandwidth} Mbps...")
    h1.cmd(f'iperf -c {h2_ip} -t {duration} -i {interval} -b {bandwidth}M > {output_file} &')

def schedule_flows(net):
    h1, h2 = net.get('h1'), net.get('h2')
    h2_ip = h2.IP()
    
    # Continuous flow setup
    threading.Thread(target=run_traffic_flow, args=(h1, h2_ip, 300, 0.5, 1, "continuous_flow.txt")).start()

    # First burst after 30 seconds
    time.sleep(30)
    run_traffic_flow(h1, h2_ip, 10, 1, 100, "first_burst_results.txt")
    
    # First random flows after 5 seconds
    time.sleep(15)  # 10 sec burst + 5 sec wait
    run_traffic_flow(h1, h2_ip, 20, 1, 10, "first_random_flows_results.txt")
    
    # Second burst after 30 seconds
    time.sleep(25)  # 20 sec random flows + 5 sec wait
    run_traffic_flow(h1, h2_ip, 10, 1, 100, "second_burst_results.txt")
    
    # Second random flows after 5 seconds
    time.sleep(15)  # 10 sec burst + 5 sec wait
    run_traffic_flow(h1, h2_ip, 10, 1, 10, "second_random_flows_results.txt")

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
