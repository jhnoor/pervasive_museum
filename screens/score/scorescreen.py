#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, persistence, config, random, json, time

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, SlideTransition
from screens.game.gamescreen import PowerupLayout

#Builder.load_file(os.path.join(os.path.dirname(__file__), 'scorescreen.kv'))

class PlayersScoreGridLayout(GridLayout):
    def reset(self):
        self.clear_widgets()

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
            ##self.allocate_points()
        else:
            self.background_color = config.colors['red']
            self.answer_feedback = "Feil"
            self.answer_color = config.colors['black']

        self.name = player.name
        self.icon_url = player.icon_url
        self.level = str(player.level)
        self.xp = player.xp
        self.progress = config.check_progress_level_up(player.level, player.xp)['progress']
        self.player = player

    def allocate_points(self):
        """Fill self.xp gradually with DEFAULT_ADD_XP"""
        if self.player.questions_answered[-1]['is_correct']:
            self.prev_xp = self.xp
            self.event = Clock.schedule_interval(self.inc_xp, 1 / 60)

    def inc_xp(self, dt=None):
        if self.xp - self.prev_xp >= config.DEFAULT_ADD_XP:
            self.event.cancel()
            #self.back()
            self.update_model()
            return
        self.xp += 1
        level_progress = config.check_progress_level_up(self.level, self.xp)
        if level_progress['level_up']:
            self.level_up()
        else:
            self.progress = level_progress['progress']

    def level_up(self):
        """Leveling up gives you a free powerup!"""
        powerup_index = random.randrange(len(self.player.powerups))
        self.player.powerups[powerup_index]['quantity'] += 1
        powerup_widget = PowerupLayout(self.player.powerups[powerup_index])
        powerup_widget.pos_hint = {"center_x": 0.5, "top": 0.5}
        powerup_widget.size_hint = (0.8, None)
        powerup_widget.on_press = config.do_nothing
        # TODO do animation
        self.add_widget(powerup_widget)
        self.level = str(int(self.level) + 1)
        self.progress = 0

    def update_model(self):
        print "in playerscorefloatlayout update_model"
        persistence.update_player(name=self.name, xp=self.xp, level=self.level,
                                  powerups=self.player.powerups)

    def reset(self):
        pass


class ScoreScreen(Screen):


    def __init__(self, sm, **kwargs):
        super(ScoreScreen, self).__init__(**kwargs)
        self.player_boxes = []
        self.players_grid = PlayersScoreGridLayout()
        self.sm = sm
        self.final = False

    def on_enter(self, *args):
        print "scorescreen on_enter"
        # TODO too much iteration starts here

        if self.final:
            final_score_label = Label(text="Final score", pos_hint={"top": 1, "center_x": 0.5},
                                      font_size=str(self.width * 0.05) + "sp", size_hint=(None, None))
            self.add_widget(final_score_label)

        self.players_grid = PlayersScoreGridLayout()
        for player in persistence.current_players:
            self.players_grid.add_widget(PlayerScoreFloatLayout(player))

        self.get_or_add_widget(self.players_grid)
        for player_box in self.players_grid.children:
            player_box.allocate_points()


    def get_or_add_widget(self, reference_to_widget):
        if reference_to_widget in self.children:
            print "Already has widget!"
            print reference_to_widget
        else:
            self.add_widget(reference_to_widget)

    def back(self, dt=None):
        print "scorescreen back"
        self.save()

        self.sm.transition = SlideTransition(direction="right")
        if self.final:
            config.main.reset()
            return

        self.sm.current = self.sm.get_screen('player_screen').game_type_screen.name

    def save(self):
        """Send persistence models to backend and save progress"""
        for player in persistence.current_players:
            print json.dumps(player.__dict__)
            request = config.request(config.PUT_UPDATE_PLAYER(player.id), "PUT", data={"player": json.dumps(player.__dict__)})
            if request.status_code != 200:
                print ("Failed to save player "+str(player.name))


    def reset(self):
        print "Resetting scorescreen"
        del self.player_boxes[:]
        self.final = False
        self.players_grid.reset()


class ScoreScreenApp(App):
    def build(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    ScoreScreenApp().run()
