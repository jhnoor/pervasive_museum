#!/usr/bin/kivy

import kivy, config, persistence

kivy.require('1.9.1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from screens.player.playerscreen import PlayerScreen
from screens.menu.menuscreen import MenuScreen
from screens.game.gamescreen import GameScreen
from screens.score.scorescreen import ScoreScreen
from model import Terminal


class MuseumGameApp(App):
    def build(self):
        # Get available terminal and set to online
        request = config.request(config.GET_TERMINALS(), "GET")
        if request.status_code == 200:
            self.success(request)
        else:
            self.error(request)
            raise RuntimeError(str(request.status_code)+" Error getting terminals, check connection: "+str(request.json()))

        self.sm = ScreenManager()
        self.sm.add_widget(PlayerScreen(self.sm, name="player_screen"))
        self.sm.add_widget(MenuScreen(self.sm, name="menu_screen"))
        self.sm.add_widget(GameScreen(self.sm, name="game_screen"))
        self.sm.add_widget(ScoreScreen(self.sm, name="score_screen"))
        config.main = self
        return self.sm

    def reset(self):
        """Resets everything"""
        del persistence.current_players[:]

        for screen_name in self.sm.screen_names:
            self.sm.get_screen(screen_name).reset()

        self.sm.current = "player_screen"

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def on_stop(self):
        config.request(config.PUT_SET_OFFLINE(config.current_terminal.id), "PUT", data={'data': 'None'})

    def success(self, request):
        print "success getting terminals"
        # Find offline terminal and activate
        # Set current_terminal
        for result in request.json()['results']:
            if not result['online']:
                config.current_terminal = Terminal(result)
                config.request(config.PUT_SET_ONLINE(config.current_terminal.id), "PUT", data={'data': 'None'})
                print "success setting " + str(config.current_terminal)
                return
        raise RuntimeError("No available terminals! Deactivate using Django Rest framework interface")

    def error(self, request):
        print "error setting terminal online"
        print request.json()


if __name__ == '__main__':
    MuseumGameApp().run()
