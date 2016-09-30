import os
import serial

from kivy.lang import Builder

from kivy.uix.screenmanager import Screen, SlideTransition

# For the app
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock

CURRENT_PATH = os.path.dirname(__file__)

KV_PATH = os.path.join(CURRENT_PATH, 'playerscreen.kv')
Builder.load_file(KV_PATH)

class PlayerScreen(Screen):

    # Players
    global player_1
    global player_2

    def __init__(self, sm, **kwargs):
        super(PlayerScreen, self).__init__(**kwargs)
        self.sm = sm
        self.arduino = self.sm.get_screen("start_screen").arduino

        # Constantly read for rfid
        refresh_time = 1  # poll arduino at this rate
        self.event = Clock.schedule_interval(self.read_rfid, refresh_time)

    def read_rfid(self, event):
        next_line = self.arduino.readline()

        if len(next_line) >= 8 and next_line != self.player_1:
            print "Player 2: "+next_line
            self.player_2 = next_line
            self.event.cancel()
            # TODO send player_2 to server with request log_in and terminal name
            # If request to log in times out call self.event and return
            # otherwise:
            self.open_menu()

    def open_menu(self):
        self.sm.transition = SlideTransition(direction="left")
        self.sm.current = "menu_screen"


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