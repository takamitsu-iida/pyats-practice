#!/usr/bin/env python

#
# ファイルに保存された'routing'をロードして表示します
#

import argparse
import os
import pickle

from pprint import pprint

# import Genie
from genie.testbed import load

# list of router name
routers = ['r1', 'r2', 'r3', 'r4']

def here(path=''):
  return os.path.abspath(os.path.join(os.path.dirname(__file__), path))

# pickle directory
pkl_dir = os.path.join(here('.'), 'pkl')

def get_file_path(hostname, status):
    return os.path.join(pkl_dir, f'routing_{hostname}_r1gig1_{status}.pickle')

def load(path):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            loaded = pickle.load(f)
        return loaded
    return None

def show():
    for router in routers:
        before_file_path = get_file_path(router, 'before')
        gig1down_file_path = get_file_path(router, 'down')
        gig1up_file_path = get_file_path(router, 'up')

        learnt_before = load(os.path.join(pkl_dir, before_file_path))
        learnt_down = load(os.path.join(pkl_dir, gig1down_file_path))
        learnt_up = load(os.path.join(pkl_dir, gig1up_file_path))

        print('='*10)
        print(before_file_path)
        print('='*10)
        pprint(learnt_before.info)

        print('='*10)
        print(gig1down_file_path)
        print('='*10)
        pprint(learnt_down.info)

        print('='*10)
        print(gig1up_file_path)
        print('='*10)
        pprint(learnt_up.info)


def diff():

    # routingではこれらを差分計算の対象から除外
    exclude = ['updated']

    for router in routers:
        before_file_path = get_file_path(router, 'before')
        gig1down_file_path = get_file_path(router, 'down')
        gig1up_file_path = get_file_path(router, 'up')

        learnt_before = load(os.path.join(pkl_dir, before_file_path))
        learnt_down = load(os.path.join(pkl_dir, gig1down_file_path))
        learnt_up = load(os.path.join(pkl_dir, gig1up_file_path))

        diff = learnt_down.diff(learnt_before, exclude=exclude)
        diff.findDiff
        print('\n' + '='*10)
        print(f'{router} diff from before to down')
        print('='*10)
        print(diff)

        diff = learnt_up.diff(learnt_down, exclude=exclude)
        diff.findDiff
        print('\n' + '='*10)
        print(f'{router} diff from down to up')
        print('='*10)
        print('\n')
        print(diff)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        'oper',
        help='show or diff',
        type=str,
        choices=['show', 'diff']
    )

    args, _ = parser.parse_known_args()

    if args.oper == 'show':
        show()
    elif args.oper == 'diff':
        diff()