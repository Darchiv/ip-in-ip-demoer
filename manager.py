from typing import Any

from Computer import Computer, Router, Connection

class NetworkManager:
    def __init__(self):
        self.nodes = {}

    # def getArgByKey(self, key: Any):
    #     return 

    def addComputer(self, key: Any, on_remove=None):
        print('Adding a computer: ', key)
        self.nodes[key] = Computer(0)

    def addRouter(self, key: Any, on_remove=None):
        print('Adding a router: ', key)
        self.nodes[key] = Router(0)

    def deleteNode(self, key: Any):
        print('Deleting a node: ', key)
        # TODO: Also delete connections of that node
        del self.nodes[key]
