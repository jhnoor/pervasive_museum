import os, serial, config

from kivy.lang import Builder

from kivy.uix.screenmanager import Screen, NoTransition

# For the app
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from player import Player

CURRENT_PATH = os.path.dirname(__file__)

KV_PATH = os.path.join(CURRENT_PATH, 'playerscreen.kv')
Builder.load_file(KV_PATH)


class PlayerScreen(Screen):
    # Players
    global player_1
    global player_2
    global uid_1
    global uid_2

    def __init__(self, sm, **kwargs):
        super(PlayerScreen, self).__init__(**kwargs)
        self.sm = sm
        self.arduino = self.sm.get_screen("start_screen").arduino

    def on_enter(self):
        refresh_time = 1  # poll arduino at this rate
        self.event = Clock.schedule_interval(self.read_rfid, refresh_time)

    def read_rfid(self, event):
        read_uid = str(self.arduino.readline()).strip()
        print read_uid

        if len(read_uid) == 8 and self.player_1.badge_uid != read_uid:
            print "UID 2: " + read_uid
            self.uid_2 = read_uid
            self.event.cancel()

            self.ids.log_id.add_widget(Label(text="Logger deg inn! Vent", id="logger_deg_inn_id"))
            request = config.request(config.GET_BADGES(), 'GET')
            if request.status_code == 200:
                self.success(request, read_uid)  # Request successful, now check if badge is valid
            else:
                self.error(request.status_code, request.json())



    def open_ready(self, result, uid): # TODO DRY this
        if result['active_player'] is None:
            request = config.request(config.POST_NEW_PLAYER(result['id']), 'POST', data={'data': 'None'})
            if request.status_code == 200:
                print "New player: "
                active_player_pk = request.json()
                print "player_"+str(active_player_pk)
            else:
                self.error(request.status_code, "Failed to post new player")
                return
        else:
            active_player_pk = result['active_player']

        request = config.request(config.GET_PLAYERS(active_player_pk), 'GET')
        self.player_2 = Player(request.json(), uid)
        print self.player_2

        self.sm.transition = NoTransition()
        self.sm.current = "ready_screen"

    def success(self, request, uid):
        print "Success!"
        data = request.json()

        for result in data['results']:
            if result['uid'] == uid:
                self.open_ready(result, uid)  # UID is valid, now show player on player screen
                return

        self.error(404, "Brikke '" + uid + "' ikke funnet!")

    def error(self, status_code, data):
        print "Error: " + str(status_code)
        self.ids.log_id.add_widget(Label(text="Nettverksfeil: " + str(data), id="feil_id"))
        self.on_enter()


class PlayerScreenBtn(Button):
    def __init__(self, **kwargs):
        super(PlayerScreenBtn, self).__init__(self, **kwargs)
        self.bind(on_press=self.callback)

    def callback(self, instance):
        content = BoxLayout(orientation="vertical")
        my_main_app = PlayerScreen("dummy_screen_monitor")
        btnclose = Button(text="Close", size_hint_y=None, size_hint_x=1)
        content.add_widget(my_main_app)
        content.add_widget(btnclose)
        popup = Popup(content=content, title="my_app", size_hint=(1, 1), auto_dismiss=False)
        btnclose.bind(on_release=popup.dismiss)
        popup.open()


class PlayerScreenApp(App):
    def build(self):
        return PlayerScreenBtn(text="open my app")

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    PlayerScreenApp().run()
