import os

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition

import config, persistence
# For the app
from kivy.app import App
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import AsyncImage
from kivy.uix.progressbar import ProgressBar
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock

Builder.load_file(os.path.join(os.path.dirname(__file__), 'coopgamescreen.kv'))

ALLOWED_POWERUPS = ['Ice age', 'Double XP', 'Hint']


class PowerupLayout(FloatLayout):
    name = StringProperty()
    quantity = NumericProperty()
    icon_url = StringProperty()
    id = NumericProperty()

    def __init__(self, powerup, **kwargs):
        super(PowerupLayout, self).__init__(**kwargs)
        if (powerup['name'] not in ALLOWED_POWERUPS):
            raise ValueError("Powerup " + powerup['name'] + " not allowed")

        self.name = powerup['name']
        self.quantity = powerup['quantity']
        self.icon_url = config.filename_to_url(powerup['icon_url'])
        self.id = powerup['id']

        self.ids.button_id.disabled = self.quantity <= 0  # Disable button if quantity is zero

    def use_powerup(self):
        # disable button since its used now (a powerup can only be used once) TODO maybe no powerups after first?
        # also change color to show user this powerup is in play
        self.ids.button_id.disabled = True
        self.parent.parent.parent.parent.parent.use_powerup(self)


class PowerupsGridLayout(GridLayout):
    cols = NumericProperty()

    def __init__(self, number_of_powerups, **kwargs):
        super(PowerupsGridLayout, self).__init__(**kwargs)
        self.cols = number_of_powerups


class PlayerXpProgressBar(ProgressBar):
    progress = NumericProperty()

    def __init__(self, player, **kwargs):
        super(PlayerXpProgressBar, self).__init__(**kwargs)
        self.progress = player.get_level_progress()

class PlayerLayout(GridLayout):
    def __init__(self, player, **kwargs):
        super(PlayerLayout, self).__init__(**kwargs)
        # Set initial data
        self.level = Label(text="lvl " + str(player.get_level()))
        self.xp_progress_bar = PlayerXpProgressBar(player)
        self.powerups_grid = PowerupsGridLayout(len(player.powerups))

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

    def countdown(self, dt=None):
        refresh_time = 1 / 100  # in seconds
        self.event = Clock.schedule_interval(self.decrement_clock, refresh_time)

    def decrement_clock(self, dt):
        if self.value > 1:
            self.value -= 1
        else:
            self.event.cancel()
            self.parent.parent.time_out()

    def pause(self, seconds_to_pause):
        self.event.cancel()
        self.pause_event = Clock.schedule_once(self.countdown, seconds_to_pause)


# Three column grid that that has left_picture, question_text and right_picture
class QuestionGrid(GridLayout):
    background_color = config.colors['player1_bg']
    questions = []
    current_index = 0
    left_picture_url = StringProperty("")
    right_picture_url = StringProperty("")
    text = StringProperty("")
    hint = StringProperty("")
    question_id = None

    def __init__(self, **kwargs):
        super(QuestionGrid, self).__init__(**kwargs)
        self.questions = config.current_terminal.questions
        self.set_question_properties(self.questions[0])
        print self.questions

    def next_question(self):
        if len(self.questions) > self.current_index + 2:  # TODO this is maybe wrong
            self.current_index += 1
            self.set_question_properties(self.questions[self.current_index])
        else:
            self.parent.parent.sm.transition = SlideTransition()
            self.parent.parent.sm.current = "player_screen"  # TODO placeholder
            return False

    def set_question_properties(self, question):
        self.left_picture_url = config.filename_to_url(question['left_picture_url'])
        self.right_picture_url = config.filename_to_url(question['right_picture_url'])
        self.text = question['text']
        self.hint = question['hint']
        self.question_id = question['id']  # For analytics

    def left_pressed(self):
        print "Left button pressed"

    def right_pressed(self):
        print "Right button pressed"

    def show_hint(self):
        popup = Popup(
            title='Hint',
            content=Label(text=self.hint),
            separator_color=config.colors['brand'],
            size_hint=(None, None),
            size=(400, 400)
        )
        popup.open()


class MainLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)


class CoopGameScreen(Screen):
    background_color = config.colors['player2_bg']
    player_boxes = []
    entered = False  # Screen previously entered flag

    def __init__(self, sm, **kwargs):
        super(CoopGameScreen, self).__init__(**kwargs)
        self.sm = sm
        self.main_layout = MainLayout()  # This layout will contain everything
        self.question_grid = QuestionGrid()
        self.countdown_progressbar = TimeProgressBar()
        self.players_grid = PlayersGridLayout()  # This holds the two players layouts at the bottom
        self.player_layouts = []

    def on_enter(self, *args):
        if self.entered:
            return
        self.entered = True

        for player in persistence.current_players:
            self.player_layouts.append(PlayerLayout(player))

        self.draw_screen()
        self.play()

    def draw_screen(self):
        self.main_layout.add_widget(self.question_grid)
        self.main_layout.add_widget(self.countdown_progressbar)

        self.players_grid.add_widget(self.player_layouts[0])  # Player 1
        self.players_grid.add_widget(self.player_layouts[1])  # Player 2

        self.main_layout.add_widget(self.players_grid)

        self.add_widget(self.main_layout)

    def play(self):
        self.countdown_progressbar.countdown()

    def score(self):
        self.sm.transition = SlideTransition()
        self.sm.current = "score_screen"

    def time_out(self):
        """Question wasn't answered in time, no one gets points TODO different for versus"""
        print "Time out!"
        for player in persistence.current_players:
            player.questions_answered.append({"player": player,
                                 "question_id": self.question_grid.question_id,
                                 "is_correct": True})

        self.score()

    def use_powerup(self, player_powerup):
        """Powerup logic is defined below, feel free to add a powerup in the backend and define proper method

        Keyword argument:
        player_powerup -- the powerup object with an id reference that can be used to update the server
        """
        if player_powerup.name == 'Ice age':
            # Pause timer for half of question_time_seconds (e.g. 30 seconds / 2 = 15 seconds)
            self.countdown_progressbar.pause(config.question_time_seconds / 2)
        elif player_powerup.name == 'Hint':
            # Popup a question_hint
            self.question_grid.show_hint()
        elif player_powerup.name == 'Double XP':
            pass  # TODO when allocate_points is implemented
        else:
            print "Powerup not recognized!"
            return  # Error

        print "Used " + str(player_powerup.name)
        player_powerup.quantity -= 1


class CoopGameScreenApp(App):
    def build(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    CoopGameScreenApp().run()
