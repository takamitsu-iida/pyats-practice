#!/usr/bin/env python


from datetime import datetime
from pprint import pprint, pformat

#
# args
#
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--testbed', dest='testbed', help='testbed YAML file', type=str, default='../lab.yml')
args, _ = parser.parse_known_args()

#
# tinydb
#
from tinydb import TinyDB, Query, where

MAX_HISTORY = 2

DB_PATH = 'log/db.json'

def db_test1():
    with TinyDB(DB_PATH) as db:
        db.insert_multiple([
        {
            'date': datetime( year=2022, month=1, day=5  ).timestamp()
        },
        {
            'date': datetime( year=2022, month=1, day=15 ).timestamp()
        }
        ])

        q = Query()

        print(db.search(
        (q.date < datetime( year=2022, month=1, day=10 ).timestamp())
        &
        (q.date > datetime( year=2022, month=1, day=4  ).timestamp())
        ))

        timestamps = [obj['date'] for obj in db]
        print(timestamps)

        ids = [obj.doc_id for obj in db]
        print(ids)


def insert_intf_info(info):
    # 格納するドキュメントの形式
    # {
    #    'timestamp': xxx,
    #    'info': 学習した情報
    # }
    d = {}

    # 現在時刻のタイムスタンプを付与
    d['timestamp'] = datetime.now().timestamp()
    d['info'] = info

    # dbに格納
    with TinyDB(DB_PATH) as db:
        db.insert(d)


def get_stored_dates():
    with TinyDB(DB_PATH) as db:
        # timestampキーの一覧を取り出す
        timestamps = [d['timestamp'] for d in db if 'timestamp' in d ]

        # datetimeオブジェクトに変換
        datetimes = [datetime.fromtimestamp(ts) for ts in timestamps]

        # 分かりやすく日付の文字列に変換
        dates = [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in datetimes]

        return dates


def delete_old():
    with TinyDB(DB_PATH) as db:
        # timestampキーの一覧を取り出す
        timestamps = [d['timestamp'] for d in db if 'timestamp' in d ]

        # 新しい順（降順）にソート
        timestamps.sort(reverse=True)

        # MAX_HISTORYを超えたものは削除
        if len(timestamps) > MAX_HISTORY:
            should_be_deleted = timestamps[MAX_HISTORY:]
            for ts in should_be_deleted:
                db.remove(where('timestamp') == ts)

#
# pyATS
#
from genie.testbed import load
from genie.ops.utils import get_ops

testbed = load(args.testbed)

uut = testbed.devices['uut']

# connect
uut.connect(via='console')

# learn all interfaces
Interface = get_ops('interface', uut)
intf = Interface(device=uut)
intf.learn()

# disconnect
if uut.is_connected():
    uut.disconnect()

# 学習した結果の辞書型はinfoキーで入手可能
# pprint(intf.info)
#
# {'GigabitEthernet1': {},
#  'GigabitEthernet2': {},
#  'GigabitEthernet3': {},

# infoをdbに格納
insert_intf_info(intf.info)

# 古いのは削除する
delete_old()

# タイムスタンプの一覧を日付に変換して取得
dates = get_stored_dates()
print('stored')
print(dates)
