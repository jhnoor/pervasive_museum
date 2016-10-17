#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition

import config, persistence
# For the app
from kivy.app import App
from kivy.uix.button import ButtonBehavior, Button
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


class ImageButton(ButtonBehavior, AsyncImage):
    pass


class PlayerXpProgressBar(ProgressBar):
    progress = NumericProperty()

    def __init__(self, player, **kwargs):
        super(PlayerXpProgressBar, self).__init__(**kwargs)
        self.progress = player.get_level_progress()


class PlayerLayout(GridLayout):
    def __init__(self, player, **kwargs):
        super(PlayerLayout, self).__init__(**kwargs)
        # Set initial data
        self.player = player
        self.level = Label(id="level_id", text="lvl " + str(player.get_level()))
        self.xp_progress_bar = PlayerXpProgressBar(player)
        self.powerups_grid = PowerupsGridLayout(len(player.powerups))

        for powerup in player.powerups:
            self.powerups_grid.add_widget(PowerupLayout(powerup))  # Add powerup to grid

        self.add_widget(self.powerups_grid)
        self.add_widget(self.level)
        self.add_widget(self.xp_progress_bar)

    def update(self):
        self.level.text = "lvl " + str(self.player.level)
        self.xp_progress_bar.value = self.player.get_level_progress()



class PlayersGridLayout(GridLayout):
    background_color = config.colors['dark_grey']

    def __init__(self, **kwargs):
        super(PlayersGridLayout, self).__init__(**kwargs)

    def reset(self): # TODO should this guy add widgets himself?
        self.clear_widgets()


class TimeProgressBar(ProgressBar):
    max = NumericProperty(config.question_time_seconds * 100)
    value = NumericProperty(config.question_time_seconds * 100)

    def __init__(self, **kwargs):
        super(TimeProgressBar, self).__init__(**kwargs)
        self.event = None

    def countdown(self, dt=None):
        refresh_time = 1 / 30  # in seconds
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

    def reset(self):
        self.event.cancel()
        self.value = config.question_time_seconds * 30


# Three column grid that that has left_picture, question_text and right_picture
class QuestionGrid(GridLayout):
    background_color = config.colors['player1_bg']
    left_picture_url = StringProperty("")
    right_picture_url = StringProperty("")
    text = StringProperty("")
    hint = StringProperty("")
    is_left_correct = None
    question_id = None

    def __init__(self, **kwargs):
        super(QuestionGrid, self).__init__(**kwargs)
        self.current_index = 0
        self.questions = config.current_terminal.questions
        self.set_question_properties(self.questions[0])
        print self.questions

    def next_question(self):
        if len(self.questions) > self.current_index + 2:  # TODO this is maybe wrong
            self.current_index += 1
            self.set_question_properties(self.questions[self.current_index])
            return True
        else:
            return False

    def set_question_properties(self, question):
        self.left_picture_url = config.filename_to_url(question['left_picture_url'])
        self.right_picture_url = config.filename_to_url(question['right_picture_url'])
        self.text = question['text']
        self.hint = question['hint']
        self.question_id = question['id']  # For analytics
        self.is_left_correct = question['is_left_correct']

    def left_pressed(self):
        self.parent.parent.choice_buttons_grid.left_choice()

    def right_pressed(self):
        self.parent.parent.choice_buttons_grid.right_choice()

    def show_hint(self):
        popup = Popup(
            title='Hint',
            content=Label(text=self.hint),
            separator_color=config.colors['brand'],
            size_hint=(None, None),
            size=(400, 400)
        )
        popup.open()

    def reset(self):
        self.current_index = 0
        self.questions = config.current_terminal.questions
        self.set_question_properties(self.questions[0])


class ChoiceButtonsGrid(GridLayout):
    left_color = config.colors['left_choice_button']
    right_color = config.colors['right_choice_button']

    def __init__(self, **kwargs):
        super(ChoiceButtonsGrid, self).__init__(**kwargs)
        self.players = kwargs['players']
        self.size_hint = (0.3, 0.15)
        self.pos_hint = {'y': 0.3, 'center_x': 0.5}
        self.add_widget(Button(text="<< Venstre", on_press=self.left_choice, font_size="14sp",
                               background_color=config.colors['left_choice_button']))
        self.add_widget(Button(text="Høyre >>", on_press=self.right_choice, font_size="14sp",
                               background_color=config.colors['right_choice_button']))

    def left_choice(self, button=None):
        print "Left choice"
        self.parent.parent.answer_submitted(self.players, left=True)

    def right_choice(self, button=None):
        print "Right choice"
        self.parent.parent.answer_submitted(self.players, left=False)

    def reset(self):
        pass


class MainLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)

    def reset(self):
        for widget in self.children:
            widget.reset()


class CoopGameScreen(Screen):
    background_color = config.colors['player2_bg']

    def __init__(self, sm, **kwargs):
        super(CoopGameScreen, self).__init__(**kwargs)
        self.sm = sm
        self.player_boxes = []
        self.main_layout = MainLayout()  # This layout will contain everything
        self.question_grid = QuestionGrid()
        self.countdown_progressbar = TimeProgressBar()
        self.choice_buttons_grid = ChoiceButtonsGrid(players=persistence.current_players)
        self.players_grid = PlayersGridLayout()  # This holds the two players layouts at the bottom
        self.number_of_players_answered_current_question = 0
        self.draw_screen()

    def on_enter(self, *args):
        self.play()

    def draw_screen(self):
        self.main_layout.add_widget(self.question_grid)
        self.main_layout.add_widget(self.countdown_progressbar)

        # Add this widget for each player in versus, in coop just one choice_buttons_grid is enough
        self.main_layout.add_widget(self.choice_buttons_grid)

        self.main_layout.add_widget(self.players_grid)

        self.add_widget(self.main_layout)

    def play(self):
        for player in persistence.current_players:
            self.player_boxes.append(PlayerLayout(player))

        for player_box in self.player_boxes:
            self.players_grid.add_widget(player_box)

        self.countdown_progressbar.countdown()

    def score(self):
        if self.question_grid.next_question():  # There is a next question
            self.sm.transition = SlideTransition()
        else:  # Final score
            self.sm.transition = SlideTransition(direction="up")
            self.sm.get_screen("score_screen").final = True

        self.sm.current = "score_screen"

    def answer_submitted(self, players, left):
        """One of the players has answered"""
        print "answer submitted"
        self.countdown_progressbar.event.cancel()

        for player in players:
            player.questions_answered.append({"player": player,
                                              "question_id": self.question_grid.question_id,
                                              "is_correct": (not (left) or self.question_grid.is_left_correct)})

        if all(players_answered < config.MAX_PLAYERS
               for players_answered in [len(players), self.number_of_players_answered_current_question]):
            print "Not all players answered current question"
            self.number_of_players_answered_current_question += 1
        else:
            self.number_of_players_answered_current_question = 0
            self.score()

    def time_out(self):
        """Question wasn't answered in time, no one gets points TODO different for versus"""
        print "Time out!"
        for player in persistence.current_players:
            player.questions_answered.append({"player": player,
                                              "question_id": self.question_grid.question_id,
                                              "is_correct": False})

        self.score()

    def update_players(self):
        for player_box in self.player_boxes:
            player_box.update()

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

    def reset(self):
        print "Resetting coopgamescreen"
        del self.player_boxes[:]
        for widget in self.children:
            widget.reset()
        """
        self.main_layout = MainLayout()  # This layout will contain everything
        self.question_grid = QuestionGrid()
        self.countdown_progressbar = TimeProgressBar()
        self.choice_buttons_grid = ChoiceButtonsGrid(players=persistence.current_players)
        self.players_grid = PlayersGridLayout()  # This holds the two players layouts at the bottom
        self.number_of_players_answered_current_question = 0
        """


class CoopGameScreenApp(App):
    def build(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    CoopGameScreenApp().run()
