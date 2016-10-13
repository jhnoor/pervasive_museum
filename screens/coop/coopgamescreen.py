import os, config

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

# For the app
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock

Builder.load_file(os.path.join(os.path.dirname(__file__), 'coopgamescreen.kv'))


# TODO seperate player-specific layouts into different file
# A single powerup
class PowerupLayout(FloatLayout):
    pass


class PowerupGridLayout(GridLayout):
    pass


class PlayerBoxLayout(BoxLayout):
    pass


class TimeProgressBar(ProgressBar):
    max = NumericProperty(config.question_time_seconds*100)
    value = NumericProperty(config.question_time_seconds*100)

    def countdown(self):
        refresh_time = 1/100  # 1 second
        self.event = Clock.schedule_interval(self.decrement_clock, refresh_time)

    def decrement_clock(self, event):
        if self.value > 1:
            self.value -= 1
            print "decrementing clock"
        else:
            self.parent.parent.time_out()
            self.event.cancel()


# Three column grid that that has left_picture, question_text and right_picture
class QuestionGrid(GridLayout):
    background_color = config.colors['player1_bg']
    current_index = 0

    def next_question(self):
        if len(config.current_terminal.questions) > self.current_index+1:
            self.current_index += 1
        else:
            return False

    def get_left_picture(self):
        return config.filename_to_url(config.current_terminal.questions[self.current_index]['left_picture_url'])

    def get_right_picture(self):
        return config.filename_to_url(config.current_terminal.questions[self.current_index]['right_picture_url'])

    def get_text(self):
        return config.current_terminal.questions[self.current_index]['text']


class MainLayout(FloatLayout):
    pass

class CoopGameScreen(Screen):
    background_color = config.colors['grey']

    def __init__(self, sm, **kwargs):
        super(CoopGameScreen, self).__init__(**kwargs)
        self.sm = sm
        self.countdown_progressbar = TimeProgressBar()

    def on_enter(self, *args):
        self.draw_screen()
        self.play()
        self.allocate_points()

    def draw_screen(self):
        self.main_layout = MainLayout()  # This layout will contain everything
        self.main_layout.add_widget(QuestionGrid())
        self.main_layout.add_widget(self.countdown_progressbar)


        self.add_widget(self.main_layout)

    def play(self):
        self.countdown_progressbar.countdown()

    # Question wasn't answered in time, no one gets points TODO different for versus
    def time_out(self):
        print "Time out!"

    def allocate_points(self):
        pass # Allocate points and return none


class CoopGameScreenApp(App):
    def build(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    CoopGameScreenApp().run()
