import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition

from screens.coop.coopgamescreen import CoopGameScreen
from screens.score.scorescreen import ScoreScreen
from screens.versus.versusgamescreen import VersusGameScreen

Builder.load_file(os.path.join(os.path.dirname(__file__), 'menuscreen.kv'))


class MenuScreen(Screen):
    game_type_screen = None

    def __init__(self, sm, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.sm = sm

    def open_coop(self):
        self.sm.transition = SlideTransition(direction="left")
        self.game_type_screen = CoopGameScreen(self.sm, name="coop_game_screen")
        self.add_screen(self.game_type_screen)
        self.sm.current = "coop_game_screen"

    def open_versus(self):
        self.sm.transition = SlideTransition(direction="left")
        self.game_type_screen = VersusGameScreen(self.sm, name="versus_game_screen")
        self.add_screen(self.game_type_screen)
        self.sm.current = "versus_game_screen"

    def add_screen(self, game_type_screen):
        self.sm.add_widget(game_type_screen)
        self.sm.add_widget(ScoreScreen(self.sm, name="score_screen"))


class MenuScreenApp(App):
    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    MenuScreenApp().run()
