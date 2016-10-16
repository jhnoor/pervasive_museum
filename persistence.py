import config
from model import Player, Terminal

current_terminal = Terminal
current_players = []

def update_player(**kwargs):
    """Updates player, kwargs holds any attributes that need to be updated"""
    print kwargs
    for player in current_players:
        if player.name == kwargs['name']:
            for key, value in kwargs.iteritems():
                setattr(player, key, value)

            return

def remove_player(player_box):
    for player in current_players:
        if player.name == player_box.name:
            current_players.remove(player)
            return True
    return False