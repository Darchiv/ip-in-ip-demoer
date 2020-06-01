from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.bubble import Bubble

Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window


class Demoer(FloatLayout):

    defaultBubble = Bubble(size_hint=(None, None), size=(100, 40))
    newNodeButton = Button(text="Nowy węzeł")
    defaultBubble.add_widget(newNodeButton)

    pendingNodePosX = 0
    pendingNodePosY = 0

    nodeBubble = Bubble(size_hint=(None, None), size=(250, 40))
    newConnButton = Button(text="Dodaj połączenie")
    deleteNodeButton = Button(text="Usuń węzeł")
    nodeBubble.add_widget(newConnButton)
    nodeBubble.add_widget(deleteNodeButton)

    pendingNodeRef = Button()

    def __init__(self, *args, **kwargs):
        Window.clearcolor=(0.7, 0.7, 0.7, 1)
        super(Demoer, self).__init__(*args, **kwargs)

    def deleteNode(self, instance):
        self.remove_widget(self.nodeBubble)
        self.remove_widget(self.defaultBubble)
        self.remove_widget(self.pendingNodeRef)

    def addNode(self, instance):
        nodebutton = Button(pos=(self.pendingNodePosY, self.pendingNodePosX), size_hint=(None, None), size=(40, 40))
        nodebutton.bind(on_press=self.showNodebubble)
        self.add_widget(nodebutton)

    def showNodebubble(self, instance):
        self.remove_widget(self.nodeBubble)
        self.remove_widget(self.defaultBubble)
        self.pendingNodeRef = instance
        self.nodeBubble.pos = (instance.pos[0]-105, instance.pos[1]+40)
        self.deleteNodeButton.bind(on_press=self.deleteNode)
        self.add_widget(self.nodeBubble)

    def showDefaultBubble(self, posx, posy):
        self.remove_widget(self.nodeBubble)
        self.remove_widget(self.defaultBubble)
        self.pendingNodePosY = posx - 20
        self.pendingNodePosX = posy - 20
        self.defaultBubble.pos = (posx-50, posy)
        self.newNodeButton.bind(on_press=self.addNode)
        self.add_widget(self.defaultBubble)

    def on_touch_down(self, touch, after=False):
        if after and self.collide_point(touch.pos[0], touch.pos[1]):
            self.remove_widget(self.defaultBubble)
            if touch.button == "right":
                self.showDefaultBubble(touch.x, touch.y)
                return True
        else:
            Clock.schedule_once(lambda dt: self.on_touch_down(touch, True), 0.01)
            return super(Demoer, self).on_touch_down(touch)


class DemoApp(App):
    def build(self):
        Window.size = (800, 600)
        return Demoer()
