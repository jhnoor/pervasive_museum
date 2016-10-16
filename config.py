import requests, serial, math

from model import Terminal

port = "COM3"
main = None
# Arduino hook
try:
    arduino = serial.Serial(port, 9600, timeout=0)
except:
    print "Arduino busy or not plugged in. Use port: " + port + " or change in config"
    exit()

api = dict(
    base_url="http://127.0.0.1:8000/",
    end_url=""
)

question_time_seconds = 400
score_screen_time_seconds = 3
xp_progressbar_height = 12

colors = dict(
    brand=[0.18, 0.77, 0.71, 1],
    player1_bg=[0.301, 0.239, 0.239, 1],
    player2_bg=[0.160, 0.211, 0.356, 1],
    left_choice_button=[0.72, 0.88, 1.00, 1],
    right_choice_button=[1, 0.6, 0, 1],
    red=[0.93, 0.04, 0.26, 1],
    green=[0.321, 1, 0.721, 1],
    blue=[0.537, 0.721, 0.941, 1],
    grey=[0.87, 0.91, 0.95, 1],
    light_grey=[0.6, 0.6, 0.6, 1],
    dark_grey=[0.2, 0.2, 0.2, 1],
    black=[0, 0, 0, 1],
    white=[1, 1, 1, 1]
)

MAX_PLAYERS = 2
DEFAULT_ADD_XP = 200

STATIC = 'static/'
BADGES = 'badges/'
PLAYERS = 'players/'
TROPHIES = 'trophies/'
POWERUPS = 'powerups/'
TERMINALS = 'terminals/'

current_terminal = Terminal


def check_progress_level_up(current_level, xp):
    next_level = (math.sqrt(625 + 100 * xp) - 25) / 50
    delta = float(next_level) - float(current_level)

    return {"progress": delta * 100, "level_up": delta * 100 >= 100}


def request(request_method, request_verb, **kwargs):
    url = api['base_url'] + request_method + api['end_url']
    print request_verb + ": " + str(url) + ", verb: " + request_verb

    if request_verb == 'GET':
        return requests.get(url)
    elif request_verb == 'PUT':
        return requests.put(url, data=kwargs['data'])
    elif request_verb == 'POST':
        return requests.post(url, data=kwargs['data'])
    elif request_verb == 'DELETE':
        return requests.delete(url)
    else:
        raise NotImplementedError("Verb " + request_verb + " unrecognized")


def filename_to_url(icon_filename):
    return api['base_url'] + STATIC + str(icon_filename)


# GET
def GET_BADGES(badge_pk=''):
    return BADGES + str(badge_pk)


def GET_PLAYERS(player_pk=''):
    return PLAYERS + str(player_pk)


def GET_TROPHIES(trophy_pk=''):
    return TROPHIES + str(trophy_pk)


def GET_POWERUPS(powerup_pk=''):
    return POWERUPS + str(powerup_pk)


def GET_TERMINALS(terminal_pk=''):
    return TERMINALS + str(terminal_pk)


# PUT
def PUT_SET_ONLINE(terminal_pk):
    return TERMINALS + str(terminal_pk) + '/set_online/'


def PUT_SET_OFFLINE(terminal_pk):
    return TERMINALS + str(terminal_pk) + '/set_offline/'


def PUT_SET_XP(player_pk, xp):
    return PLAYERS + str(player_pk) + '/set_xp/' + str(xp)


def PUT_SET_POWERUP_QUANTITY(player_pk, quantity):
    return PLAYERS + str(player_pk) + '/set_powerup_quantity/' + str(quantity)


def PUT_EARN_TROPHY(player_pk, trophy_pk):
    return PLAYERS + str(player_pk) + '/earn_trophy/' + str(trophy_pk)


def PUT_ADD_XP(player_pk, xp=DEFAULT_ADD_XP):
    return PLAYERS + str(player_pk) + '/add_xp/' + str(xp)


def PUT_PLAYER_FINISHED(badge_pk):
    return BADGES + str(badge_pk) + '/player_finished'


# POST
def POST_NEW_PLAYER(badge_pk):
    return BADGES + str(badge_pk) + '/new_active_player/'


def POST_NEW_BADGE():
    return BADGES


headers = {'Content-type': 'application/json',
           'Accept': 'application/json; charset=UTWF-8'}
