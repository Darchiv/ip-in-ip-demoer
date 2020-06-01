from typing import Any, Dict, Callable

from Computer import Computer, Router, Connection, Node

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

    def deleteNode(self, key: Any):
        print('Deleting a node: ', key)
        node: Node = self.nodes[key]

        for connection in node.connections:
            self.remove_connection(connection.arg)

        del self.nodes[key]
