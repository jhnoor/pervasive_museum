import os, serial, config

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.network.urlrequest import UrlRequest
from player import Player

CURRENT_PATH = os.path.dirname(__file__)

KV_PATH = os.path.join(CURRENT_PATH, 'startscreen.kv')
Builder.load_file(KV_PATH)

# Arduino hook
try:
    arduino = serial.Serial('COM6', 9600, timeout=0)
except:
    print "No arduino detected, please connect to COM6"
    exit()


class StartScreen(Screen):
    bg = ListProperty(config.colors['brand'])

    def __init__(self, sm, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self.sm = sm
        self.arduino = arduino
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
            request = config.request(config.POST_NEW_PLAYER(result['id']), 'POST', data={'data': 'None'}) # TODO should be post
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


class StartScreenBtn(Button):
    def __init__(self, **kwargs):
        super(StartScreenBtn, self).__init__(self, **kwargs)
        self.bind(on_press=self.callback)

    def callback(self, instance):
        content = BoxLayout(orientation="vertical")
        my_main_app = StartScreen("dummy_screen_monitor")
        btnclose = Button(text="Close", size_hint_y=None, size_hint_x=1)
        content.add_widget(my_main_app)
        content.add_widget(btnclose)
        popup = Popup(content=content, title="my_app", size_hint=(1, 1), auto_dismiss=False)
        btnclose.bind(on_release=popup.dismiss)
        popup.open()


class StartScreenApp(App):
    def build(self):
        return StartScreenBtn(text="open my app")

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    StartScreenApp().run()
