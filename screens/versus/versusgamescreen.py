from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

import config

Builder.load_file(config.KV_PATH('screens/versus/versusgamescreen.kv'))


class VersusGameScreen(Screen):
    def __init__(self, sm, **kwargs):
        super(VersusGameScreen, self).__init__(**kwargs)
        self.sm = sm

        # TODO game has started, do something


class VersusGameScreenApp(App):
    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    VersusGameScreenApp().run()
