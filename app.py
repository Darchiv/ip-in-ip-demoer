import functools

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.bubble import Bubble
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
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

        # define widgets of side panel and add them to window
        self.sidePanelTabbedPanel = TabbedPanel(do_default_tab=False, size=(200, 600), pos=(800, 0),
                                                background_color=(0, 0, 0, 0), tab_width=100)

        # define widgets of log display and add them to window
        self.sidePanelLogTab = TabbedPanelItem(text="Symulacja")
        self.sidePanelLogLayout = GridLayout(cols=1, spacing=10,
                                             size_hint=(None, None), size=(200, 550))
        self.logField = TextInput(padding=10, readonly=True, size_hint_max_y=None, size_hint=(None, None),
                                  size=(190, 550))
        self.logField.bind(minimum_height=self.logField.setter('height'))
        self.sidePanelLogScrollView = ScrollView(size_hint=(None, None),
                                                 size=(200, 450),
                                                 scroll_type=['bars'], bar_width=10,
                                                 bar_inactive_color=[1, 1, 1, .8], bar_color=[0.3, 1, 1, 1])
        self.sidePanelLogScrollView.add_widget(self.logField)
        self.sidePanelLogLayout.add_widget(self.sidePanelLogScrollView)
        self.sidePanelLogTab.add_widget(self.sidePanelLogLayout)
        self.sidePanelTabbedPanel.add_widget(self.sidePanelLogTab)

        # test of WIP log display
        for i in range(100):
            self.logField.text = self.logField.text + "This is a test log entry. \n\n"

        # define widgets of node edit panel to be added to window later
        # when a node is selected, add sidePanelNodeTab with the proper tab name to sidePanelTabbedPanel
        # and fill sidePanelNodeTab with content - interface configuration form
        self.sidePanelNodeTab = TabbedPanelItem()
        self.sidePanelNodeLayout = GridLayout(cols=1, spacing=5,
                                              size_hint=(None, None), size=(200, 550))
        self.sidePanelNodeLayout.bind(minimum_height=self.sidePanelNodeLayout.setter('height'))
        self.sidePanelNodeScrollView = ScrollView(size_hint=(None, None), size=(200, 550), pos=(800, 0),
                                                  scroll_type=['bars'], bar_width=10,
                                                  bar_inactive_color=[1, 1, 1, .8], bar_color=[1, 1, 1, 1])
        self.sidePanelNodeTab.add_widget(self.sidePanelNodeScrollView)
        self.sidePanelNodeScrollView.add_widget(self.sidePanelNodeLayout)

        # define simulation-related buttons and add them to the window
        self.toggleSimButton = Button(text="Symuluj")
        self.addPacketButton = Button(text="Nowy pakiet")
        self.stepSimButton = Button(text=">|")
        self.playSimButton = Button(text=">")
        self.simButtonLayout = BoxLayout()
        self.sidePanelLogLayout.add_widget(self.addPacketButton)
        self.sidePanelLogLayout.add_widget(self.toggleSimButton)
        self.sidePanelLogLayout.add_widget(self.simButtonLayout)
        self.simButtonLayout.add_widget(self.playSimButton)
        self.simButtonLayout.add_widget(self.stepSimButton)

        # set window color
        Window.clearcolor = (0.7, 0.7, 0.7, 1)

        super(Demoer, self).__init__(*args, **kwargs)

        self.add_widget(self.sidePanelTabbedPanel)

        # create delimiter line around the work area
        self.canvas.before.add(Line(rectangle=(self.workAreaXPos, self.workAreaYPos,
                                               self.workAreaXDim, self.workAreaYDim), width=0.5))

        # create background square behind side panel
        with self.canvas.before:
            Color(0.3, 0.3, 0.3, 1)
            Rectangle(pos=(2 * self.workAreaXPos + self.workAreaXDim, 0), size=(200, 600))
            Color(1, 1, 1, 1)

    # switch between placing connection or editing nodes
    def toggleConnectionMode(self, instance):
        self.clearBubbles()
        if not self.isInConnectionMode:
            self.pendingNodeRef.background_color = (1, 0.5, 0.5, 1)
            self.isInConnectionMode = True
        else:
            self.pendingNodeRef.background_color = (1, 1, 1, 1)
            self.isInConnectionMode = False

    # display node property edit tab
    def showNodeEditPanel(self, instance):
        print('Show edit panel of:', instance)
        node_name = self.netManager.getNodeName(instance)
        self.sidePanelNodeTab.text = node_name

        if len(self.sidePanelTabbedPanel.children) == 2:
            self.sidePanelTabbedPanel.add_widget(self.sidePanelNodeTab)

        self.sidePanelTabbedPanel.switch_to(self.sidePanelNodeTab)

        self.sidePanelNodeLayout.clear_widgets()
        self.sidePanelNodeLayout.add_widget(Label(text="Interfejsy węzła " + node_name + ":", size_hint=(1, None)))

        self.sidePanelNodeLayout.add_widget(Label(text="GigabitEthernet0/0:", size_hint=(1, None), height=30))
        input_field = TextInput(text="192.168.0.1", size_hint=(1, None), height=30)
        self.sidePanelNodeLayout.add_widget(input_field)

        interfaces = self.netManager.getNodeInterfaces(instance)
        for label, (ip, conn) in interfaces.items():
            print('Interface:', label, 'ip:', ip)
            self.sidePanelNodeLayout.add_widget(Label(text=label, size_hint=(1, None)))
            input_field = TextInput(text=ip, multiline=False, size_hint=(1, None))
            cb = functools.partial(self.on_node_edit, conn, instance)
            input_field.bind(on_text_validate=cb)
            self.sidePanelNodeLayout.add_widget(input_field)

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

        if self.sidePanelNodeTab.text == self.pendingNodeRef.children[0].text:
            self.sidePanelTabbedPanel.remove_widget(self.sidePanelNodeTab)
            self.sidePanelTabbedPanel.switch_to(self.sidePanelLogTab)

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
        nodeLabel.text = self.netManager.getNodeName(nodeButton)

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
        nodeLabel.text = self.netManager.getNodeName(nodeButton)

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

    def on_node_edit(self, connection, node_button, text_input):
        print('Changing address of', node_button, 'to', text_input.text)

        # TODO: Actual address change

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
