import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition
from screens.game.coopgamescreen import CoopGameScreen
from screens.game.versusgamescreen import VersusGameScreen
from screens.score.coopscorescreen import CoopScoreScreen
from screens.score.versusscorescreen import VersusScoreScreen


# Builder.load_file(os.path.join(os.path.dirname(__file__), 'menuscreen.kv'))

class MenuScreen(Screen):
    game_screen = None

    def __init__(self, sm, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.sm = sm

    def open_coop(self):
        self.sm.transition = SlideTransition(direction="left")
        self.sm.add_widget(CoopGameScreen(self.sm, name="game_screen"))
        self.sm.add_widget(CoopScoreScreen(self.sm, name="score_screen"))
        self.sm.current = "game_screen"

    def open_versus(self):
        self.sm.transition = SlideTransition(direction="left")
        self.sm.add_widget(VersusGameScreen(self.sm, name="game_screen"))
        self.sm.add_widget(VersusScoreScreen(self.sm, name="score_screen"))
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
