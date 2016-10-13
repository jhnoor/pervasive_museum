#!/usr/bin/kivy

import kivy, config

kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from screens.player.playerscreen import PlayerScreen
from screens.menu.menuscreen import MenuScreen
from screens.coop.coopgamescreen import CoopGameScreen
from screens.versus.versusgamescreen import VersusGameScreen
from terminal import Terminal


class MuseumGameApp(App):
    def build(self):
        # Get available terminal and set to online
        request = config.request(config.GET_TERMINALS(), "GET")
        if request.status_code == 200:
            self.success(request)
        else:
            self.error(request)

        sm = ScreenManager()
        sm.add_widget(PlayerScreen(sm, name="player_screen"))
        sm.add_widget(MenuScreen(sm, name="menu_screen"))
        sm.add_widget(CoopGameScreen(sm, name="coop_game_screen"))
        sm.add_widget(VersusGameScreen(sm, name="versus_game_screen"))
        return sm

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        config.request(config.PUT_SET_OFFLINE(config.current_terminal), "PUT", data={'data': 'None'})


    def success(self, request):
        print "success getting terminals"
        # Find offline terminal and activate
        # Set current_terminal
        for result in request.json()['results']:
            if not result['online']:
                config.current_terminal = Terminal(result)
                config.request(config.PUT_SET_ONLINE(config.current_terminal.id), "PUT", data={'data': 'None'})
                print "success setting "+str(config.current_terminal)
                return
        self.stop()

    def error(self, request):
        print "error setting terminal online"
        print request.json()

if __name__ == '__main__':
    MuseumGameApp().run()
