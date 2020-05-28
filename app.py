from kivy.app import App
from kivy.config import Config

Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window


class Demoer(FloatLayout):

    def __init__(self, *args, **kwargs):
        super(Demoer, self).__init__(*args, **kwargs)
        nodebutton = Button(pos=(100, 100), size_hint=(None, None), size=(10, 10))
        nodebutton.bind(on_press=self.clicknode)
        self.add_widget(nodebutton)

    def clicknode(self, instance):
        self.remove_widget(instance)

    def on_touch_down(self, touch):
        if self.collide_point(touch.pos[0], touch.pos[1]):
            if touch.button == "right":
                nodebutton = Button(pos=(touch.x - 5, touch.y - 5), size_hint=(None, None), size=(10, 10))
                nodebutton.bind(on_press=self.clicknode)
                self.add_widget(nodebutton)
                return True


class DemoApp(App):
    def build(self):
        Window.size = (800, 600)
        return Demoer()
