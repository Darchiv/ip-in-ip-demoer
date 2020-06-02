from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics.vertex_instructions import Line
from kivy.uix.bubble import Bubble
from kivy.uix.image import Image

Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

from Computer import DemoerException
from manager import NetworkManager

class Demoer(FloatLayout):
    # multiple choice bubble menu for node addition
    defaultBubble = Bubble(size_hint=(None, None), size=(250, 40))
    newComputerButton = Button(text="Nowy komputer")
    newRouterButton = Button(text="Nowy router")
    defaultBubble.add_widget(newComputerButton)
    defaultBubble.add_widget(newRouterButton)

    # coordinates of node-button to be placed
    pendingNodePosX = 0
    pendingNodePosY = 0

    # multiple choice bubble menu for node editing/removal
    nodeBubble = Bubble(size_hint=(None, None), size=(250, 40))
    newConnButton = Button(text="Dodaj połączenie")
    deleteNodeButton = Button(text="Usuń węzeł")
    nodeBubble.add_widget(newConnButton)
    nodeBubble.add_widget(deleteNodeButton)

    # reference to button being edited/removed
    pendingNodeRef = Button()

    # global state - adding connection or not
    isInConnectionMode = False

    def __init__(self, *args, **kwargs):
        # set window color
        Window.clearcolor = (0.7, 0.7, 0.7, 1)
        super(Demoer, self).__init__(*args, **kwargs)

        self.netManager = NetworkManager(self.__deleteLine)

    ## switch between placing connection or editing nodes
    def toggleConnectionMode(self, instance):
        self.clearBubbles()
        if not self.isInConnectionMode:
            self.pendingNodeRef.background_color = (1, 0.5, 0.5, 1)
            self.isInConnectionMode = True
        else:
            self.pendingNodeRef.background_color = (1, 1, 1, 1)
            self.isInConnectionMode = False

    # remove active bubble menus
    def clearBubbles(self):
        self.remove_widget(self.nodeBubble)
        self.remove_widget(self.defaultBubble)

    def __deleteLine(self, line):
        print('deleting line', line)
        self.canvas.before.remove(line)

    # remove active node after clicking in bubble menu
    def deleteNode(self, instance):
        self.clearBubbles()
        self.remove_widget(self.pendingNodeRef)
        self.netManager.deleteNode(self.pendingNodeRef)

    # add pending node as computer after clicking in bubble menu
    def addComputer(self, instance):
        nodeButton = Button(pos=(self.pendingNodePosY, self.pendingNodePosX), size_hint=(None, None), size=(40, 40))
        nodeImg = Image(source="Images/computer.png")
        nodeLabel = Label()
        nodeButton.add_widget(nodeImg)
        nodeButton.add_widget(nodeLabel)
        nodeImg.center_x = nodeImg.parent.center_x
        nodeImg.center_y = nodeImg.parent.center_y+10
        nodeLabel.center_x = nodeLabel.parent.center_x
        nodeLabel.center_y = nodeLabel.parent.center_y-10
        nodeButton.bind(on_press=self.showNodeBubble)
        self.add_widget(nodeButton)
        self.netManager.addComputer(nodeButton)
        nodeLabel.text = "PC"

    # add pending node as router after clicking in bubble menu
    def addRouter(self, instance):
        nodeButton = Button(pos=(self.pendingNodePosY, self.pendingNodePosX), size_hint=(None, None), size=(40, 40))
        nodeImg = Image(source="Images/router.png")
        nodeLabel = Label()
        nodeButton.add_widget(nodeImg)
        nodeButton.add_widget(nodeLabel)
        nodeImg.center_x = nodeImg.parent.center_x
        nodeImg.center_y = nodeImg.parent.center_y+10
        nodeLabel.center_x = nodeLabel.parent.center_x
        nodeLabel.center_y = nodeLabel.parent.center_y-10
        nodeButton.bind(on_press=self.showNodeBubble)
        self.add_widget(nodeButton)
        self.netManager.addRouter(nodeButton)
        nodeLabel.text = "R"

    # show bubble menu on click on node
    # OR create connection between active node and clicked node when in connection mode
    def showNodeBubble(self, instance):
        if not self.isInConnectionMode:
            self.clearBubbles()
            self.pendingNodeRef = instance
            self.nodeBubble.pos = (instance.pos[0] - 105, instance.pos[1] + 40)
            self.deleteNodeButton.bind(on_press=self.deleteNode)
            self.newConnButton.bind(on_press=self.toggleConnectionMode)
            self.add_widget(self.nodeBubble)
        else:
            try:
                connection = self.netManager.addConnection(instance, self.pendingNodeRef)
            except DemoerException as e:
                print(e.message)
            else:
                line = Line(points=[self.pendingNodeRef.pos[0] + 20, self.pendingNodeRef.pos[1] + 20,
                            instance.pos[0] + 20, instance.pos[1] + 20], width=2)
                self.canvas.before.add(line)
                connection.setArg(line)
                self.toggleConnectionMode(Button())

    # show bubble on right-clicking canvas
    def showDefaultBubble(self, posx, posy):
        self.clearBubbles()
        self.pendingNodePosY = posx - 20
        self.pendingNodePosX = posy - 20
        self.defaultBubble.pos = (posx - 125, posy)
        self.newComputerButton.bind(on_press=self.addComputer)
        self.newRouterButton.bind(on_press=self.addRouter)
        self.add_widget(self.defaultBubble)

    def on_touch_down(self, touch, after=False):
        if after and self.collide_point(touch.pos[0], touch.pos[1]):
            self.remove_widget(self.defaultBubble)
            if touch.button == "right":
                if not self.isInConnectionMode:
                    self.showDefaultBubble(touch.x, touch.y)
                else:
                    self.toggleConnectionMode(Button())
        else:
            Clock.schedule_once(lambda dt: self.on_touch_down(touch, True), 0.01)
            return super(Demoer, self).on_touch_down(touch)


class DemoApp(App):
    def build(self):
        Window.size = (800, 600)
        return Demoer()
