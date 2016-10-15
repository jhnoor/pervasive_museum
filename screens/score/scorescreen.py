import os

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, SlideTransition

import config

Builder.load_file(os.path.join(os.path.dirname(__file__), 'scorescreen.kv'))


class PlayersScoreGridLayout(GridLayout):
    pass


class PlayerScoreFloatLayout(FloatLayout):
    background_color = ListProperty()
    name = StringProperty()
    icon_url = StringProperty()
    level = StringProperty()
    xp = NumericProperty()
    answer_feedback = StringProperty()
    answer_color = ListProperty([])
    progress = NumericProperty()

    def __init__(self, player_box, correct):
        super(PlayerScoreFloatLayout, self).__init__()
        if correct:
            self.background_color = config.colors['green']
            self.answer_feedback = "Korrekt"
            self.answer_color = config.colors['white']
            self.allocate_points()
        else:
            self.background_color = config.colors['red']
            self.answer_feedback = "Feil"
            self.answer_color = config.colors['black']

        self.name = player_box.name
        self.icon_url = player_box.icon_url
        self.level = player_box.level
        self.xp = player_box.xp
        self.progress = player_box.progress

    def allocate_points(self):
        """Fill self.xp gradually with DEFAULT_ADD_XP"""
        self.prev_xp = self.xp
        self.event = Clock.schedule_interval(self.inc_xp, 1 / 100)

    def inc_xp(self, dt=None):
        if self.xp - self.prev_xp >= config.DEFAULT_ADD_XP:
            self.event.cancel()
            return
        self.xp += 1


class ScoreScreen(Screen):
    player_1_box = None
    player_2_box = None
    player_scores = {}
    players_grid = None

    def __init__(self, sm, **kwargs):
        super(ScoreScreen, self).__init__(**kwargs)
        self.sm = sm
        print self.player_scores

    def on_enter(self, *args):
        previous_screen = self.sm.get_screen(self.sm.previous())
        player_boxes = previous_screen.player_boxes
        self.player_1_box = PlayerScoreFloatLayout(player_boxes[0], self.player_scores[player_boxes[0]])
        self.player_2_box = PlayerScoreFloatLayout(player_boxes[1], self.player_scores[player_boxes[1]])

        self.players_grid = PlayersScoreGridLayout()
        self.players_grid.add_widget(self.player_1_box)
        self.players_grid.add_widget(self.player_2_box)
        self.add_widget(self.players_grid)

        self.event = Clock.schedule_once(self.back, config.score_screen_time_seconds)

    def back(self, dt=None):
        self.sm.transition = SlideTransition(direction="right")
        self.sm.current = self.sm.get_screen('menu_screen').game_type_screen.name


class ScoreScreenApp(App):
    def build(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    ScoreScreenApp().run()
