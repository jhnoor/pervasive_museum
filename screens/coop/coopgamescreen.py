import os, config

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

# For the app
from kivy.app import App
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.image import AsyncImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock

Builder.load_file(os.path.join(os.path.dirname(__file__), 'coopgamescreen.kv'))


class PowerupLayout(FloatLayout):
    quantity = NumericProperty()

    def __init__(self, powerup, **kwargs):
        super(PowerupLayout, self).__init__(**kwargs)
        print powerup
        # TODO


class PowerupGridLayout(GridLayout):
    cols = NumericProperty()

    def __init__(self, number_of_powerups, **kwargs):
        super(PowerupGridLayout, self).__init__(**kwargs)
        self.cols = number_of_powerups


class PlayerXpProgressBar(ProgressBar):
    value = NumericProperty()


class PlayerLayout(GridLayout):
    def __init__(self, player, **kwargs):
        super(PlayerLayout, self).__init__(**kwargs)
        # Set initial data
        self.level = Label(text="lvl "+str(player.get_level()))
        self.xp_progress_bar = PlayerXpProgressBar()
        self.xp_progress_bar.value = config.get_level_progress_percentage(player.get_level(), player.get_xp())
        self.powerups_grid = PowerupGridLayout(len(player.powerups))

        for powerup in player.powerups:
            self.powerups_grid.add_widget(PowerupLayout(powerup))  # Add powerup to grid

        self.add_widget(self.powerups_grid)
        self.add_widget(self.level)
        self.add_widget(self.xp_progress_bar)


class ImageButton(ButtonBehavior, AsyncImage):
    pass

class PlayersGridLayout(GridLayout):
    background_color = config.colors['dark_grey']

    def __init__(self, **kwargs):
        super(PlayersGridLayout, self).__init__(**kwargs)


class TimeProgressBar(ProgressBar):
    max = NumericProperty(config.question_time_seconds * 100)
    value = NumericProperty(config.question_time_seconds * 100)

    def __init__(self, **kwargs):
        super(TimeProgressBar, self).__init__(**kwargs)

    def countdown(self):
        refresh_time = 1 / 100  # in seconds
        self.event = Clock.schedule_interval(self.decrement_clock, refresh_time)

    def decrement_clock(self, event):
        if self.value > 1:
            self.value -= 1
        else:
            self.parent.parent.time_out()
            self.event.cancel()


# Three column grid that that has left_picture, question_text and right_picture
class QuestionGrid(GridLayout):
    background_color = config.colors['player1_bg']
    current_index = 0

    def __init__(self, **kwargs):
        super(QuestionGrid, self).__init__(**kwargs)

    def next_question(self):
        if len(config.current_terminal.questions) > self.current_index + 1:
            self.current_index += 1
        else:
            return False

    def get_left_picture(self):
        return config.filename_to_url(config.current_terminal.questions[self.current_index]['left_picture_url'])

    def get_right_picture(self):
        return config.filename_to_url(config.current_terminal.questions[self.current_index]['right_picture_url'])

    def get_text(self):
        return config.current_terminal.questions[self.current_index]['text']

    def left_pressed(self):
        print "Left button pressed"

    def right_pressed(self):
        print "Right button pressed"


class MainLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)


class CoopGameScreen(Screen):
    background_color = config.colors['player2_bg']
    player_boxes = []

    def __init__(self, sm, **kwargs):
        super(CoopGameScreen, self).__init__(**kwargs)
        self.sm = sm
        self.countdown_progressbar = TimeProgressBar()
        self.question_grid = QuestionGrid()
        self.main_layout = MainLayout()  # This layout will contain everything
        self.players_grid = PlayersGridLayout()  # This holds the two players layouts at the bottom

    def on_enter(self, *args):
        self.player_boxes = self.sm.get_screen("player_screen").players

        self.draw_screen()
        self.play()
        self.allocate_points()

    def draw_screen(self):
        self.main_layout.add_widget(self.question_grid)
        self.main_layout.add_widget(self.countdown_progressbar)

        self.player_1_layout = PlayerLayout(self.player_boxes[0].player_object)
        self.player_2_layout = PlayerLayout(self.player_boxes[1].player_object)
        self.players_grid.add_widget(self.player_1_layout)
        self.players_grid.add_widget(self.player_2_layout)

        self.main_layout.add_widget(self.players_grid)

        self.add_widget(self.main_layout)

    def play(self):
        self.countdown_progressbar.countdown()

    # Question wasn't answered in time, no one gets points TODO different for versus
    def time_out(self):
        print "Time out!"

    def allocate_points(self):
        pass  # Allocate points and return none


class CoopGameScreenApp(App):
    def build(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    CoopGameScreenApp().run()
