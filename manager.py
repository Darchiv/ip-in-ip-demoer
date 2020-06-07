from typing import Any, Dict, Set, Callable, Tuple, List
from ipaddress import IPv4Interface, AddressValueError

from Computer import Computer, Router, Connection, ConnectionType, Node, DemoerException
from Packet import Packet, Protocol

PacketInfo = Dict[str, Any]

class NetworkManager:
    def __init__(self, remove_connection: Callable[[Any], None],
                 appendLog: Callable[[str], None],
                 animatePacket: Callable[[], None]):
        self.nodes: Dict[Any, Node] = {}
        self.remove_connection = remove_connection
        self.appendLog = appendLog
        self.animatePacket = animatePacket
        self.packetInfos: List[PacketInfo] = []

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
        if len(self.packetInfos) > 0:
            raise DemoerException('Only one packet at a time please')

        if len(keys) != 2:
            raise RuntimeError('Packet needs exactly two endpoints')

        start_node, end_node = self.nodes[keys[0]], self.nodes[keys[1]]

        if not isinstance(start_node, Computer) or not isinstance(end_node, Computer):
            raise DemoerException('A packet can be sent only between two Computers')

        source_conns = list(start_node.connections)
        if len(source_conns) != 1:
            raise DemoerException('Exactly one interface on the source node ({}) is required'.format(start_node.getName()))

        dest_conns = list(end_node.connections)
        if len(dest_conns) != 1:
            raise DemoerException('Exactly one interface on the destination node ({}) is required'.format(end_node.getName()))

        sourceAddr = source_conns[0].getAddress(start_node)
        destAddr = dest_conns[0].getAddress(end_node)

        if sourceAddr == IPv4Interface('0.0.0.0/0'):
            raise DemoerException('Source must have a valid IP address')

        if destAddr == IPv4Interface('0.0.0.0/0'):
            raise DemoerException('Destination must have a valid IP address')

        packet = Packet(str(sourceAddr), str(destAddr), 'TESTDATA')
        self.packetInfos.append({
            'sourceAddr': sourceAddr,
            'destAddr': destAddr,
            'currentNode': start_node,
            'packet': packet
        })

        self.appendLog('A packet has been prepared: {} -> {}'.format(start_node.getName(), end_node.getName()))

    def __routeNextNode(self, packetInfo: PacketInfo) -> Tuple[Node, IPv4Interface, ConnectionType]:
        '''Returns the next node on the routing path, along with its address and connection type.'''
        # Basic routing:
        # - from Computer to neighbor Router,
        # - from Router to Router through Tunnel, or
        # - from Router to Computer if directly connected

        currentNode = packetInfo['currentNode']
        destAddr = packetInfo['destAddr']

        route_info = None

        if isinstance(currentNode, Computer):
            conn = tuple(currentNode.connections)[0]

            if not conn.hasValidAddressing():
                raise DemoerException('The {} <-> {} connection is not configured appropriately'.format(conn.node1.getName(), conn.node2.getName()))

            destNode, destAddr = conn.getDestinationNode(currentNode)
            route_info = (destNode, destAddr, conn.type)

        elif isinstance(currentNode, Router):
            for conn in currentNode.connections:
                nextNode, nextAddr = conn.getDestinationNode(currentNode)
                if nextAddr == destAddr:
                    print('Directly connected: {}'.format(destAddr))
                    route_info = (nextNode, nextAddr, conn.type)
                    break

            if route_info is None:
                for conn in currentNode.connections:
                    if conn.type == ConnectionType.TUNNEL:
                        print('Tunnelling to: {}'.format(destAddr))
                        nextNode, nextAddr = conn.getDestinationNode(currentNode)
                        route_info = (nextNode, nextAddr, conn.type)
                        break

        if route_info is None:
            raise DemoerException('No next node to route to')

        return route_info

    def stepSimulation(self):
        for packetInfo in self.packetInfos[:]:
            nextNode, nextAddress, connType = self.__routeNextNode(packetInfo)
            print('Route: {} -> {}, IP = {}, connType = {}'.format(packetInfo['currentNode'].getName(), nextNode.getName(), str(nextAddress.ip), connType))

            packetInfo['packet'].ttl_dec()

            if isinstance(packetInfo['packet'].data, Packet) and connType == ConnectionType.INTRA_NETWORK:
                packetInfo['packet'] = packetInfo['packet'].decap()

            elif not isinstance(packetInfo['packet'].data, Packet) and connType == ConnectionType.TUNNEL:
                packetInfo['packet'] = packetInfo['packet'].encap(packetInfo['currentNode'].getName(), nextNode.getName())

            self.appendLog(packetInfo['packet'].to_string())

            # TODO: This will allow animating the packet as it ventures through
            # the network. Node keys (buttons) or the connection need to be passed there
            self.animatePacket()

            packetInfo['currentNode'] = nextNode
            if packetInfo['destAddr'] == nextAddress:
                print('Packet has arrived at its destination')
                self.packetInfos.remove(packetInfo)

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
