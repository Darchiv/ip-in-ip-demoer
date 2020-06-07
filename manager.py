from typing import Any, Dict, Set, Callable, Tuple
from ipaddress import IPv4Interface, AddressValueError

from Computer import Computer, Router, Connection, Node, DemoerException

class NetworkManager:
    def __init__(self, remove_connection: Callable[[Any], None], appendLog: Callable[[str], None]):
        self.nodes: Dict[Any, Node] = {}
        self.remove_connection = remove_connection
        self.appendLog = appendLog

    def addComputer(self, key: Any):
        computer = Computer(0)
        self.appendLog('{} computer has been added'.format(computer.getName()))
        self.nodes[key] = computer

    def addRouter(self, key: Any):
        router = Router(0)
        self.appendLog('{} router has been added'.format(router.getName()))
        self.nodes[key] = router

    def isComputer(self, key: Any):
        return isinstance(self.nodes[key], Computer)

    def isRouter(self, key: Any):
        return isinstance(self.nodes[key], Router)

    def getNodeName(self, key: Any):
        return self.nodes[key].getName()

    def addConnection(self, key1: Any, key2: Any) -> Connection:
        node1 = self.nodes[key1]
        node2 = self.nodes[key2]

        connection = Connection(node1, node2)
        node1.connections.add(connection)
        node2.connections.add(connection)

        self.appendLog('A connection between {} and {} has been created'.format(node1.getName(), node2.getName()))
        return connection

    def getNodeInterfaces(self, key: Any) -> Dict[str, Tuple[str, Connection]]:
        interfaces: Dict[str, Tuple[str, Connection]] = {}
        node = self.nodes[key]

        for connection in node.connections:
            key = connection.getDestinationName(node)
            ipstr: str = connection.getAddressStr(node)
            interfaces[key] = (ipstr, connection)

        return interfaces

    def preparePacket(self, keys: Tuple[Any, Any]):
        if len(keys) != 2:
            raise RuntimeError('Packet needs exactly two endpoints')

        start_node, end_node = self.nodes[keys[0]], self.nodes[keys[1]]
        self.appendLog('A packet has been prepared: {} -> {}'.format(start_node.getName(), end_node.getName()))

    def setAddress(self, key: Any, conn: Connection, addrStr: str):
        '''Set the network address on the `key` node's interface
        which is connected with `conn` connection.'''
        node = self.nodes[key]

        try:
            address = IPv4Interface(addrStr)
        except (ValueError, AddressValueError):
            raise DemoerException('The supplied address is invalid. Use a CIDR notation.')

        conn.setAddress(node, address)
        self.appendLog('The network address of {} changed to: {}'.format(node.getName(), addrStr))

    def deleteNode(self, key: Any):
        node: Node = self.nodes[key]
        node_name = node.getName()

        for connection in node.connections.copy():
            connection.disband()
            self.remove_connection(connection.arg)

        del self.nodes[key]
        self.appendLog('Node {} has beed removed'.format(node_name))
