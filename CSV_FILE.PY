import csv
import re
import time
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import Controller, RemoteController, OVSController
from mininet.link import TCLink

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

def run_iperf(h1, h2_ip, duration, interval, delay, loop):
    result = h1.cmd(f'iperf -c {h2_ip} -i {interval} -t {duration} -b 10m -d')

    lines = result.split('\n')

    iperf_data = []
    with open('iperf_results.csv', 'a', newline='') as csvfile:
        fieldnames = ['Loop', 'Delay', 'Interval', 'Transferred Data', 'Average Bandwidth']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        for line in lines:
            match = re.search(r'\[(\d+)\]\s+(\d+\.\d+)-(\d+\.\d+) sec\s+(\d+\.\d+|\d+\s+) (KBytes|MBytes|Bytes)\s+(\d+\.\d+|\d+) (Mbits|Kbits|bits)/sec', line)
            if match:
                loop_num = loop
                delay_ms = delay
                start_time = float(match.group(2))
                end_time = float(match.group(3))
                interval_sec = end_time - start_time
                transferred_data = float(match.group(4))
                if match.group(5) == 'KBytes':
                    transferred_data *= 1024
                elif match.group(5) == 'MBytes':
                    transferred_data *= 1024 * 1024
                bandwidth = float(match.group(6))
                if match.group(7) == 'Kbits':
                    bandwidth /= 1000
                elif match.group(7) == 'bits':
                    bandwidth /= 1000 * 1000

                data_dict = {
                    'Loop': loop_num,
                    'Delay': delay_ms,
                    'Interval': interval_sec,
                    'Transferred Data': transferred_data,
                    'Average Bandwidth': bandwidth
                }
                writer.writerow(data_dict)
                iperf_data.append(data_dict)

    print(result)
    return iperf_data

def create_linear_topology():
    topo = LinearTopology()
    net = Mininet(topo=topo, controller=RemoteController, link=TCLink)
    net.start()

    h1, h2 = net.get('h1', 'h2')

    delays = [10, 50]
    num_loops = 2

    for loop in range(1, num_loops + 1):
        for delay in delays:
            h1.cmd(f'tc qdisc add dev h1-eth0 root netem delay {delay}ms')
            h2.cmd(f'tc qdisc add dev h2-eth0 root netem delay {delay}ms')

            result = run_iperf(h1, h2.IP(), 10, 0.5, delay, loop)

            h1.cmd('tc qdisc del dev h1-eth0 root')
            h2.cmd('tc qdisc del dev h2-eth0 root')

            time.sleep(1)

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_linear_topology()
