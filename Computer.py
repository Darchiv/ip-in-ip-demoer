import enum
from typing import Any, Union, Set
from ipaddress import IPv4Interface

class DemoerException(Exception):
    def __init__(self, message):
        self.message = message

class NetworkSettings:
    class_lastIP = "192.168.0.1"
    class_defaultMask = 24
    class_defaultGateway = "192.168.0.1"
    NEXT_IP = "next"

    def __init__(self, ip=NEXT_IP, mask=class_defaultMask, gateway=class_defaultGateway):
        if ip == NetworkSettings.NEXT_IP:
            tmp_ip = NetworkSettings.class_lastIP.split('.')
            tmp_ip[-1] = str(int(tmp_ip[-1]) + 1)
            NetworkSettings.class_lastIP = '.'.join(tmp_ip)
            self.ip = NetworkSettings.class_lastIP
        else:
            self.ip = ip
        self.mask = mask
        self.gateway = gateway

class Node:
    def __init__(self):
        self.connections: Set[Connection] = set()

class Computer(Node):
    class_img = "pc.jpg"
    NETWORK_AUTO = "auto"

    def __init__(self, position, network=NETWORK_AUTO):
        super().__init__()

        self.position = position
        if network == Computer.NETWORK_AUTO:
            self.network = NetworkSettings()
        else:
            self.network = network

class Router(Node):
    class_img = "router.jpg"
    LOCAL = 0
    GLOBAL = 1
    LOCAL_DEFAULT = "auto"
    class_defaultLocalIP = NetworkSettings.class_defaultGateway

    def __init__(self, global_network, local_network=LOCAL_DEFAULT):
        super().__init__()

        self.network = [None] * 2
        if local_network == Router.LOCAL_DEFAULT:
            self.network[Router.LOCAL] = NetworkSettings(Router.class_defaultLocalIP)
            self.network[Router.GLOBAL] = global_network
        else:
            self.network = [local_network, global_network]

class ConnectionType(enum.Enum):
    '''A type of connection. An intra network applies to computers and routers
    within the same network whereas a tunnel one is between different routers.'''

    INTRA_NETWORK = 1
    TUNNEL = 2

class Connection:
    '''A logical representation of a connection between nodes (computers or routers).'''

    def __init__(self, node1: Node, node2: Node):
        if isinstance(node1, Computer) and isinstance(node2, Computer):
            raise DemoerException('A connection between two Computers cannot be created')

        if isinstance(node1, Router) and isinstance(node2, Router):
            self.type = ConnectionType.TUNNEL
        else:
            self.type = ConnectionType.INTRA_NETWORK

        self.node1 = node1
        self.node2 = node2
        self.address1: IPv4Interface
        self.address2: IPv4Interface
        self.arg: Any

    def setArg(self, arg: Any):
        self.arg = arg

    def includesNode(self, node: Node):
        '''Checks whether the node is part of this connection.'''
        return node in (self.node1, self.node2)

    def setAddress(self, node: Node, address: IPv4Interface):
        if self.node1 == node:
            self.address1 = address
        elif self.node2 == node:
            self.address2 = address
        else:
            raise RuntimeError('Node {} is not part of connection {}'.format(node, self))

        # TODO: Propagate to the whole network and check for validity (whether
        # all Computers and Routers are in the same network).

if __name__ == '__main__':
    c = Computer([10, 10], Computer.NETWORK_AUTO)
    c2 = Computer([10, 10], Computer.NETWORK_AUTO)

    r1 = Router(NetworkSettings("10.0.0.1", gateway="10.0.0.2"))

    print(c.network.ip)
    print(c2.network.ip)
    print(r1.network[Router.GLOBAL].ip)
