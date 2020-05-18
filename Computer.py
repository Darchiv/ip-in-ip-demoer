class NetworkSettings:
    class_lastIP = "192.168.0.1"
    class_defaultMask = 24
    class_defaultGateway = "192.168.0.1"
    NEXT_IP = "next"

    def __init__(self, ip=NEXT_IP, mask=class_defaultMask, gateway=class_defaultGateway):
        if ip == NetworkSettings.NEXT_IP:
            tmp_ip = NetworkSettings.class_lastIP.split('.')
            tmp_ip[-1] = str(int(tmp_ip[-1])+1)
            NetworkSettings.class_lastIP = '.'.join(tmp_ip)
            self.ip = NetworkSettings.class_lastIP
        else:
            self.ip = ip
        self.mask = mask
        self.gateway = gateway


class Computer:
    class_img = "pc.jpg"
    NETWORK_AUTO = "auto"

    def __init__(self, position, network=NETWORK_AUTO):
        self.position = position
        if network == Computer.NETWORK_AUTO:
            self.network = NetworkSettings()
        else:
            self.network = network


class Router:
    LOCAL = 0
    GLOBAL = 1
    LOCAL_DEFAULT = "auto"
    class_defaultLocalIP = NetworkSettings.class_defaultGateway

    def __init__(self, global_network, local_network=LOCAL_DEFAULT):
        self.network = [None]*2
        if local_network == Router.LOCAL_DEFAULT:
            self.network[Router.LOCAL] = NetworkSettings(Router.class_defaultLocalIP)
            self.network[Router.GLOBAL] = global_network
        else:
            self.network = [local_network, global_network]


c = Computer([10, 10], Computer.NETWORK_AUTO)
c2 = Computer([10, 10], Computer.NETWORK_AUTO)

r1 = Router(NetworkSettings("10.0.0.1", gateway="10.0.0.2"))

print(c.network.ip)
print(c2.network.ip)
print(r1.network[Router.GLOBAL].ip)
