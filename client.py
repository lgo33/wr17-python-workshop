import requests
from argparse import ArgumentParser
import sys
from pprint import pprint
import time
from ranking import *

UUID = 'e616926e-fdba-47dc-9655-61c5a9c02626'
base_url = 'http://pokerserver.retreat.tngtech.com:5555'
myself = 'FetteElke'



def register_user(username):
    req = requests.post(base_url + "/uuid", json={'player_name': username})
    print(f'player {username} registered with uuid {req.content}')


def get_tables(tablename=None, do_print=False):
    req = requests.get(base_url + "/tables")
    tables = req.json()['tables']
    if (do_print):
        for t in tables:
            print('tablename: {}, open spots: {}, players: {}'.format(t['name'],
                                                                      t['max_player_count'] - len(t['players']),
                                                                      t['players']))
    else:
        if tablename is None:
            return tables
        else:
            for t in tables:
                if t['name'] == tablename:
                    return t
            return None


def join_table(tablename, position):
    url = base_url + '/table/' + tablename + '/actions/join?uuid=' + UUID
    req = requests.post(url, json={'position': position})
    print(req.text)


def table_action(tablename, action, data=None):
    url = base_url + '/table/' + tablename + '/actions/' + action + '?uuid=' + UUID
    req = requests.post(url, json=data)
    print(req.text)
    return req.status_code


def get_table_status(tablename, do_print=False):
    url = base_url + '/table/' + tablename
    req = requests.get(url)
    if do_print:
        pprint(req.json())
    if req.status_code == 200:
        return req.json()
    else:
        return req.status_code


def fold_loop(tablename):
    while True:
        status = get_table_status(tablename)
        print('table {}, current player {}'.format(tablename, status['current_player']))
        if status['current_player'] == myself:
            table_action(tablename, 'fold')
            print('folded')
        time.sleep(0.5)


def call_loop(tablename):
    while True:
        status = get_table_status(tablename)
        print('table {}, current player {}'.format(tablename, status['current_player']))
        if status['current_player'] == myself:
            response = table_action(tablename, 'call')
            if response != 200:
                table_action(tablename, 'check')
            print('called')
        time.sleep(0.5)



if __name__ == '__main__':
    argparser = ArgumentParser(description='register Poker client')
    argparser.add_argument('-r', '--register_user', type=str, help='register username')
    argparser.add_argument('-u', '--user', type=str, help='username')
    argparser.add_argument('-j', '--join', type=str, help='join <tablename>')
    argparser.add_argument('-s', '--status', type=str, help='status <tablename>')
    argparser.add_argument('-p', '--playername', type=str, help='playername <name>')
    argparser.add_argument('-f', '--fold', type=str, help='fold <tablename>')
    argparser.add_argument('-c', '--call', type=str, help='call <tablename>')
    argparser.add_argument('-t', '--get_tables', action='store_true')
    args = argparser.parse_args()

    if args.register_user:
        register_user(args.register_user)

    if args.user:
        UUID=args.user

    if args.playername:
        myself=args.playername

    if args.get_tables:
        get_tables(do_print=True)

    if args.join:
        table = get_tables(args.join)
        if table is None:
            print('table {} unknown'.format(args.join))
            sys.exit()

        if len(table['players']) == table['max_player_count']:
            print('table {} full'.format(args.join))
            sys.exit()

        for i in range(1, table['max_player_count'] + 1):
            if str(i) not in table['players']:
                join_table(args.join, i)
                break

    if args.status:
        get_table_status(args.status, do_print=True)

    if args.fold:
        fold_loop(args.fold)

    if args.call:
        call_loop(args.call)
