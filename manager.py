from typing import Any, Dict, Callable
from ipaddress import IPv4Interface, AddressValueError

from Computer import Computer, Router, Connection, Node, DemoerException

class NetworkManager:
    def __init__(self, remove_connection: Callable[[Any], None]):
        self.nodes: Dict[Any, Node] = {}
        self.remove_connection = remove_connection

    def addComputer(self, key: Any):
        print('Adding a computer: ', key)
        self.nodes[key] = Computer(0)

    def addRouter(self, key: Any):
        print('Adding a router: ', key)
        self.nodes[key] = Router(0)

    def isComputer(self, key: Any):
        return isinstance(self.nodes[key], Computer)

    def isRouter(self, key: Any):
        return isinstance(self.nodes[key], Router)

    def addConnection(self, key1: Any, key2: Any) -> Connection:
        print('Adding a connection between', key1, 'and', key2)
        node1 = self.nodes[key1]
        node2 = self.nodes[key2]

        connection = Connection(node1, node2)
        node1.connections.add(connection)
        node2.connections.add(connection)
        return connection

    def setAddress(self, key1: Any, key2: Any, addrStr: str):
        '''Set the network address on the key1 node's interface
        which is connected to the key2 node.'''
        print('Setting the network address of', key1, '(pointed to', key2, ')')
        node1 = self.nodes[key1]
        node2 = self.nodes[key2]

        try:
            address = IPv4Interface(addrStr)
        except (ValueError, AddressValueError):
            raise DemoerException('The supplied address is invalid. Use a CIDR notation.')

        for connection in node1.connections:
            if connection.includesNode(node2):
                connection.setAddress(node1, address)
                break

        raise RuntimeError('Connection between {} and {} does not exist'.format(key1, key2))

    def deleteNode(self, key: Any):
        print('Deleting a node: ', key)
        node: Node = self.nodes[key]

        for connection in node.connections:
            self.remove_connection(connection.arg)

        del self.nodes[key]
