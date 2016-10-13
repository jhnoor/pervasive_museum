import os

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

# For the app
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

Builder.load_file(os.path.join(os.path.dirname(__file__), 'coopgamescreen.kv'))

class CoopGameScreen(Screen):
    def __init__(self, sm, **kwargs):
        super(CoopGameScreen, self).__init__(**kwargs)
        self.sm = sm

    #TODO game has started, do something


class CoopGameScreenBtn(Button):
    def __init__(self, **kwargs):
        super(CoopGameScreenBtn, self).__init__(self, **kwargs)
        self.bind(on_press=self.callback)

    def callback(self, instance):
        content = BoxLayout(orientation="vertical")
        my_main_app = CoopGameScreen("dummy_screen_monitor")
        btnclose = Button(text="Close", size_hint_y=None, size_hint_x=1)
        content.add_widget(my_main_app)
        content.add_widget(btnclose)
        popup = Popup(content=content, title="my_app", size_hint=(1, 1), auto_dismiss=False)
        btnclose.bind(on_release=popup.dismiss)
        popup.open()