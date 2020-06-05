from Packet import Packet

print("test GitHub push")
# testing pushing via PyCharm -JZ

p = Packet("X", "Y", data="xyzassszasdasdasdsad")
print(p.to_string())

x = p.encap('A', 'B')

if isinstance(x.datagram_fragment(), list):
    for i in x.datagram_fragment():
        print(i.to_string())
else:
    print(x.datagram_fragment().to_string())


