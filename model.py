import config
from pprint import pprint


class Terminal():
    questions = []

    def __init__(self, terminal):
        self.id = terminal['id']
        self.questions = terminal['questions']
        self.name = terminal['name']

    def __str__(self):
        return str(pprint(vars(self)))


class Player(dict):

    def __init__(self, player, badge_uid):
        super(Player, self).__init__()
        self.__dict__ = self
        self.name = player['name']
        self.id = player['id']
        self.icon_url = config.filename_to_url(player['icon_filename'])
        self.badge_uid = badge_uid
        self.xp = player['xp']
        self.level = player['level']
        self.url = player['url']
        self.trophies = player['trophies']
        self.powerups = player['powerups']
        self.questions_answered = []
        self.active_powerups = []


    def update(self, player_box):
        self.name = player_box.name
        # TODO fill in rest

    def __str__(self):
        return str(pprint(vars(self)))

    def get_level_progress(self):
        """Gets level progress in percentage for this player"""
        return config.check_progress_level_up(self.level, self.xp)['progress']

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
