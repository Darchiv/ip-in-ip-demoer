from Packet import Packet

print("test GitHub push")
# testing pushing via PyCharm -JZ

p = Packet("X", "Y", data="xyzasdasdasdasdasda")
print(p.toData())

x = p.encap("A", "B", max_size=25)
for p in x:
    print(p.toData())

