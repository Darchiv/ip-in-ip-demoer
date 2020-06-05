from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Rectangle
from kivy.uix.bubble import Bubble
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput

Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

from Computer import DemoerException
from manager import NetworkManager


class Demoer(FloatLayout):
    def __init__(self, *args, **kwargs):

        # dimensions of the area where nodes can be placed
        self.workAreaXDim = 720
        self.workAreaYDim = 520
        self.workAreaXPos = 40
        self.workAreaYPos = 40

        # multiple choice bubble menu for node addition
        self.defaultBubble = Bubble(size_hint=(None, None), size=(250, 40))
        self.newComputerButton = Button(text="Nowy komputer")
        self.newRouterButton = Button(text="Nowy router")
        self.defaultBubble.add_widget(self.newComputerButton)
        self.defaultBubble.add_widget(self.newRouterButton)

        # coordinates of node-button to be placed
        self.pendingNodePosX = 0
        self.pendingNodePosY = 0

        # multiple choice bubble menu for node editing/removal
        self.nodeBubble = Bubble(size_hint=(None, None), size=(250, 40))
        self.newConnButton = Button(text="Dodaj połączenie")
        self.deleteNodeButton = Button(text="Usuń węzeł")
        self.nodeBubble.add_widget(self.newConnButton)
        self.nodeBubble.add_widget(self.deleteNodeButton)

        # reference to button being edited/removed
        self.pendingNodeRef = Button()

        # global state - adding connection or not
        self.isInConnectionMode = False
        self.netManager = NetworkManager(self.__deleteLine)

        # define widgets of side panel
        self.sidePanelTabbedPanel = TabbedPanel(do_default_tab=False, size=(200, 600), pos=(800, 0))
        self.sidePanelLogTab = TabbedPanelItem(text="Logi")
        self.sidePanelLogLayout = GridLayout(cols=1, spacing=20, size_hint=(None, None), size=(190, 550))
        self.sidePanelLogLayout.bind(minimum_height=self.sidePanelLogLayout.setter('height'))

        # test of WIP log display
        for i in range(100):
            self.logLabel = Label(padding=(20, 20), text="Log line test.")
            self.sidePanelLogLayout.add_widget(self.logLabel)

        self.sidePanelScrollView = ScrollView(size_hint=(None, None), size=(200, 550), pos=(800, 0),
                                              scroll_type=['bars'], bar_width=10,
                                              bar_inactive_color=[1, 1, 1, .8], bar_color=[1, 1, 1, 1])
        self.sidePanelScrollView.add_widget(self.sidePanelLogLayout)
        self.sidePanelLogTab.add_widget(self.sidePanelScrollView)
        self.sidePanelTabbedPanel.add_widget(self.sidePanelLogTab)

        # set window color
        Window.clearcolor = (0.7, 0.7, 0.7, 1)
        super(Demoer, self).__init__(*args, **kwargs)

        self.add_widget(self.sidePanelTabbedPanel)

        # create delimiter line around the work area
        self.canvas.before.add(Line(rectangle=(self.workAreaXPos, self.workAreaYPos,
                                               self.workAreaXDim, self.workAreaYDim), width=0.5))

        # create background square behind side panel and scrollbar
        with self.canvas.before:
            Color(0.3, 0.3, 0.3, 1)
            Rectangle(pos=(2*self.workAreaXPos+self.workAreaXDim, 0), size=(200, 600))
            Color(0.2, 0.2, 0.2, 1)
            Rectangle(pos=(2*self.workAreaXPos+self.workAreaXDim+190, 0), size=(10, 550))

    # switch between placing connection or editing nodes
    def toggleConnectionMode(self, instance):
        self.clearBubbles()
        if not self.isInConnectionMode:
            self.pendingNodeRef.background_color = (1, 0.5, 0.5, 1)
            self.isInConnectionMode = True
        else:
            self.pendingNodeRef.background_color = (1, 1, 1, 1)
            self.isInConnectionMode = False

    def showNodeEditPanel(self, instance):
        self.sidePanelTabbedPanel.remove_widget(self.sidePanelTabbedPanel.children[1])
        sidePanelNodeTab = TabbedPanelItem(text=instance.children[0].text)
        sidePanelNodeLayout = GridLayout(cols=1, spacing=10, size_hint=(None, None), size=(190, 550))
        sidePanelNodeLayout.add_widget(Label(text="GigabitEthernet 0/0"))
        sidePanelNodeLayout.add_widget(TextInput())
        sidePanelNodeTab.add_widget(sidePanelNodeLayout)
        self.sidePanelTabbedPanel.add_widget(sidePanelNodeTab)

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
        nodeImg.center_y = nodeImg.parent.center_y + 10
        nodeLabel.center_x = nodeLabel.parent.center_x
        nodeLabel.center_y = nodeLabel.parent.center_y - 10
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
        nodeImg.center_y = nodeImg.parent.center_y + 10
        nodeLabel.center_x = nodeLabel.parent.center_x
        nodeLabel.center_y = nodeLabel.parent.center_y - 10
        nodeButton.bind(on_press=self.showNodeBubble)
        self.add_widget(nodeButton)
        self.netManager.addRouter(nodeButton)
        nodeLabel.text = "R"

    # show bubble menu on click on node
    # OR create connection between active node and clicked node when in connection mode
    def showNodeBubble(self, instance):
        if not self.isInConnectionMode:
            self.showNodeEditPanel(instance)
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
        if after:
            self.remove_widget(self.defaultBubble)
            if self.workAreaXPos + self.workAreaXDim > touch.pos[0] > self.workAreaXPos \
                    and self.workAreaYPos + self.workAreaYDim > touch.pos[1] > self.workAreaYPos:
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
        Window.size = (1000, 600)
        return Demoer()
