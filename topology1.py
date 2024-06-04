#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
About: Basic example of service (running inside an APPContainer) migration.
"""

import os
import shlex
import time

from subprocess import check_output

from comnetsemu.cli import CLI
from comnetsemu.net import Containernet, VNFManager  # Ensure Containernet is imported
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.node import Controller
from docker import DockerClient

class CustomContainernet(Containernet):
    def __init__(self, **kwargs):
        self.dclient = kwargs.pop('dclient', None)
        super().__init__(**kwargs)

def get_ofport(ifce: str):
    """Get the openflow port based on the interface name.

    :param ifce (str): Name of the interface.
    """
    return (
        check_output(shlex.split("ovs-vsctl get Interface {} ofport".format(ifce)))
        .decode("utf-8")
        .strip()
    )

if __name__ == "__main__":

    # Only used for auto-testing.
    AUTOTEST_MODE = os.environ.get("COMNETSEMU_AUTOTEST_MODE", 0)

    setLogLevel("info")

    # Initialize Docker client
    docker_client = DockerClient(base_url='unix://var/run/docker.sock')

    net = CustomContainernet(controller=Controller, link=TCLink, xterms=False, dclient=docker_client)
    mgr = VNFManager(net)

    info("*** Add the default controller\n")
    net.addController("c0")

    info("*** Creating the client and hosts\n")
    h1 = net.addDockerHost(
        "h1", dimage="dev_test", ip="10.0.0.11/24", docker_args={"hostname": "h1"}
    )

    h2 = net.addDockerHost(
        "h2",
        dimage="dev_test",
        ip="10.0.0.12/24",
        docker_args={"hostname": "h2", "pid_mode": "host"},
    )

    info("*** Adding switch and links\n")
    s1 = net.addSwitch("s1")
    net.addLinkNamedIfce(s1, h1, bw=1000, delay="5ms")
    # Add the interfaces for service traffic.
    net.addLinkNamedIfce(s1, h2, bw=1000, delay="5ms")

    info("\n*** Starting network\n")
    net.start()

    s1_h1_port_num = get_ofport("s1-h1")
    s1_h2_port_num = get_ofport("s1-h2")
    h2_mac = h2.MAC(intf="h2-s1")

    h2.setMAC("00:00:00:00:00:12", intf="h2-s1")

    info("*** Add flow to forward traffic from h1 to h2 to switch s1.\n")
    check_output(
        shlex.split(
            'ovs-ofctl add-flow s1 "in_port={}, actions=output:{}"'.format(
                s1_h1_port_num, s1_h2_port_num
            )
        )
    )
    check_output(
        shlex.split(
            'ovs-ofctl add-flow s1 "in_port={}, actions=output:{}"'.format(
                s1_h2_port_num, s1_h1_port_num
            )
        )
    )

    info("*** h1 ping 10.0.0.12 with 3 packets: \n")
    ret = h1.cmd("ping -c 3 10.0.0.12")
    print(ret)

    info("*** Deploy video server on h2.\n")
    video_server_h2 = mgr.addContainer(
        "video_server_h2", "h2", "topologyproject", "python /home/video_server.py"
    )
    time.sleep(3)
    info("*** Deploy client app on h1.\n")
    client_app = mgr.addContainer(
        "client", "h1", "topologyproject", "python /home/client.py"
    )
    time.sleep(10)
    client_log = client_app.getLogs()
    print("\n*** Current log of the client: \n{}".format(client_log))

    if not AUTOTEST_MODE:
        CLI(net)

    try:
        mgr.removeContainer("video_server_h2")
    except Exception as e:
        print(e)
    finally:
        net.stop()
        mgr.stop()