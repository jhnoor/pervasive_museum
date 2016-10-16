#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, persistence

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition

import config
# For the app
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from model import Player
from kivy.properties import StringProperty, NumericProperty, ListProperty

Builder.load_file(os.path.join(os.path.dirname(__file__), 'playerscreen.kv'))


class StartScreenBoxLayout(BoxLayout):
    """Splash screen"""
    background_color = ListProperty(config.colors['brand'])
    msg = StringProperty()


class PlayerBoxLayout(BoxLayout):
    """Each player's box showing stats, level, ready button etc."""
    background_color = ListProperty([])
    ready_color = ListProperty(config.colors['green'])
    cancel_color = ListProperty(config.colors['red'])
    powerup_color = ListProperty(config.colors['grey'])
    is_ready = False
    ready_button_text = StringProperty("Klar?")

    name = StringProperty()  # TODO objectproperty?
    uid = StringProperty()
    icon_url = StringProperty()
    xp = NumericProperty()
    level = StringProperty()
    progress = NumericProperty()
    trophies = ListProperty([])
    powerups = ListProperty([])

    def __init__(self, player, player_number):
        super(PlayerBoxLayout, self).__init__()
        self.name = player.name
        self.uid = player.badge_uid
        self.icon_url = player.icon_url
        self.progress = config.check_progress_level_up(player.level, player.xp)['progress']
        self.level = str(player.level)
        self.background_color = config.colors['player1_bg'] if player_number == 1 else config.colors['player2_bg']
        self.player_object = player

    def toggle_ready(self):
        if self.is_ready:
            self.is_ready = False
            self.ready_button_text = "Klar?"
            self.ready_color = config.colors['green']
        else:
            self.is_ready = True
            self.ready_button_text = "Venter på andre spiller"
            self.ready_color = config.colors['grey']

    def cancel(self, *args):
        self.is_ready = False
        self.parent.parent.remove_player(self)  # parent.parent because of MainGridLayout


class MainGridLayout(GridLayout):
    """The main grid with columns for each player"""
    pass


class PlayerScreen(Screen):
    background_color = ListProperty(config.colors['brand'])
    start_screen_layout = StartScreenBoxLayout()
    main_grid_layout = MainGridLayout()
    events = []

    def __init__(self, sm, **kwargs):
        super(PlayerScreen, self).__init__(**kwargs)
        self.sm = sm
        self.main_grid_layout.add_widget(self.start_screen_layout)
        self.add_widget(self.main_grid_layout)
        self.players_boxes = []

    def on_enter(self):
        refresh_time = 1  # poll arduino at this rate
        self.events.append(Clock.schedule_interval(self.read_rfid, refresh_time))
        self.refresh_main_grid_layout()

    def on_leave(self, *args):
        print "Leaving playerscreen!"
        map(lambda event: event.cancel(), self.events)

    def read_rfid(self, event):
        read_uid = str(config.arduino.readline()).strip()
        print "player_screen: " + read_uid

        if len(read_uid) != 8 or len(persistence.current_players) == config.MAX_PLAYERS:
            return
        elif any(player.badge_uid == read_uid for player in persistence.current_players):  # if badge already registered
            self.start_screen_layout.msg = "Du er allerede innlogget"
        else:
            print "UID: " + read_uid
            self.start_screen_layout.msg = "Logger deg inn! Vent"
            request = config.request(config.GET_BADGES(), 'GET')
            if request.status_code == 200:
                self.success(request, read_uid)  # Request successful, now check if badge is valid
            else:
                self.error(request.status_code, request.json())

    def add_player(self, result, uid):  # TODO DRY this
        if result['active_player'] is None:
            request = config.request(config.POST_NEW_PLAYER(result['id']), 'POST', data={'data': 'None'})
            if request.status_code == 200:
                print "New player: "
                active_player_pk = request.json()
                print "player_" + str(active_player_pk)
            else:
                self.error(request.status_code, "Failed to post new player")
                return
        else:
            active_player_pk = result['active_player']

        request = config.request(config.GET_PLAYERS(active_player_pk), 'GET')
        persistence.current_players.append(Player(request.json(), uid))


        self.refresh_main_grid_layout()

        # Poll both players for ready or cancel changes
        refresh_time = 1
        self.events.append(Clock.schedule_interval(self.poll_players_ready, refresh_time))

    def refresh_main_grid_layout(self):
        self.main_grid_layout.clear_widgets()
        self.players_boxes = []

        for index, player in enumerate(persistence.current_players):
            self.players_boxes.append(PlayerBoxLayout(player, index + 1))
            self.main_grid_layout.add_widget(self.players_boxes[-1])

        if len(persistence.current_players) < 2:
            self.main_grid_layout.add_widget(self.start_screen_layout)

    def remove_player(self, player_box):
        persistence.remove_player(player_box)
        self.refresh_main_grid_layout()

    def success(self, request, uid):
        print "Success!"
        data = request.json()
        self.start_screen_layout.msg = ""
        for result in data['results']:
            if result['uid'] == uid:
                self.add_player(result, uid)  # UID is valid, now show player on player screen
                return

        self.error(404, "Brikke '" + uid + "' ikke funnet!")

    def error(self, status_code, data):
        print "Error: " + str(status_code)
        self.start_screen_layout.msg = "Nettverksfeil: " + str(data)
        self.on_enter()

    def poll_players_ready(self, event):
        if len(self.players_boxes) == 2 and all(player.is_ready for player in self.players_boxes):
            self.sm.transition = SlideTransition()
            self.sm.current = "menu_screen"


class PlayerScreenApp(App):
    def build(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    PlayerScreenApp().run()
