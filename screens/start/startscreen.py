import os, serial, config

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest


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

    def __init__(self, sm, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        self.sm = sm
        self.arduino = arduino
        print "init startscreen"

    def on_enter(self):
        refresh_time = 1  # poll arduino at this rate
        self.event = Clock.schedule_interval(self.read_rfid, refresh_time)

    def read_rfid(self, event):
        next_line = arduino.readline()
        print next_line
        print "next_line too short" if len(next_line) < 8 else "next_line should pass!"

        if len(next_line) >= 8:
            print "Player 1: " + next_line
            self.sm.get_screen("player_screen").player_1 = next_line
            self.event.cancel()

            self.ids.log_id.add_widget(Label(text="Logger deg inn! Vent", id="logger_deg_inn_id"))
            request = UrlRequest(config.api['base_url']+ config.api['end_url'], on_success=self.success, on_error=self.error,
                                 req_headers=config.headers)


    def open_player(self):
        self.sm.transition = SlideTransition(direction="left")
        self.sm.current = "player_screen"

    def success(self, request, result):
        print "Success!"
        print request
        print "Result:"
        print result
        # TODO create models for the api
        self.open_player()

    def error(self, request, error):
        print "Error"
        print type(error)
        print error
        self.ids.log_id.add_widget(Label(text="Nettverksfeil: "+str(error), id="feil_id"))
        print self.ids.log_id.children
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
        popup = Popup(content=content, title="my_app", size_hint=(1,1), auto_dismiss=False)
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