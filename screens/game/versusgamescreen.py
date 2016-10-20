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

ALLOWED_POWERUPS = ['Frys klokka!', 'Dobbel XP']

class VersusGameScreen(Screen):
    background_color = config.colors['player1_bg']

    def __init__(self, sm, **kwargs):
        super(VersusGameScreen, self).__init__(**kwargs)

class VersusGameScreenApp(App):
    def build(self):
        pass

    def on_pause(self):
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    VersusGameScreenApp().run()
