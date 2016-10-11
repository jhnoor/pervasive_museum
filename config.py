import os

import requests

CURRENT_PATH = os.path.dirname(__file__)


def KV_PATH(kv_file):
    return os.path.join(CURRENT_PATH, kv_file)


port = "COM3"

api = dict(
    base_url="http://127.0.0.1:8000/",
    end_url=""
)

colors = dict(
    brand=[0.18, 0.77, 0.71, 1],
    contrast_brand=[0.015, 0.050, 0.078, 1],
    red=[0.93, 0.04, 0.26, 1],
    green=[0.48, 0.91, 0.78, 1],
    blue=[0.72, 0.88, 1.00, 1],
    grey=[0.87, 0.91, 0.95, 1],
)

DEFAULT_ADD_XP = 200

STATIC = 'static/'
BADGES = 'badges/'
PLAYERS = 'players/'
TROPHIES = 'trophies/'
POWERUPS = 'powerups/'


def get_level_progress_percentage(level, xp):
    return 30 #TODO calculate based on xp and level

def request(request_method, request_verb, **kwargs):
    url = api['base_url'] + request_method + api['end_url']
    print "config request: "+str(url)+", verb: "+request_verb

    if request_verb == 'GET':
        return requests.get(url)
    elif request_verb == 'PUT':
        return requests.put(url, data = kwargs['data'])
    elif request_verb == 'POST':
        return requests.post(url, data = kwargs['data'])
    elif request_verb == 'DELETE':
        return requests.delete(url)


def filename_to_url(icon_filename):
    return api['base_url']+STATIC+str(icon_filename)

# GET
def GET_BADGES(badge_pk=''):
    return BADGES + str(badge_pk)


def GET_PLAYERS(player_pk=''):
    return PLAYERS + str(player_pk)


def GET_TROPHIES(trophy_pk=''):
    return TROPHIES + str(trophy_pk)


def GET_POWERUPS(powerup_pk=''):
    return POWERUPS + str(powerup_pk)


# PUT
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
