from jsonconfig import JSONConfig
from ranking import *
import random


class pokerAI(object):
    def __init__(self):
        self.full_deck = {create_card(i, j) for i in range(2, 15) for j in 'hsdc'}

    def get_winning_odds(self, cards, table_info):
        pass

    def get_strategy(self, cards, table_info):
        pass


if __name__ == '__main__':
    ai = pokerAI()
    print(ai.full_deck, len(ai.full_deck))