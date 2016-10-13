#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, WipeTransition

import config
# For the app
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from player import Player
from kivy.properties import StringProperty, NumericProperty, ListProperty

Builder.load_file(os.path.join(os.path.dirname(__file__), 'playerscreen.kv'))


class StartScreenBoxLayout(BoxLayout):
    background_color = ListProperty(config.colors['brand'])
    msg = StringProperty()


class PlayerBoxLayout(BoxLayout):
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

    def __init__(self, player, player2_bg):
        super(PlayerBoxLayout, self).__init__()
        self.name = player.name
        self.uid = player.badge_uid
        self.icon_url = player.icon_url
        self.progress = config.get_level_progress_percentage(player.level, player.xp)
        self.level = str(player.level)
        self.background_color = config.colors['player1_bg'] if player2_bg else config.colors['player2_bg']

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
        if hasattr(self, "ready_modal_view"):
            self.ready_modal_view.dismiss()
        else:
            self.parent.parent.remove_player(self)  # parent.parent because of Gridlayout


class MainGridLayout(GridLayout):
    pass


class PlayerScreen(Screen):
    background_color = ListProperty(config.colors['brand'])
    start_screen_layout = StartScreenBoxLayout()
    main_grid_layout = MainGridLayout()

    def __init__(self, sm, **kwargs):
        super(PlayerScreen, self).__init__(**kwargs)
        self.sm = sm
        self.main_grid_layout.add_widget(self.start_screen_layout)
        self.add_widget(self.main_grid_layout)
        self.players = []

    def on_enter(self):
        refresh_time = 1  # poll arduino at this rate
        self.event = Clock.schedule_interval(self.read_rfid, refresh_time)

    def on_leave(self, *args):
        print "Leaving playerscreen!"
        self.event.cancel()

    def read_rfid(self, event):
        read_uid = str(config.arduino.readline()).strip()
        print "player_screen: " + read_uid

        if len(read_uid) != 8:
            return
        elif any(player.uid == read_uid for player in self.players):  # if badge already registered
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
        self.players.append(PlayerBoxLayout(Player(request.json(), uid), (len(self.players) % 2 == 0)))
        print self.players[-1]

        self.refresh_main_grid_layout()

        # Poll both players for ready or cancel changes
        refresh_time = 1
        self.event = Clock.schedule_interval(self.poll_players_ready, refresh_time)

    def refresh_main_grid_layout(self):
        self.main_grid_layout.clear_widgets()

        for player in self.players:
            self.main_grid_layout.add_widget(player)  # get last item in list

        if len(self.players) < 2:
            self.main_grid_layout.add_widget(self.start_screen_layout)

    def remove_player(self, player):
        self.players.remove(player)
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
        if len(self.players) == 2 and all(player.is_ready for player in self.players):
            self.sm.transition = WipeTransition()
            self.sm.current = "coop_game_screen" # TODO set to menu_screen


class PlayerScreenApp(App):
    def build(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    PlayerScreenApp().run()
