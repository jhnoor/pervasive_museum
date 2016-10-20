#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, config, persistence
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, SlideTransition
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
from common.commonclasses import PowerupLayout, PowerupsGridLayout

# Builder.load_file(os.path.join(os.path.dirname(__file__), 'gamescreen.kv'))

ALLOWED_POWERUPS = ['Frys klokka!', 'Dobbel XP', 'Hint']



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
        self.rows = 3
        self.player = player
        self.level = Label(id="level_id", text="lvl " + str(player.get_level()))
        self.xp_progress_bar = PlayerXpProgressBar(player)
        self.powerups_grid = PowerupsGridLayout(cols=len(player.powerups))

        for powerup in player.powerups:
            if (powerup['name'] in ALLOWED_POWERUPS):
                self.powerups_grid.add_widget(PowerupLayout(powerup, pressable=True))  # Add powerup to grid
            else:
                print "Ignoring " + powerup['name'] + " as its not allowed in this game mode"

        self.add_widget(self.powerups_grid)
        self.add_widget(self.level)
        self.add_widget(self.xp_progress_bar)

    def update(self):
        self.level.text = "lvl " + str(self.player.level)
        self.xp_progress_bar.value = self.player.get_level_progress()
        self.powerups_grid.update_powerups(self.player)


    def use_powerup(self, player_powerup):
        """Powerup logic is defined below, feel free to add a powerup in the backend and define proper method

        Keyword argument:
        player_powerup -- the powerup object with an id reference that can be used to update the server
        """
        if player_powerup.name == 'Frys klokka!':
            # Pause timer for half of question_time_seconds (e.g. 30 seconds / 2 = 15 seconds)
            config.current_gamescreen.countdown_progressbar.pause(config.DEFAULT_QUESTION_TIME / 2)
        elif player_powerup.name == 'Hint':
            # Popup a question_hint
            config.current_gamescreen.question_grid.show_hint()
        elif player_powerup.name == 'Dobbel XP':
            self.player.active_powerups.append('Dobbel XP')
        else:
            print "Powerup not recognized!"
            return  # Error

        print "Used " + str(player_powerup.name)
        for powerup in self.player.powerups:
            if powerup['name'] == player_powerup.name:
                powerup['quantity'] -= 1
        player_powerup.quantity -= 1


class PlayersGridLayout(GridLayout):
    background_color = config.colors['dark_grey']

    def __init__(self, **kwargs):
        super(PlayersGridLayout, self).__init__(**kwargs)
        self.size_hint = (1, 0.2)

    def reset(self):
        self.clear_widgets()


class TimeProgressBar(ProgressBar):
    max = NumericProperty(config.DEFAULT_QUESTION_TIME * 100)
    value = NumericProperty(config.DEFAULT_QUESTION_TIME * 100)

    def __init__(self, **kwargs):
        super(TimeProgressBar, self).__init__(**kwargs)
        self.event = None

    def countdown(self, dt=None, **kwargs):
        if kwargs.get('reset', False):
            self.value = config.DEFAULT_QUESTION_TIME * 100
        refresh_time = 1 / config.REFRESH_RATE  # in seconds
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
        self.value = config.DEFAULT_QUESTION_TIME * 100


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
        for player in persistence.current_players:
            print "player questions_answered"
            print player.questions_answered
        print self.questions

    def next_question(self):
        if len(self.questions) > self.current_index + 2:
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
        self.size_hint = (0.3, 0.15)
        self.pos_hint = {'y': 0.3, 'center_x': 0.5}
        self.add_widget(Button(text="<< Venstre", on_press=self.left_choice, font_size="20sp",
                               background_color=config.colors['left_choice_button']))
        self.add_widget(Button(text="Høyre >>", on_press=self.right_choice, font_size="20sp",
                               background_color=config.colors['right_choice_button']))

    def left_choice(self, button=None):
        print "Left choice"
        config.current_gamescreen.answer_submitted(left=True)

    def right_choice(self, button=None):
        print "Right choice"
        config.current_gamescreen.answer_submitted(left=False)

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
        config.current_gamescreen = self
        self.player_boxes = []
        self.main_layout = MainLayout()  # This layout will contain everything
        self.question_grid = QuestionGrid()
        self.countdown_progressbar = TimeProgressBar()
        self.choice_buttons_grid = None
        self.players_grid = None  # This holds the two players layouts at the bottom
        self.draw_screen()

    def on_enter(self, *args):
        for player_box in self.player_boxes:
            player_box.update()
        self.countdown_progressbar.countdown(reset=True)

    def draw_screen(self):
        self.main_layout.add_widget(self.question_grid)
        self.main_layout.add_widget(self.countdown_progressbar)

        self.choice_buttons_grid = ChoiceButtonsGrid()
        self.main_layout.add_widget(self.choice_buttons_grid)

        self.players_grid = PlayersGridLayout()

        for player in persistence.current_players:
            self.player_boxes.append(PlayerLayout(player))

        for player_box in self.player_boxes:
            self.players_grid.add_widget(player_box)

        self.main_layout.add_widget(self.players_grid)
        self.add_widget(self.main_layout)

    def score(self):
        if self.question_grid.next_question():  # There is a next question
            self.sm.transition = SlideTransition()
        else:  # Final score
            self.sm.transition = SlideTransition(direction="up")
            self.sm.get_screen("score_screen").final = True

        self.sm.current = "score_screen"

    def answer_submitted(self, left):
        print "answer_submitted!"
        for player in persistence.current_players:
            player.questions_answered.append({
                "player_ids": [player.id],
                "question_id": self.question_grid.question_id,
                "is_correct": left == self.question_grid.is_left_correct,
                "elapsed_time": self.countdown_progressbar.value / 100
            })

        print "elapsed time: "+str(self.countdown_progressbar.value / 100)

        self.countdown_progressbar.event.cancel()
        self.score()

    def time_out(self):
        """Question wasn't answered in time, no one gets points TODO different for versus"""
        print "Time out!"
        for player in persistence.current_players:
            player.questions_answered.append({
                "player": player,
                "question_id": self.question_grid.question_id,
                "is_correct": False,
                "elapsed_time": config.DEFAULT_QUESTION_TIME
            })

        self.score()


    def reset(self):
        # TODO don't need as entire screen is deleted
        print "Resetting gamescreen"
        del self.player_boxes[:]
        for widget in self.children:
            widget.reset()


class CoopGameScreenApp(App):
    def build(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    CoopGameScreenApp().run()
