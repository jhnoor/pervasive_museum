import config
from pprint import pprint

class Terminal():
    def __init__(self, terminal):
        self.id = terminal['id']
        self.questions = terminal['questions']
        self.name = terminal['name']

    def __str__(self):
        return str(pprint(vars(self)))