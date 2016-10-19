import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition
from screens.game.coopgamescreen import CoopGameScreen


#Builder.load_file(os.path.join(os.path.dirname(__file__), 'menuscreen.kv'))

class MenuScreen(Screen):
    game_screen = None

    def __init__(self, sm, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.sm = sm

    def open_game(self, game_type):
        self.sm.transition = SlideTransition(direction="left")
        # not created in main.py because need current_players in persistence when creating game screen
        self.game_screen = CoopGameScreen(self.sm, game_type, name="game_screen")
        self.sm.add_widget(self.game_screen)
        self.sm.current = "game_screen"

    def reset(self):
        pass

class MenuScreenApp(App):
    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    MenuScreenApp().run()
