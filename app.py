from kivy.app import App
from kivy.clock import Clock
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

    def clicknode(self, instance):
        Clock.schedule_once(lambda dt: self.remove_widget(instance), 0.2)

    def on_touch_down(self, touch, after=False):
        if after and self.collide_point(touch.pos[0], touch.pos[1]):
            if touch.button == "right":
                nodebutton = Button(pos=(touch.x - 20, touch.y - 20), size_hint=(None, None), size=(40, 40))
                nodebutton.bind(on_press=self.clicknode)
                self.add_widget(nodebutton)
                return True
        else:
            Clock.schedule_once(lambda dt: self.on_touch_down(touch, True), 0.01)
            return super(Demoer, self).on_touch_down(touch)


class DemoApp(App):
    def build(self):
        Window.size = (800, 600)
        return Demoer()
