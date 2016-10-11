from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, NoTransition

import config
# For the app
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from player import Player
from arduino import arduino
from kivy.properties import StringProperty, NumericProperty, ListProperty

Builder.load_file(config.KV_PATH('screens/player/playerscreen.kv'))


class StartScreenLayout(BoxLayout):
    background_color = ListProperty(config.colors['brand'])


class PlayerBoxLayout(BoxLayout):
    background_color = ListProperty(config.colors['contrast_brand'])
    ready_color = ListProperty(config.colors['green'])
    cancel_color = ListProperty(config.colors['red'])
    powerup_color = ListProperty(config.colors['grey'])

    player_name = StringProperty()  # TODO objectproperty?
    player_icon_url = StringProperty()
    player_xp = NumericProperty()
    player_level = StringProperty()
    player_progress = NumericProperty()
    player_trophies = ListProperty([])
    player_powerups = ListProperty([])

    def __init__(self, player, **kwargs):
        super(PlayerBoxLayout, self).__init__(**kwargs)
        self.player_name = player.name
        self.player_icon_url = player.icon_url
        self.player_progress = config.get_level_progress_percentage(player.level, player.xp)
        self.player_level = str(player.level)


class PlayerScreen(Screen):
    # Kivy properties
    background_color = ListProperty(config.colors['brand'])


    # Players
    global player_1
    global player_2
    global uid_1
    global uid_2

    def __init__(self, sm, **kwargs):
        super(PlayerScreen, self).__init__(**kwargs)
        self.sm = sm

    def on_enter(self):
        refresh_time = 1  # poll arduino at this rate
        self.event = Clock.schedule_interval(self.read_rfid, refresh_time)

        # Fill in player_data
        player_1_boxlayout = PlayerBoxLayout(self.player_1)

        # Add start widgets to box
        main_layout = GridLayout(cols=2)
        main_layout.add_widget(player_1_boxlayout)
        main_layout.add_widget(StartScreenLayout())
        self.add_widget(main_layout)

    def read_rfid(self, event):
        read_uid = str(arduino.readline()).strip()
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

    def open_ready(self, result, uid):  # TODO DRY this
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


class PlayerScreenApp(App):
    def build(self):
        return PlayerScreenBtn(text="open my app")

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    PlayerScreenApp().run()
