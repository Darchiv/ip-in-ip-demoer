import math


class Protocol:
    IpInIp = 4
    ICMP = 1
    TCP = 6
    UDP = 17


class Packet:
    # for representatnion real is
    MAXSIZE = 50
    # IPv4
    VERSION = 4
    # no options - packet header size 5 * 32bit
    IHL = 5

    header_size = int(IHL * 32 / 8)

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
        # self.totalLength = 20 + len(data)
        self.totalLength = 20 + (len(data) if isinstance(data, str) else len(data.to_string()))
        self.str_header_size = len(self.header_to_str())

    def header_to_str(self):
        header = [self.VERSION, self.IHL, self.dscp,
                  int(self.header_size + (len(self.data) if isinstance(self.data, str) else len(self.data.to_string()))),
                  self.id, "00" + str(self.flag2),
                  self.offset, self.ttl, self.protocol, "checksum", self.source, self.destination]
        return str(header)

    def data_to_string(self):
        data = ""
        if isinstance(self.data, str):
            data = self.data
        elif isinstance(self.data, Packet):
            data = self.data.to_string()
        return data

    def to_string(self):
        header = self.header_to_str()

        # TODO: add padding - make sure data starts on a 32 bit boundary.
        return "{" + header + self.data_to_string() + "}"

    def encap(self, source, destination, protocol=Protocol.UDP,
              ttl=15, offset=0, flag2=0, uid=0, dscp=0):
        return Packet(source, destination, data=self)

    def decap(self):
        if isinstance(self.data, Packet):
            return self.data
        else:
            print("It is not encapsulated packet")

    def fragment(self, max_size=60):
        pstr = self.to_string()
        if len(pstr) > max_size:
            h_str = self.header_to_str()
            d_str = self.data_to_string()
            data_max_size = max_size - len(h_str)
            c = math.ceil(len(d_str) / data_max_size)
            if c <= 0:
                print("Data max size too low ", data_max_size)

            data_parts = [d_str[i:i + c] for i in range(0, len(d_str), c)]
            result = []
            for data_part in data_parts:
                result.append("{" + self.header_to_str() + data_part + "}")

            return result

        else:
            return self.to_string()
