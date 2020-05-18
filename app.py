from kivy.app import App
from kivy.uix.widget import Widget

class DemoWidget(Widget):
    pass

class DemoApp(App):
    def build(self):
        return DemoWidget()
