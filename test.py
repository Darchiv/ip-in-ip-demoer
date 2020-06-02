from Packet import Packet

print("test GitHub push")
# testing pushing via PyCharm -JZ

p = Packet("X", "Y", data="xyz")
print(p.toData())

x = p.encap("A", "B")
print(x.toData())

