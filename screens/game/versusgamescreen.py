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
        self.choice_buttons_grid = None
        self.time_progress_bar = None

        for powerup in player.powerups:
            if (powerup['name'] in config.current_gamescreen.ALLOWED_POWERUPS):
                self.powerups_grid.add_widget(PowerupLayout(powerup, pressable=True))  # Add powerup to grid
                print "adding powerup: " + powerup['name']
            else:
                print "Ignoring " + powerup['name'] + " as its not allowed in this game mode"

        self.add_widget(self.powerups_grid)
        self.add_widget(self.level)
        self.add_widget(self.xp_progress_bar)

    def update(self):
        self.level.text = "lvl " + str(self.player.level)
        self.xp_progress_bar.value = self.player.get_level_progress()
        self.powerups_grid.update_powerups(self.player)
        self.choice_buttons_grid.enable_buttons()

    def time_out(self):
        """time_progress_bar has hit zero! Penalize user"""
        self.choice_buttons_grid.disable_buttons()
        config.current_gamescreen.answer_submitted(left="time_out", player_box=self)

    def use_powerup(self, player_powerup):
        """Powerup logic is defined below, feel free to add a powerup in the backend and define proper method

        Keyword argument:
        player_powerup -- the powerup object with an id reference that can be used to update the server
        """
        if player_powerup.name == 'Freeze time!':
            # Pause timer for half of question_time_seconds (e.g. 30 seconds / 2 = 15 seconds)
            self.time_progress_bar.pause(config.DEFAULT_QUESTION_TIME / 2)
        elif player_powerup.name == 'Hint':
            # Popup a question_hint
            config.current_gamescreen.question_grid.show_hint()
        elif player_powerup.name == 'Double XP':
            self.player.active_powerups.append('Double XP')
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
        self.countdown_event = None
        self.player_box = kwargs['player_box']

    def countdown(self, dt=None, **kwargs):
        if kwargs.get('reset', False):
            self.value = config.DEFAULT_QUESTION_TIME * 100
        refresh_time = 1 / config.REFRESH_RATE  # in seconds
        if self.countdown_event:
            self.countdown_event.cancel()
        self.countdown_event = Clock.schedule_interval(self.decrement_clock, refresh_time)

    def decrement_clock(self, dt):
        if self.value > 1:
            self.value -= 1
        else:
            self.countdown_event.cancel()
            self.player_box.time_out()

    def pause(self, seconds_to_pause):
        self.countdown_event.cancel()
        self.pause_event = Clock.schedule_once(self.countdown, seconds_to_pause)

    def reset(self):
        if self.countdown_event:
            self.countdown_event.cancel()
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
        """Images can't be clicked in versus"""
        pass

    def right_pressed(self):
        """Images can't be clicked in versus"""
        pass

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
        self.player_box = kwargs['player_box']
        self.add_widget(Button(text="<< Venstre", on_press=self.left_choice, font_size="20sp",
                               background_color=config.colors['left_choice_button']))
        self.add_widget(Button(text="Høyre >>", on_press=self.right_choice, font_size="20sp",
                               background_color=config.colors['right_choice_button']))

    def left_choice(self, button=None):
        print "Left choice"
        config.current_gamescreen.answer_submitted(left=True, player_box=self.player_box)
        self.disable_buttons()
        self.player_box.time_progress_bar.reset()

    def right_choice(self, button=None):
        print "Right choice"
        config.current_gamescreen.answer_submitted(left=False, player_box=self.player_box)
        self.disable_buttons()
        self.player_box.time_progress_bar.reset()

    def disable_buttons(self):
        for button in self.children:
            button.disabled = True

    def enable_buttons(self):
        for button in self.children:
            button.disabled = False

    def reset(self):
        pass


class MainLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(MainLayout, self).__init__(**kwargs)

    def reset(self):
        for widget in self.children:
            widget.reset()


class VersusGameScreen(Screen):
    ALLOWED_POWERUPS = ['Freeze time!', 'Double XP']
    background_color = config.colors['versus_bg']

    def __init__(self, sm, **kwargs):
        super(VersusGameScreen, self).__init__(**kwargs)
        self.sm = sm
        config.current_gamescreen = self
        self.player_boxes = []
        self.main_layout = MainLayout()  # This layout will contain everything
        self.question_grid = QuestionGrid()
        self.players_grid = None  # This holds the two players layouts at the bottom
        self.draw_screen()

    def on_enter(self, *args):
        for player_box in self.player_boxes:
            player_box.update()
            player_box.time_progress_bar.countdown(reset=True)

    def draw_screen(self):
        for player in persistence.current_players:
            self.player_boxes.append(PlayerLayout(player))

        self.main_layout.add_widget(self.question_grid)

        pl_grid = GridLayout(cols=2, size_hint=(0.97, 0.2),
                             pos_hint={'center_y': 0.35, 'center_x': 0.5},
                             spacing=(60, 60))
        for player_box in self.player_boxes:
            """For each player_box, associate a choicegrid and progressbar"""
            player_choice_progress_layout = FloatLayout()
            player_box.time_progress_bar = TimeProgressBar(pos_hint={'center_x': 0.5, 'center_y': 0.9},
                                                           player_box=player_box)
            player_box.choice_buttons_grid = ChoiceButtonsGrid(size_hint=(0.5, 0.5),
                                                               pos_hint={'center_x': 0.5, 'center_y': 0.4},
                                                               player_box=player_box)
            player_choice_progress_layout.add_widget(player_box.time_progress_bar)
            player_choice_progress_layout.add_widget(player_box.choice_buttons_grid)
            pl_grid.add_widget(player_choice_progress_layout)

        self.main_layout.add_widget(pl_grid)

        self.players_grid = PlayersGridLayout()

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

    def answer_submitted(self, left, player_box):
        print "answer_submitted!"
        print "from player"
        print player_box

        if left == 'time_out' and left == self.question_grid.is_left_correct:
            raise RuntimeError("This should never happen lol") # TODO remove

        player_box.player.questions_answered.append({
                "player_ids": [player_box.player.id],
                "question_id": self.question_grid.question_id,
                "is_correct": left == self.question_grid.is_left_correct,
                "elapsed_time": config.DEFAULT_QUESTION_TIME-(player_box.time_progress_bar.value / 100)
            })


        print "elapsed time: " + str(config.DEFAULT_QUESTION_TIME-(player_box.time_progress_bar.value / 100))

        if player_box.time_progress_bar.countdown_event:
            player_box.time_progress_bar.countdown_event.cancel()

        try:
            if all(self.question_grid.question_id == player.questions_answered[-1]['question_id'] for player in persistence.current_players):
                #  If all the players have answered the current question
                self.score()
        except IndexError:
            print "Player questions_answered empty, probably a new player"


    def reset(self):
        pass


class VersusGameScreenApp(App):
    def build(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    VersusGameScreenApp().run()
