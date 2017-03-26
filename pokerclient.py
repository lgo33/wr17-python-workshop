import requests
from argparse import ArgumentParser
import time
from config import Config
from ranking import *

class Player(object):
    def __init__(self, **kwargs):
        self.UUID = 'e616926e-fdba-47dc-9655-61c5a9c02626'
        self.base_url = 'http://pokerserver.retreat.tngtech.com:5555'
        self.playername = 'FetteElke'
        for k, v in kwargs.items():
            if v is not None:
                self.__dict__[k] = v
                print('setting', k, v)
        self.config = Config(self.configfile)
        for player in self.config.items('players'):
            if player[0] == self.playername:
                self.UUID = player[1]
                print(f'found player {self.playername} with UUID {self.UUID}')
        else:
            print(f'registering player {self.playername}')
            self.register_user()
            print(f'registered player {self.playername} with UUID {self.UUID}')

    def register_user(self):
        self.UUID = requests.post(self.base_url + "/uuid", json={'player_name': self.playername}).text
        self.config.set('players', self.playername, self.UUID)
        self.config.save()

    def get_table_info(self):
        req = requests.get(self.base_url + "/tables")
        tables = req.json()['tables']
        for t in tables:
            if t['name'] == self.tablename:
                return t
        return None

    def join_table(self):
        info = self.get_table_info()
        if self.playername in info['players'].values():
            return
        for i in range(1, info['max_player_count'] + 1):
            if str(i) not in info['players']:
                position = i
                break
        url = self.base_url + '/table/' + self.tablename + '/actions/join?uuid=' + self.UUID
        req = requests.post(url, json={'position': position})
        print(req.text)

    def table_action(self, action, data=None):
        url = self.base_url + '/table/' + self.tablename + '/actions/' + action + '?uuid=' + self.UUID
        req = requests.post(url, json=data)
        print(req.text)
        return req.status_code

    def get_table_status(self):
        url = self.base_url + '/table/' + self.tablename + '?uuid=' + self.UUID
        req = requests.get(url)
        if req.status_code == 200:
            return req.json()
        else:
            return req.status_code

    def play(self):
        while True:
            self.join_table()
            status = self.get_table_status()
            print('table {}, current player {}'.format(self.tablename, status['current_player']))
            if status['current_player'] == self.playername:
                print(status)
                response = self.table_action('call')
                if response != 200:
                    self.table_action('check')
                print('called')
            time.sleep(0.3)


if __name__ == '__main__':
    argparser = ArgumentParser(description='register Poker client')
    argparser.add_argument('-u', '--UUID', type=str, help='username')
    argparser.add_argument('-s', '--status', type=str, help='get current information of a table')
    argparser.add_argument('-p', '--playername', type=str, help='set the player name, if UUID is not found in config, the player will be registered first')
    argparser.add_argument('-t', '--tablename', type=str, help='name of the table to join')
    argparser.add_argument('-b', '--base_url', type=str, help='set the address of the poker server')
    argparser.add_argument('-c', '--configfile', type=str, default='.config')

    params = vars(argparser.parse_args())
    player = Player(**params)
    # player.play()
