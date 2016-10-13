import os

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition

# For the app
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

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


class MenuScreenBtn(Button):
    def __init__(self, **kwargs):
        super(MenuScreenBtn, self).__init__(self, **kwargs)
        self.bind(on_press=self.callback)

    def callback(self, instance):
        content = BoxLayout(orientation="vertical")
        my_main_app = MenuScreen("dummy_screen_monitor")
        btnclose = Button(text="Close", size_hint_y=None, size_hint_x=1)
        content.add_widget(my_main_app)
        content.add_widget(btnclose)
        popup = Popup(content=content, title="my_app", size_hint=(1, 1), auto_dismiss=False)
        btnclose.bind(on_release=popup.dismiss)
        popup.open()


class MenuScreenApp(App):
    def build(self):
        return MenuScreenBtn(text='open my app')

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    MenuScreenApp().run()
