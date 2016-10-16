import config
from model import Player, Terminal

current_terminal = Terminal
current_players = []

def update_player(**kwargs):
    print "what are args!?"
    print kwargs
    for player in current_players:
        if player.name == kwargs['name']:
            player.xp = kwargs['xp']
            player.level = kwargs['level']
            return

def remove_player(player_box):
    for player in current_players:
        if player.name == player_box.name:
            current_players.remove(player)
            return True
    return False