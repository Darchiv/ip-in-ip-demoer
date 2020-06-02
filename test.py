from Packet import Packet

print("test GitHub push")
# testing pushing via PyCharm -JZ

p = Packet("X", "Y", data="xyzasssz")
print(p.toData())

x = p.encap("A", "B", max_size=40)
for p in x:
    print(p.toData())

