import functools
import enum

from kivy.animation import Animation
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
from kivy.uix.popup import Popup

Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

from Computer import DemoerException
from manager import NetworkManager

class ToolState(enum.Enum):
    EMPTY = 0
    SELECTING_CONNECTION_END = 1
    SELECTING_PACKET_NODE1 = 2
    SELECTING_PACKET_NODE2 = 3

class Demoer(FloatLayout):
    def __init__(self, *args, **kwargs):
        self.state = ToolState.EMPTY

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
        self.netManager = NetworkManager(self.__deleteLine, self.appendLog, self.animatePacket)

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

        # A welcome log
        self.appendLog('A new workspace has been created.')

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
        self.addPacketButton = Button(text="Nowy pakiet", on_press=self.on_new_packet)
        self.stepSimButton = Button(text=">|", on_press=self.on_step)
        self.playSimButton = Button(text=">")
        self.simButtonLayout = BoxLayout()
        self.sidePanelLogLayout.add_widget(self.addPacketButton)
        self.sidePanelLogLayout.add_widget(self.toggleSimButton)
        self.sidePanelLogLayout.add_widget(self.simButtonLayout)
        self.simButtonLayout.add_widget(self.playSimButton)
        self.simButtonLayout.add_widget(self.stepSimButton)

        self.packetNodes = []

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
        node_name = self.netManager.getNodeName(instance)
        self.sidePanelNodeTab.text = node_name

        if len(self.sidePanelTabbedPanel.children) == 2:
            self.sidePanelTabbedPanel.add_widget(self.sidePanelNodeTab)

        self.sidePanelTabbedPanel.switch_to(self.sidePanelNodeTab)

        self.sidePanelNodeLayout.clear_widgets()
        self.sidePanelNodeLayout.add_widget(Label(text="Interfejsy węzła " + node_name + ":", size_hint=(1, None)))

        interfaces = self.netManager.getNodeInterfaces(instance)
        for label, (ip, conn) in interfaces.items():
            self.sidePanelNodeLayout.add_widget(Label(text=label, size_hint=(1, None), height=30))
            input_field = TextInput(text=ip, multiline=False, size_hint=(1, None), height=30)
            cb = functools.partial(self.on_node_edit, conn, instance)
            input_field.bind(on_text_validate=cb)
            self.sidePanelNodeLayout.add_widget(input_field)

    # remove active bubble menus
    def clearBubbles(self):
        self.remove_widget(self.nodeBubble)
        self.remove_widget(self.defaultBubble)

    def __deleteLine(self, line):
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
    # OR select nodes for packet transmission
    def showNodeBubble(self, instance):
        if self.state == ToolState.SELECTING_PACKET_NODE1:
            self.packetNodes.append(instance)
            instance.background_color = (1, 0.5, 0.5, 1)
            self.state = ToolState.SELECTING_PACKET_NODE2
        elif self.state == ToolState.SELECTING_PACKET_NODE2:
            packetNodes = self.packetNodes.copy()
            packetNodes.append(instance)
            try:
                self.netManager.preparePacket(tuple(packetNodes))
            except DemoerException as e:
                self.showPopup('Error', e.message)
            else:
                instance.background_color = (1, 0.5, 0.5, 1)
                self.state = ToolState.EMPTY
                self.packetNodes.clear()
        else:
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
                    self.showPopup('Error', e.message)
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

    def animatePacket(self, sourceWidget, targetWidget):
        print('Animating')
        img = Image(source='Images/packet.png', pos=sourceWidget.pos)
        anim = Animation(x=targetWidget.pos[0], y=targetWidget.pos[1])
        self.add_widget(img)
        anim.start(img)


    def showPopup(self, title, content):
        popup = Popup(title=title,
                      content=Label(text=content),
                      size_hint=(None, None), size=(500, 200))
        popup.open()

    def appendLog(self, content):
        self.logField.text = self.logField.text + content + '\n\n'

    def on_step(self, instance):
        try:
            self.netManager.stepSimulation()
        except DemoerException as e:
            self.showPopup('Error', e.message)

    def on_new_packet(self, instance):
        if not self.state == ToolState.EMPTY:
            return

        self.state = ToolState.SELECTING_PACKET_NODE1

    def on_node_edit(self, connection, node_button, text_input):
        try:
            self.netManager.setAddress(node_button, connection, text_input.text)
        except DemoerException as e:
            self.showPopup('Error', e.message)

    def on_touch_down(self, touch, after=False):
        if after:
            self.remove_widget(self.defaultBubble)
            if self.workAreaXPos + self.workAreaXDim > touch.pos[0] > self.workAreaXPos \
                    and self.workAreaYPos + self.workAreaYDim > touch.pos[1] > self.workAreaYPos:
                if touch.button == "right":
                    if self.state != ToolState.EMPTY:
                        self.state = ToolState.EMPTY
                        self.packetNodes.clear()
                    else:
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
