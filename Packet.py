class Protocol:
    IpInIp = 4
    ICMP = 1
    TCP = 6
    UDP = 17


class Packet:
    # for representatnion real is
    MAXSIZE = 30
    # IPv4
    VERSION = 4
    # no options - packet header size 5 * 32bit
    IHL = 5

    header_size = IHL * 32 / 8

    # DSCP - service type - copy from oryginal
    # ECN - end-to-end notification - copy?
    # total length - header + data (20 - 65535 Bytes)
    # id - uniquely identifying the group of fragments of a single IP datagram
    # FLAGS 0 - reserved, 1 - dont fragment(drop), 2 - (0 for unfragmented, 1 fragmented except last)
    # data offset relative to unfragmented datagram (datagram not data?)
    # TTL - hop limit
    # Protocol - 4(Ip in IP) 1(ICMP) 6TCP 17UDP
    # Header checksum - after changing TTL
    # source - chenged by NAT
    # destination - changed by NAT

    def __init__(self, source, destination, data="", protocol=Protocol.UDP,
                 ttl=15, offset=0, flag2=0, uid=0, dscp=0):
        self.data = data
        self.dscp = dscp
        self.flag2 = flag2
        self.id = uid
        self.offset = offset
        self.ttl = ttl
        self.source = source
        self.destination = destination
        self.protocol = protocol
        self.totalLength = 20 + len(data)

    def toData(self):
        header = [self.VERSION, self.IHL, self.dscp,
                  int(self.header_size + len(self.data)), self.id, "00"+str(self.flag2),
                  self.offset, self.ttl, self.protocol, "checksum", self.source, self.destination]
        result = str(header)
        result += self.data
        return "{"+result+"}"

    def encap(self, source, destination, protocol=Protocol.UDP,
                 ttl=15, offset=0, flag2=0, uid=0, dscp=0, max_size=30):
        packet_size = self.header_size + len(self.data)
        if packet_size > self.MAXSIZE:
            print("wymagany podział na osobne datagramy (id??)")
        elif packet_size > max_size:

            print("Wymagany podział na pakiety (offset??)")
        else:
            print("Zmiesci się w 1 pakiecie")
            return Packet(source, destination, data=self.toData())

