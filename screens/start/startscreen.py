from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, SlideTransition

import config
from arduino import arduino
from player import Player

Builder.load_file(config.KV_PATH('screens/start/startscreen.kv'))


class StartScreen(Screen):
    bg = ListProperty(config.colors['brand'])

    def __init__(self, sm, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self.sm = sm
        self.uid_1 = ""
        print "init startscreen"

    def on_enter(self):
        refresh_time = 1  # poll arduino at this rate
        self.event = Clock.schedule_interval(self.read_rfid, refresh_time)

    def read_rfid(self, event):
        read_uid = str(arduino.readline()).strip()
        print read_uid
        print "read_uid must be 8 characters" if len(read_uid) != 8 else "read_uid ok"

        if len(read_uid) == 8:
            print "UID 1: " + read_uid
            self.uid_1 = read_uid
            self.event.cancel()

            self.ids.log_id.add_widget(Label(text="Logger deg inn! Vent", id="logger_deg_inn_id"))
            request = config.request(config.GET_BADGES(), 'GET')
            if request.status_code == 200:
                self.success(request, self.uid_1)  # Request successful, now check if badge is valid
            else:
                self.error(request.status_code, request.json())

    def open_player(self, result, uid):
        if result['active_player'] is None:
            request = config.request(config.POST_NEW_PLAYER(result['id']), 'POST',
                                     data={'data': 'None'})  # TODO should be post
            if request.status_code == 200:
                print "New player: "
                active_player_pk = request.json()
                print active_player_pk
            else:
                self.error(request.status_code, "Failed to post new player")
                return
        else:
            active_player_pk = result['active_player']

        request = config.request(config.GET_PLAYERS(active_player_pk), 'GET')
        player = Player(request.json(), uid)
        print player
        self.sm.get_screen("player_screen").player_1 = player

        self.sm.transition = SlideTransition(direction="left")
        self.sm.current = "player_screen"

    def success(self, request, uid):
        print "Success!"
        data = request.json()

        for result in data['results']:
            if result['uid'] == uid:
                self.open_player(result, uid)  # UID is valid, now open player for badge
                return

        self.error(404, "Brikke '" + uid + "' ikke funnet!")

    def error(self, status_code, data):
        print "Error: " + str(status_code)
        self.ids.log_id.add_widget(Label(text="Nettverksfeil: " + str(data), id="feil_id"))
        self.on_enter()


class StartScreenApp(App):
    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    StartScreenApp().run()
