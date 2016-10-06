import config
from pprint import pprint
from kivy.event import EventDispatcher
from kivy.properties import StringProperty, NumericProperty, ListProperty
# TODO create trophy and powerup models as well and inhertic eventdispatcher

class Player(EventDispatcher):
    name = StringProperty('')
    icon_url = StringProperty('')
    # TODO fill in rest

    def __init__(self, player, badge_uid):
        self.name = player['name']
        self.icon_url = config.filename_to_url(player['icon_filename'])
        self.badge_uid = badge_uid
        self.xp = player['xp']
        self.level = player['level']
        self.url = player['url']

        self.trophies = player['trophies']
        self.powerups = player['powerups']

    def __str__(self):
        return str(pprint(vars(self)))

    def get_xp(self):
        return self.xp

    def set_xp(self, xp):
        if xp > 0:
            self.xp = xp

    def add_xp(self, xp):
        if xp > 0:
            self.xp += xp

    def get_level(self):
        return self.level

    def set_level(self, level):
        if level > 1:
            self.level = level

    def get_name(self):
        return self.name

    def get_url(self):
        return self.url
