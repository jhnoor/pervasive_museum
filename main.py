#!/usr/bin/kivy

import kivy
kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from screens.start.startscreen import StartScreen
from screens.player.playerscreen import PlayerScreen
from screens.menu.menuscreen import MenuScreen
from screens.coop.coopgamescreen import CoopGameScreen
from screens.versus.versusgamescreen import VersusGameScreen


class MuseumGameApp(App):

    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(sm, name="start_screen"))
        sm.add_widget(PlayerScreen(sm, name="player_screen"))
        sm.add_widget(MenuScreen(sm, name="menu_screen"))
        sm.add_widget(CoopGameScreen(sm, name="coop_game_screen"))
        sm.add_widget(VersusGameScreen(sm, name="versus_game_screen"))
        return sm


    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    MuseumGameApp().run()