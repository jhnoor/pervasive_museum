import requests

api = dict(
    base_url="http://127.0.0.1:8000/",
    end_url=""
)

DEFAULT_ADD_XP = 200

STATIC = 'static/'
BADGES = 'badges/'
PLAYERS = 'players/'
TROPHIES = 'trophies/'
POWERUPS = 'powerups/'


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
