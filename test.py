from Packet import Packet

print("test GitHub push")
# testing pushing via PyCharm -JZ

p = Packet("X", "Y", data="xyzasssz")
print(p.to_string())

x = p.encap('A', 'B')

print(x.mtu_fragment())


