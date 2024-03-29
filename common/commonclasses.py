import os, config, persistence, functools
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.bubble import Bubble
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock


class PowerupsGridLayout(GridLayout):
    #rows = NumericProperty()
    #cols = NumericProperty()

    def __init__(self, **kwargs):
        super(PowerupsGridLayout, self).__init__(**kwargs)
        if kwargs.get('cols', False):
            self.cols = kwargs['cols']
        elif kwargs.get('rows', False):
            self.rows = kwargs['rows']
        else:
            raise RuntimeError("PowerupsGridLayout must specify rows or cols!")

    def update_powerups(self, player):
        self.clear_widgets()
        for powerup in player.powerups:
            if (powerup['name'] in config.current_gamescreen.ALLOWED_POWERUPS):
                self.add_widget(PowerupLayout(powerup, pressable=True))

class PowerupLayout(FloatLayout):
    name = StringProperty()
    description = StringProperty()
    quantity = NumericProperty()
    icon_url = StringProperty()
    id = NumericProperty()

    def __init__(self, powerup, **kwargs):
        super(PowerupLayout, self).__init__(**kwargs)

        self.name = powerup['name']
        self.description = powerup['description']
        self.quantity = powerup['quantity']
        self.icon_url = config.filename_to_url(powerup['icon_url'])
        self.id = powerup['id']
        self.bubble = None
        if kwargs.get("pressable", False):
            self.ids.button_id.on_press = self.use_powerup
            self.ids.button_id.disabled = self.quantity <= 0  # Disable button if quantity is zero
        else:
            self.ids.button_id.on_press = self.toogle_bubble

    def use_powerup(self):
        self.disable_button()
        self.parent.parent.use_powerup(self)

    def disable_button(self):
        self.ids.button_id.disabled = True

    def enable_button(self):
        """Enables button - but only if enough quantity"""
        self.ids.button_id.disabled = self.quantity <= 0

    def toogle_bubble(self):
        if self.bubble:
            self.remove_widget(self.bubble)
            self.bubble = None
        else:
            self.bubble = Bubble(orientation='horizontal', size_hint=(1, 1),
                                 pos=(self.x, self.y+self.size[1]))
            self.bubble.add_widget(Label(text=self.description))
            self.add_widget(self.bubble)
