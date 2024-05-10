from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import threading
import random

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

def run_continuous_flow(h1, h2_ip):
    print("Starting continuous flow for 5 minutes, capturing data every 0.5 second...")
    h1.cmd(f'iperf -c {h2_ip} -t 300 -i 0.5 -b 1M > continuous_flow_results.txt &')

def run_burst_traffic(h1, h2_ip, delay):
    print(f"Starting burst traffic after {delay} seconds...")
    time.sleep(delay)
    h1.cmd(f'iperf -c {h2_ip} -t 10 -b 100M > burst_traffic_results.txt &')

def run_random_flows(h1, h2_ip):
    while True:
        duration = random.randint(1, 10)  # Duration between 1 and 10 seconds
        bandwidth = random.randint(1, 50) * 10  # Bandwidth between 10 Mbps and 500 Mbps
        print(f"Starting random flow for {duration} seconds at {bandwidth} Mbps...")
        h1.cmd(f'iperf -c {h2_ip} -t {duration} -b {bandwidth}M > random_flow_{time.time()}.txt &')
        time.sleep(random.randint(1, 5))  # Wait between 1 and 5 seconds before starting another flow

def setup_network():
    topo = LinearTopology()
    net = Mininet(topo)
    net.start()
    h1, h2 = net.get('h1'), net.get('h2')
    h2_ip = h2.IP()

    # Start continuous flow
    threading.Thread(target=run_continuous_flow, args=(h1, h2_ip)).start()

    # Schedule burst traffic
    threading.Thread(target=run_burst_traffic, args=(h1, h2_ip, 30)).start()  # Start after 30 seconds

    # Start random flows
    threading.Thread(target=run_random_flows, args=(h1, h2_ip)).start()

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    setup_network()
