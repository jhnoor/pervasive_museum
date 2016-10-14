import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition

Builder.load_file(os.path.join(os.path.dirname(__file__), 'menuscreen.kv'))


class MenuScreen(Screen):
    def __init__(self, sm, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.sm = sm

    def open_coop(self):
        self.sm.transition = SlideTransition(direction="left")
        self.sm.current = "coop_game_screen"

    def open_versus(self):
        self.sm.transition = SlideTransition(direction="left")
        self.sm.current = "versus_game_screen"


class MenuScreenApp(App):
    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    MenuScreenApp().run()
