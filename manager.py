from typing import Any, Dict, Set, Callable, Tuple
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

    def getNodeName(self, key: Any):
        return self.nodes[key].getName()

    def addConnection(self, key1: Any, key2: Any) -> Connection:
        print('Adding a connection between', key1, 'and', key2)
        node1 = self.nodes[key1]
        node2 = self.nodes[key2]

        connection = Connection(node1, node2)
        node1.connections.add(connection)
        node2.connections.add(connection)
        return connection

    def getNodeInterfaces(self, key: Any) -> Dict[str, Tuple[str, Connection]]:
        interfaces: Dict[str, Tuple[str, Connection]] = {}
        node = self.nodes[key]

        for connection in node.connections:
            key = connection.getDestinationName(node)
            ipstr: str = connection.getAddressStr(node)
            interfaces[key] = (ipstr, connection)

        return interfaces

    def setAddress(self, key: Any, conn: Connection, addrStr: str):
        '''Set the network address on the `key` node's interface
        which is connected with `conn` connection.'''
        print('Setting the network address of', key, '(connection', conn, ') to ', addrStr)
        node = self.nodes[key]

        try:
            address = IPv4Interface(addrStr)
        except (ValueError, AddressValueError):
            raise DemoerException('The supplied address is invalid. Use a CIDR notation.')

        conn.setAddress(node, address)
        # for connection in node.connections:
            # if connection.includesNode(node2):
                # break

    def deleteNode(self, key: Any):
        print('Deleting a node: ', key)
        node: Node = self.nodes[key]

        for connection in node.connections.copy():
            connection.disband()
            self.remove_connection(connection.arg)

        del self.nodes[key]