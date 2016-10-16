#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, persistence

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
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

    def __init__(self, player):  # TODO extra argument pass xp for double xp powerup
        super(PlayerScoreFloatLayout, self).__init__()
        if player.questions_answered[-1]['is_correct']:
            self.background_color = config.colors['green']
            self.answer_feedback = "Korrekt"
            self.answer_color = config.colors['light_grey']
            self.allocate_points()
        else:
            self.background_color = config.colors['red']
            self.answer_feedback = "Feil"
            self.answer_color = config.colors['black']

        self.name = player.name
        self.icon_url = player.icon_url
        self.level = str(player.level)
        self.xp = player.xp
        self.progress = config.check_progress_level_up(player.level, player.xp)['progress']

    def allocate_points(self):
        """Fill self.xp gradually with DEFAULT_ADD_XP"""
        self.prev_xp = self.xp
        self.event = Clock.schedule_interval(self.inc_xp, 1 / 100)

    def inc_xp(self, dt=None):
        if self.xp - self.prev_xp >= config.DEFAULT_ADD_XP:
            self.event.cancel()
            self.event = Clock.schedule_once(self.parent.parent.back, config.score_screen_time_seconds)
            self.update_model()
            return
        self.xp += 1
        level_progress = config.check_progress_level_up(self.level, self.xp)
        if level_progress['level_up']:
            self.level = str(int(self.level) + 1)
            self.progress = 0
        else:
            self.progress = level_progress['progress']

    def update_model(self):
        persistence.update_player(name=self.name, xp=self.xp, level=self.level)


class ScoreScreen(Screen):
    final = False

    def __init__(self, sm, **kwargs):
        super(ScoreScreen, self).__init__(**kwargs)
        self.player_boxes = []
        self.players_grid = None
        self.sm = sm

    def on_enter(self, *args):
        if self.final:
            self.add_widget(Label(text="Final score"))

        for player in persistence.current_players:
            self.player_boxes.append(PlayerScoreFloatLayout(player))

        self.players_grid = PlayersScoreGridLayout()
        for player_box in self.player_boxes:
            self.players_grid.add_widget(player_box)

        self.add_widget(self.players_grid)

    def back(self, dt=None):
        self.sm.transition = SlideTransition(direction="right")
        if self.final:
            # TODO update powerups, trophies, level and xp to backend
            self.save()
            config.main.reset()
            return

        self.sm.current = self.sm.get_screen('menu_screen').game_type_screen.name

    def save(self):
        pass


class ScoreScreenApp(App):
    def build(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    ScoreScreenApp().run()
